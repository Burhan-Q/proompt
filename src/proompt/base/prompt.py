from abc import ABC, abstractmethod
from collections.abc import Iterable

from proompt.base.context import Context, ToolContext, ToolLike
from proompt.base.mixins import RenderStrMixin
from proompt.base.provider import BaseProvider


class PromptSection(RenderStrMixin, ABC):
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
        providers: Iterable[BaseProvider] | None = None,
        tools: Iterable[ToolLike] | None = None,
    ) -> None:
        """Initialize with optional context, providers, and tools."""
        self._context = context
        self.providers: list[BaseProvider] = []
        self.tools: list[ToolContext] = []
        self.add_providers(*(providers or ()))
        self.add_tools(*(tools or ()))

    @property
    def context(self) -> Context | None:
        """Get the context (None if unset)."""
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
            self.tools.extend(ToolContext.normalize(t))

    @abstractmethod
    def formatter(self, *args, **kwargs) -> str:
        """Format the prompt text."""
        raise NotImplementedError

    @abstractmethod
    def render(self) -> str:
        """Render the prompt section as a string."""
        raise NotImplementedError


class BasePrompt(RenderStrMixin, ABC):
    """
    Abstract base class for different types of prompts.

    Attributes:
        sections (PromptSection): list of prompt sections that compose the final prompt

    Methods:
        render: abstract method to be defined in concrete class to generate string; also aliased using `str()`
    """

    def __init__(self, *sections: PromptSection) -> None:
        """Initialize the BasePrompt with sections."""
        self.sections = list(sections or [])

    @abstractmethod
    def render(self) -> str:
        """Render the prompt as a string."""
        raise NotImplementedError
