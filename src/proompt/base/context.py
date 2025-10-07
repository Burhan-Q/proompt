import inspect
from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Callable


class Context(ABC):
    """
    Base class for different types of contexts.

    Methods:
        render: abstract method to be defined in concrete class to generate string; also aliased using `str()`
    """

    @abstractmethod
    def render(self) -> str:
        """Render the context as a string."""
        raise NotImplementedError

    def __str__(self) -> str:
        """String representation of the context."""
        return self.render()


class ToolContext(Context):
    """
    Context for a tool, including its name, arguments, return type, and description.

    Attributes:
        tool_use (str): Description of how to use the tool.
        tool_name (str): Name of the tool.
        tool_args (MappingProxytype): Arguments accepted by the tool.
        output_type (Any): Expected output type of the tool.
        tool_description (str): Description of the tool's functionality.

    Methods:
        args_render: renders text for tool arguments
        render: generates string information for tool context, also aliased using `str()`
    """

    def __init__(self, tool: Callable, tool_use: str | None = None) -> None:
        """Initialize the ToolContext with a tool function."""
        self._tool = tool
        self.tool_use = tool_use or "Reference description for usage."
        self.tool_name = tool.__name__
        self.tool_args = inspect.signature(tool).parameters
        self.output_type = inspect.signature(tool).return_annotation
        self.tool_description = tool.__doc__ or "No description available."

    def args_render(self) -> str:
        """Render the tool arguments as a string."""
        args_list = []
        for name, param in self.tool_args.items():
            arg = f"{name}"
            if param.annotation is not inspect.Parameter.empty:
                arg += f": {param.annotation.__name__}"
            if param.default is not inspect.Parameter.empty:
                arg += f"{' = ' + str(param.default)}"
            args_list.append(arg)
        return ", ".join(args_list) if args_list else "Doesn't accept arguments"

    def render(self) -> str:
        """Render the tool context as a string."""
        return dedent(f"""
        Name: {self.tool_name}
        Description: {self.tool_description}
        Arguments: {self.args_render()}
        Returns: {"None" if self.output_type in (inspect.Signature.empty, None) else self.output_type.__name__}
        Usage: {self.tool_use}
        """)
