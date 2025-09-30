import inspect
from abc import ABC, abstractmethod
from textwrap import dedent
from typing import Callable


class Context(ABC):
    """Base class for different types of contexts."""

    @abstractmethod
    def render(self) -> str:
        """Render the context as a string."""
        raise NotImplementedError

    def __str__(self) -> str:
        """String representation of the context."""
        return self.render()


class ToolContext(Context):
    """Context for a tool, including its name, arguments, return type, and description."""

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
            if param.annotation is not inspect.Parameter.empty:
                args_list.append(
                    f"{name}: {param.annotation.__name__}{' = ' + str(param.default) if param.default is not inspect.Parameter.empty else ''}"
                )
            else:
                args_list.append(name)
        return ", ".join(args_list)

    def render(self) -> str:
        """Render the tool context as a string."""
        return dedent(f"""
        Name: {self.tool_name}
        Description: {self.tool_description}
        Arguments: {self.args_render()}
        Returns: {self.output_type.__name__ if self.output_type is not inspect.Signature.empty else "None"}
        Usage: {self.tool_use}
        """)
