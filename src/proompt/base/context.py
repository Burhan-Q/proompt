import collections.abc
import inspect
import re
import types
import typing
from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Callable

from pydantic_ai.tools import Tool
from pydantic_ai.toolsets import FunctionToolset

from proompt.base.mixins import RenderStrMixin

_NONE_TYPE = type(None)
_MODULE_PREFIX = re.compile(r"(?<![\"'\w.])(?:[A-Za-z_]\w*\.)+(\w+)")


def _strip_modules(text: str) -> str:
    """Remove dotted module prefixes from a rendered annotation string."""
    return _MODULE_PREFIX.sub(r"\1", text)


def render_annotation(annotation: object) -> str:
    """Render a type annotation to a clean source-style string.

    Handles unions (X | Y), subscripted generics, custom classes (module
    prefixes stripped), Ellipsis, None, and empty annotations. Never raises
    on types.UnionType (unlike annotation.__name__).
    """
    if annotation is inspect.Parameter.empty or annotation is inspect.Signature.empty:
        return ""
    if annotation is None or annotation is _NONE_TYPE:
        return "None"
    if annotation is Ellipsis:
        return "..."
    if isinstance(annotation, type) and not typing.get_args(annotation):
        return annotation.__qualname__

    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin is typing.Union or isinstance(annotation, types.UnionType):
        return " | ".join(render_annotation(a) for a in args)

    if origin is not None:
        if origin is typing.Literal:
            return f"Literal[{', '.join(repr(a) for a in args)}]"
        if origin is collections.abc.Callable:
            params, ret = args[0], args[-1]
            params_s = "..." if params is Ellipsis else f"[{', '.join(render_annotation(p) for p in params)}]"
            return f"Callable[{params_s}, {render_annotation(ret)}]"
        name = origin.__qualname__ if isinstance(origin, type) else getattr(origin, "_name", None) or str(origin)
        if args:
            return f"{name}[{', '.join(render_annotation(a) for a in args)}]"
        return name

    return _strip_modules(inspect.formatannotation(annotation))


class Context(RenderStrMixin, ABC):
    """
    Base class for different types of contexts.

    Methods:
        render: abstract method to be defined in concrete class to generate string; also aliased using `str()`
    """

    @abstractmethod
    def render(self) -> str:
        """Render the context as a string."""
        raise NotImplementedError


ToolLike = Callable | "ToolContext" | Tool | FunctionToolset


class ToolContext(RenderStrMixin):
    """
    Context for a tool, including its name, arguments, return type, and description.

    Attributes:
        tool_use (str): Description of how to use the tool.
        tool_name (str): Name of the tool.
        tool_description (str): Description of the tool's functionality.
        tool_args (MappingProxyType): Arguments accepted by the tool.
        output_type (Any): Expected output type of the tool.

    Methods:
        args_render: renders text for tool arguments
        render: generates string information for tool context, also aliased using `str()`
    """

    def __init__(self, tool: Callable, tool_use: str | None = None) -> None:
        """Initialize the ToolContext with a tool function."""
        self._tool = tool
        self.tool_use = tool_use or "Reference description for usage."
        self.tool_name = tool.__name__
        self.tool_description = tool.__doc__ or "No description available."
        self.tool_args = inspect.signature(tool).parameters
        self.output_type = inspect.signature(tool).return_annotation

    @classmethod
    def from_pydantic_tool(cls, tool: Tool) -> "ToolContext":
        """
        Create a ToolContext from a pydantic-ai Tool object.

        Args:
            tool: A pydantic-ai Tool instance

        Returns:
            ToolContext wrapping the tool's function with its metadata
        """
        return cls(tool=tool.function)

    @classmethod
    def normalize(cls, tool: "ToolLike | None") -> list["ToolContext"]:
        """
        Normalize any tool type to a list of ToolContext instances.

        Accepts:
        - ToolContext: Returns as single-item list
        - Tool (pydantic-ai): Converts via from_pydantic_tool
        - FunctionToolset (pydantic-ai): Extracts all tools from .tools dict
        - None or invalid: Returns empty list

        Args:
            tool (ToolLike | None): Tool of any supported type

        Returns:
            List of ToolContext instances (may be empty)
        """
        result: list[ToolContext] = []

        if isinstance(tool, cls):
            result.append(tool)
        elif isinstance(tool, Tool):
            result.append(cls.from_pydantic_tool(tool))
        elif isinstance(tool, FunctionToolset):
            for pydantic_tool in tool.tools.values():
                result.append(cls.from_pydantic_tool(pydantic_tool))
        elif isinstance(tool, Callable):
            result.append(cls(tool=tool))

        return result

    def args_render(self) -> str:
        """Render the tool arguments as a string."""
        args_list = []
        for name, param in self.tool_args.items():
            arg = f"{name}"
            if param.annotation is not inspect.Parameter.empty:
                arg += f": {render_annotation(param.annotation)}"
            if param.default is not inspect.Parameter.empty:
                arg += f"{' = ' + str(param.default)}"
            args_list.append(arg)
        return ", ".join(args_list) if args_list else "Doesn't accept arguments"

    def render(self) -> str:
        """Render the tool context as a string."""
        returns = render_annotation(self.output_type) or "None"
        return dedent(f"""
        Name: {self.tool_name}
        Description: {self.tool_description}
        Arguments: {self.args_render()}
        Returns: {returns}
        Usage: {self.tool_use}
        """)
