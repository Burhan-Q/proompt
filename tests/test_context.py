import inspect
from abc import ABCMeta
from textwrap import dedent

import pytest

from proompt.base.context import Context, ToolContext


def format_args(args_dict: dict) -> str:
    """Tool argument string formatting logic."""
    args_list = []
    for name, param in args_dict.items():
        if param.annotation is not inspect.Parameter.empty:
            args_list.append(
                f"{name}: {param.annotation.__name__}"
                f"{' = ' + str(param.default) if param.default is not inspect.Parameter.empty else ''}"
            )
        else:
            args_list.append(name)
    return ", ".join(args_list)


class ConcreteContext(Context):
    """Concrete implementation for testing Context."""

    def __init__(self, content: str = "test content"):
        self.content = content

    def render(self) -> str:
        return self.content


class TestContextBase:
    """Test Context abstract base class behavior."""

    @pytest.fixture
    def context(self):
        """Create a test context instance."""
        return ConcreteContext()

    def test_str_delegates_to_render(self, context: ConcreteContext):
        """Test that __str__ delegates to render method."""
        assert str(context) == context.render()
        assert str(context) == "test content"

    def test_abstract_method_enforced(self):
        """Test that render method is abstract."""
        with pytest.raises(TypeError):
            Context()

    def test_is_abstract_base_class(self):
        """Test that Context is properly abstract."""
        assert Context.__class__ == ABCMeta
        assert hasattr(Context, "__abstractmethods__")
        assert "render" in Context.__abstractmethods__


class TestToolContext:
    """Test ToolContext implementation."""

    @pytest.fixture(
        params=[
            # (function, expected_name, has_args, has_return_type)
            (lambda: None, "<lambda>", False, False),
            (lambda x: x, "<lambda>", True, False),
            (lambda x, y=1: x + y, "<lambda>", True, False),
        ]
    )
    def sample_function(self, request):
        """Parametrized fixture for different function types."""
        return request.param

    @pytest.fixture
    def named_function(self):
        """A named function for testing."""

        def test_function(x: int, y: str = "default") -> str:
            """Test function docstring."""
            return f"{x}:{y}"

        return test_function

    @pytest.fixture
    def function_no_doc(self):
        """A function without docstring."""

        def no_doc_function():
            pass

        return no_doc_function

    def test_tool_context_initialization(self, named_function):
        """Test ToolContext initialization with a named function."""
        tool_ctx = ToolContext(named_function)

        assert tool_ctx.tool_name == "test_function"
        assert tool_ctx.tool_description == "Test function docstring."
        assert tool_ctx.tool_use == "Reference description for usage."  # default
        assert len(tool_ctx.tool_args) == 2
        assert tool_ctx.output_type is str

    def test_tool_context_with_custom_use(self, named_function):
        """Test ToolContext with custom tool_use."""
        custom_use = "Custom usage description"
        tool_ctx = ToolContext(named_function, tool_use=custom_use)
        assert tool_ctx.tool_use == custom_use

    def test_tool_context_no_docstring(self, function_no_doc):
        """Test ToolContext with function that has no docstring."""
        tool_ctx = ToolContext(function_no_doc)

        assert tool_ctx.tool_description == "No description available."

    def test_args_render_with_annotations(self, named_function):
        """Test args_render method with type annotations."""
        tool_ctx = ToolContext(named_function)
        args_str = tool_ctx.args_render()

        assert "x: int" in args_str
        assert "y: str = default" in args_str

    def test_args_render_no_annotations(self):
        """Test args_render method without type annotations."""

        def simple_func(a, b):
            pass

        tool_ctx = ToolContext(simple_func)
        assert tool_ctx.args_render() == "a, b"
        assert tool_ctx.output_type is inspect.Parameter.empty

    def test_render_output(self, named_function):
        """Test that render produces expected format."""
        tool_ctx = ToolContext(named_function)
        rendered = tool_ctx.render()
        result = dedent(f"""
            Name: {named_function.__name__}
            Description: {named_function.__doc__ or "No description available."}
            Arguments: {format_args(dict(inspect.signature(named_function).parameters))}
            Returns: {inspect.signature(named_function).return_annotation.__name__}
            Usage: Reference description for usage.
            """)

        assert rendered == result

    def test_str_delegates_to_render(self, named_function):
        """Test that __str__ delegates to render."""
        tool_ctx = ToolContext(named_function)
        assert str(tool_ctx) == tool_ctx.render()

    # TODO: more nicer
    def f():
        pass

    @pytest.mark.parametrize(
        "func,expected_return",
        [
            (lambda: None, "None"),
            (lambda x: x, "None"),  # No annotation means None
            (f, ""),
        ],
    )
    def test_return_type_handling(self, func, expected_return):
        """Test handling of different return type annotations."""
        tool_ctx = ToolContext(func)
        rendered = tool_ctx.render()
        assert f"Returns: {expected_return}" in rendered
        # TODO: more complete
