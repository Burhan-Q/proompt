from abc import ABCMeta

import pytest

from proompt.base.provider import BaseProvider

PROVIDER_STR = "Provider Name: {}\nProvider Context: {}"


class ConcreteProvider(BaseProvider[str]):
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


class DictProvider(BaseProvider[dict]):
    """A concrete dictionary data provider instance."""

    def __init__(self, name: str = "dict-provider", ctx: str = "A series of key-value pairs."):
        self._name = name
        self._provider_ctx = ctx

    @property
    def name(self) -> str:
        return self._name

    @property
    def provider_ctx(self) -> str:
        return self._provider_ctx

    def run(self, *args, **kwargs) -> dict:
        return kwargs

    def __str__(self) -> str:
        return PROVIDER_STR.format(self.name, self.provider_ctx)


class TestBaseProvider:
    """Test BaseProvider abstract base class behavior."""

    @pytest.fixture
    def provider(self) -> ConcreteProvider:
        """Create a test provider instance."""
        return ConcreteProvider()

    @pytest.fixture
    def dict_provider(self) -> DictProvider:
        return DictProvider()

    def test_call_delegates_to_run(self, provider: ConcreteProvider, dict_provider: DictProvider):
        """Test that __call__ delegates to run method."""
        assert provider() == "test_result" == provider.run()
        assert isinstance(dict_provider(), dict)

    def test_call_with_args(self, provider: ConcreteProvider, dict_provider: DictProvider):
        """Test that __call__ passes arguments to run method."""

        # Override run to capture args
        def mock_run(*args, **kwargs):
            return f"args:{args}, kwargs:{kwargs}"

        provider.run = mock_run
        result = provider("arg1", "arg2", key="value")
        assert "args:('arg1', 'arg2')" in result and "kwargs:{'key': 'value'}" in result
        assert "args:(), kwargs:{}" == provider.run()
        assert dict_provider(1, 2, 3, this="that", the_answer=42) == {"this": "that", "the_answer": 42}

    def test_arun_raises_not_implemented(self, provider: ConcreteProvider):
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

    def test_properties_accessible(self, provider: ConcreteProvider, dict_provider: DictProvider):
        """Test that concrete implementation properties work."""
        assert provider.name == "test_provider"
        assert provider.provider_ctx == "test context"
        assert (
            str(dict_provider) == PROVIDER_STR.format(dict_provider.name, dict_provider.provider_ctx)
        ) and f"{dict_provider}" == PROVIDER_STR.format(dict_provider.name, dict_provider.provider_ctx)

    def test_is_abstract_base_class(self):
        """Test that BaseProvider is properly abstract."""
        assert BaseProvider.__class__ == ABCMeta
        assert hasattr(BaseProvider, "__abstractmethods__")
        assert "name" in BaseProvider.__abstractmethods__
        assert "provider_ctx" in BaseProvider.__abstractmethods__
        assert "run" in BaseProvider.__abstractmethods__
