from abc import ABC, abstractmethod

from proompt.base.context import Context, ToolContext
from proompt.base.provider import BaseProvider


class PromptSection(ABC):
    """Abstract base class for different sections of a prompt."""

    def __init__(
        self,
        context: Context | None = None,
        tools: list[ToolContext] | None = None,
        *providers: BaseProvider | None,
    ):
        self._context = context
        self.providers = list(providers or [])
        self.tools = tools or []

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

    def add_tools(self, *tools: ToolContext) -> None:
        """Add variable quantity of tools."""
        self.tools.extend([t for t in tools if isinstance(t, ToolContext)])

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
    """Abstract base class for different types of prompts."""

    def __init__(self, *sections: PromptSection) -> None:
        self.sections = list(sections or [])

    @abstractmethod
    def render(self) -> str:
        """Render the prompt as a string."""
        raise NotImplementedError

    def __str__(self) -> str:
        """String representation of the prompt."""
        return self.render()
