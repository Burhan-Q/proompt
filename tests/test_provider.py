import pytest
from abc import ABCMeta

from proompt.base.provider import BaseProvider


class ConcreteProvider(BaseProvider):
    """Concrete implementation for testing BaseProvider."""
    
    def __init__(self, name: str = "test_provider", ctx: str = "test context", result: str = "test_result"):
        self._name = name
        self._ctx = ctx
        self._result = result
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def provider_ctx(self) -> str:
        return self._ctx
    
    def run(self, *args, **kwargs) -> str:
        return self._result


class TestBaseProvider:
    """Test BaseProvider abstract base class behavior."""
    
    @pytest.fixture
    def provider(self):
        """Create a test provider instance."""
        return ConcreteProvider()
    
    def test_call_delegates_to_run(self, provider):
        """Test that __call__ delegates to run method."""
        result = provider()
        assert result == "test_result"
        assert result == provider.run()
    
    def test_call_with_args(self, provider):
        """Test that __call__ passes arguments to run method."""
        # Override run to capture args
        def mock_run(*args, **kwargs):
            return f"args:{args}, kwargs:{kwargs}"
        
        provider.run = mock_run
        result = provider("arg1", "arg2", key="value")
        assert "args:('arg1', 'arg2')" in result
        assert "kwargs:{'key': 'value'}" in result
    
    def test_arun_raises_not_implemented(self, provider):
        """Test that arun raises NotImplementedError by default."""
        with pytest.raises(NotImplementedError):
            # Use asyncio to test async method
            import asyncio
            asyncio.run(provider.arun())
    
    def test_abstract_methods_enforced(self):
        """Test that abstract methods are enforced."""
        with pytest.raises(TypeError):
            # Cannot instantiate abstract class
            BaseProvider()
    
    def test_properties_accessible(self, provider):
        """Test that concrete implementation properties work."""
        assert provider.name == "test_provider"
        assert provider.provider_ctx == "test context"
    
    def test_is_abstract_base_class(self):
        """Test that BaseProvider is properly abstract."""
        assert BaseProvider.__class__ == ABCMeta
        assert hasattr(BaseProvider, '__abstractmethods__')
        assert 'name' in BaseProvider.__abstractmethods__
        assert 'provider_ctx' in BaseProvider.__abstractmethods__
        assert 'run' in BaseProvider.__abstractmethods__