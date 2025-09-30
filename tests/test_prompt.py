import pytest
from abc import ABCMeta

from proompt.base.prompt import PromptSection, BasePrompt
from proompt.base.context import Context, ToolContext
from proompt.base.provider import BaseProvider


class ConcreteContext(Context):
    """Concrete context for testing."""
    def __init__(self, content: str = "test context"):
        self.content = content
    
    def render(self) -> str:
        return self.content


class ConcreteProvider(BaseProvider):
    """Concrete provider for testing."""
    def __init__(self, name: str = "test_provider"):
        self._name = name
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def provider_ctx(self) -> str:
        return f"Context for {self._name}"
    
    def run(self, *args, **kwargs) -> str:
        return "test result"


class ConcretePromptSection(PromptSection):
    """Concrete implementation for testing PromptSection."""
    
    def formatter(self, *args, **kwargs) -> str:
        return "formatted content"
    
    def render(self) -> str:
        return "rendered section"


class ConcretePrompt(BasePrompt):
    """Concrete implementation for testing BasePrompt."""
    
    def render(self) -> str:
        return "rendered prompt"


class TestPromptSection:
    """Test PromptSection abstract base class."""
    
    @pytest.fixture
    def context(self):
        """Create a test context."""
        return ConcreteContext()
    
    @pytest.fixture
    def provider(self):
        """Create a test provider."""
        return ConcreteProvider()
    
    @pytest.fixture
    def tool_context(self):
        """Create a test tool context."""
        def dummy_tool():
            pass
        return ToolContext(dummy_tool)
    
    @pytest.fixture
    def prompt_section(self, context, provider, tool_context):
        """Create a test prompt section with all components."""
        return ConcretePromptSection(context, [tool_context], provider)
    
    def test_initialization_with_all_params(self, context, provider, tool_context):
        """Test initialization with all parameters."""
        section = ConcretePromptSection(context, [tool_context], provider)
        
        assert section._context == context
        assert len(section.providers) == 1
        assert section.providers[0] == provider
        assert len(section.tools) == 1
        assert section.tools[0] == tool_context
    
    def test_initialization_minimal(self):
        """Test initialization with minimal parameters."""
        section = ConcretePromptSection()
        
        assert section._context is None
        assert section.providers == []
        assert section.tools == []
    
    def test_context_property_get(self, prompt_section, context):
        """Test context property getter."""
        assert prompt_section.context == context
    
    def test_context_property_get_not_set(self):
        """Test context property getter when not set."""
        section = ConcretePromptSection()
        
        with pytest.raises(ValueError, match="Context is not set"):
            _ = section.context
    
    def test_context_property_set_valid(self):
        """Test context property setter with valid context."""
        section = ConcretePromptSection()
        context = ConcreteContext()
        
        section.context = context
        assert section._context == context
    
    def test_context_property_set_invalid(self):
        """Test context property setter with invalid context."""
        section = ConcretePromptSection()
        
        with pytest.raises(TypeError, match="Context must be an instance of Context"):
            section.context = "not a context"
    
    def test_add_providers(self):
        """Test adding providers."""
        section = ConcretePromptSection()
        provider1 = ConcreteProvider("provider1")
        provider2 = ConcreteProvider("provider2")
        
        section.add_providers(provider1, provider2)
        
        assert len(section.providers) == 2
        assert provider1 in section.providers
        assert provider2 in section.providers
    
    def test_add_providers_filters_invalid(self):
        """Test that add_providers filters out non-BaseProvider objects."""
        section = ConcretePromptSection()
        provider = ConcreteProvider()
        
        section.add_providers(provider, "not a provider", None)
        
        assert len(section.providers) == 1
        assert section.providers[0] == provider
    
    def test_add_tools(self):
        """Test adding tools."""
        section = ConcretePromptSection()
        tool1 = ToolContext(lambda: None)
        tool2 = ToolContext(lambda: None)
        
        section.add_tools(tool1, tool2)
        
        assert len(section.tools) == 2
        assert tool1 in section.tools
        assert tool2 in section.tools
    
    def test_add_tools_filters_invalid(self):
        """Test that add_tools filters out non-ToolContext objects."""
        section = ConcretePromptSection()
        tool = ToolContext(lambda: None)
        
        section.add_tools(tool, "not a tool", None)
        
        assert len(section.tools) == 1
        assert section.tools[0] == tool
    
    def test_str_delegates_to_render(self, prompt_section):
        """Test that __str__ delegates to render."""
        assert str(prompt_section) == prompt_section.render()
    
    def test_abstract_methods_enforced(self):
        """Test that abstract methods are enforced."""
        with pytest.raises(TypeError):
            PromptSection()
    
    def test_is_abstract_base_class(self):
        """Test that PromptSection is properly abstract."""
        assert PromptSection.__class__ == ABCMeta
        assert hasattr(PromptSection, '__abstractmethods__')
        assert 'formatter' in PromptSection.__abstractmethods__
        assert 'render' in PromptSection.__abstractmethods__


class TestBasePrompt:
    """Test BasePrompt abstract base class."""
    
    @pytest.fixture
    def prompt_sections(self):
        """Create test prompt sections."""
        return [ConcretePromptSection(), ConcretePromptSection()]
    
    def test_initialization_with_sections(self, prompt_sections):
        """Test initialization with sections."""
        prompt = ConcretePrompt(*prompt_sections)
        
        assert len(prompt.sections) == 2
        assert all(section in prompt.sections for section in prompt_sections)
    
    def test_initialization_empty(self):
        """Test initialization without sections."""
        prompt = ConcretePrompt()
        
        assert prompt.sections == []
    
    def test_str_delegates_to_render(self):
        """Test that __str__ delegates to render."""
        prompt = ConcretePrompt()
        assert str(prompt) == prompt.render()
    
    def test_abstract_method_enforced(self):
        """Test that render method is abstract."""
        with pytest.raises(TypeError):
            BasePrompt()
    
    def test_is_abstract_base_class(self):
        """Test that BasePrompt is properly abstract."""
        assert BasePrompt.__class__ == ABCMeta
        assert hasattr(BasePrompt, '__abstractmethods__')
        assert 'render' in BasePrompt.__abstractmethods__