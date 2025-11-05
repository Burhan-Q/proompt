from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from proompt.base.context import PYDANTIC_AI_AVAILABLE, Context, ToolContext
from proompt.base.provider import BaseProvider

if TYPE_CHECKING:
    if PYDANTIC_AI_AVAILABLE:
        from pydantic_ai.tools import Tool as PydanticTool  # noqa: F401
        from pydantic_ai.toolsets import FunctionToolset  # noqa: F401


class PromptSection(ABC):
    """
    Abstract base class for different sections of a prompt.

    Attributes:
        tools (list[ToolContext]): context information on tools to include in prompt
        providers (BaseProvider): variable number of data providers, generally a subclass of BaseProvider

    Properties:
        context (Context): context information only accessible at runtime

    Methods:
        add_providers: extend the providers included
        add_tools: extend the tools included
        formatter: abstract method to be defined in concrete class
        render: abstract method to be defined in concrete class to generate string; also aliased using `str()`
    """

    def __init__(
        self,
        context: Context | None = None,
        tools: list | None = None,
        *providers: BaseProvider | None,
    ):
        self._context = context
        self.providers = list(providers or [])
        # Normalize all tools to ToolContext
        self.tools: list[ToolContext] = []
        for t in (tools or []):
            if t is None:
                continue
            normalized = self._normalize_tool(t)
            if normalized is None:
                continue
            if isinstance(normalized, list):
                self.tools.extend(normalized)
            else:
                self.tools.append(normalized)

    @property
    def context(self) -> Context:
        """Get the context."""
        if not self._context:
            raise ValueError(f"Context is not set for {self.__class__.__name__}.")
        return self._context

    @context.setter
    def context(self, value: Context) -> None:
        """Set the context."""
        if not isinstance(value, Context) or issubclass(value.__class__, Context) is False:
            raise TypeError(f"Context must be an instance of Context or its subclass for {self.__class__.__name__}.")
        self._context = value

    def add_providers(self, *providers: BaseProvider) -> None:
        """Add variable quantity of providers."""
        self.providers.extend([p for p in providers if isinstance(p, BaseProvider)])

    def add_tools(self, *tools) -> None:
        """Add variable quantity of tools (ToolContext, pydantic-ai Tool, or FunctionToolset)."""
        for t in tools:
            if t is None:
                continue  # Skip None values for backward compatibility
            normalized = self._normalize_tool(t)
            if normalized is None:
                continue  # Skip invalid tools
            if isinstance(normalized, list):
                self.tools.extend(normalized)
            else:
                self.tools.append(normalized)

    def _normalize_tool(self, tool) -> ToolContext | list[ToolContext] | None:
        """
        Normalize a tool to ToolContext.
        
        Accepts:
        - ToolContext (returned as-is)
        - pydantic-ai Tool (converted to ToolContext)
        - pydantic-ai FunctionToolset (tools extracted and each converted)
        - None or invalid objects (returns None, silently skipped for backward compatibility)
        
        Args:
            tool: A ToolContext, pydantic-ai Tool, or FunctionToolset instance
            
        Returns:
            A ToolContext, list of ToolContext instances, or None if invalid
        """
        # Skip None values
        if tool is None:
            return None
            
        # If already ToolContext, return as-is
        if isinstance(tool, ToolContext):
            return tool
        
        # Try to detect and handle pydantic-ai FunctionToolset
        # FunctionToolset stores tools in a .tools dict attribute where values are Tool objects
        if PYDANTIC_AI_AVAILABLE and hasattr(tool, 'tools'):
            tools_attr = getattr(tool, 'tools', None)
            # Check if it's a dict (FunctionToolset stores tools as {name: Tool})
            if isinstance(tools_attr, dict):
                result = []
                for tool_obj in tools_attr.values():
                    normalized = self._normalize_tool(tool_obj)
                    if normalized is None:
                        continue
                    if isinstance(normalized, list):
                        result.extend(normalized)
                    else:
                        result.append(normalized)
                return result if result else None
        
        # Try to handle it as a pydantic-ai Tool object
        if PYDANTIC_AI_AVAILABLE:
            try:
                return ToolContext.from_pydantic_tool(tool)
            except (AttributeError, TypeError):
                # If it's not a valid Tool, return None (backward compatible)
                return None
        
        # If pydantic-ai not available and not a ToolContext, return None (backward compatible)
        return None

    @abstractmethod
    def formatter(self, *args, **kwargs) -> str:
        """Format the prompt text."""
        raise NotImplementedError

    @abstractmethod
    def render(self) -> str:
        """Render the prompt section as a string."""
        raise NotImplementedError

    def __str__(self) -> str:
        """String representation of the prompt section."""
        return self.render()


class BasePrompt(ABC):
    """
    Abstract base class for different types of prompts.

    Attributes:
        sections (PromptSection): list of prompt sections that compose the final prompt

    Methods:
        render: abstract method to be defined in concrete class to generate string; also aliased using `str()`
    """

    def __init__(self, *sections: PromptSection) -> None:
        self.sections = list(sections or [])

    @abstractmethod
    def render(self) -> str:
        """Render the prompt as a string."""
        raise NotImplementedError

    def __str__(self) -> str:
        """String representation of the prompt."""
        return self.render()
