# Unit Tests for proompt

This directory contains comprehensive unit tests for the `proompt.base` module components,
the concrete `proompt.data`/`proompt.providers` providers, and the top-level `proompt` package.

## Test Structure

### test_provider.py
- **TestBaseProvider**: Tests for the abstract BaseProvider class
  - Tests `__call__` delegation to `run()`
  - Tests `arun()` raises NotImplementedError by default
  - Tests abstract method enforcement
  - Tests property access
  - Tests default `__repr__` surfaces `name`/`provider_ctx`

### test_context.py
- **TestContextBase**: Tests for the abstract Context class
  - Tests `__str__` delegation to `render()`
  - Tests abstract method enforcement
- **TestRenderAnnotation**: Tests for the `render_annotation()` helper
  - Parametrized over plain types, unions, subscripted generics, `Literal`,
    `Callable`, `TypeVar`, and custom classes
- **TestToolContext**: Tests for ToolContext implementation
  - Tests initialization with different function signatures
  - Tests argument rendering with/without type annotations
  - Tests docstring handling
  - Tests output formatting
  - Uses parametrized tests for different return types

### test_prompt.py
- **TestPromptSection**: Tests for PromptSection abstract class
  - Tests initialization with various parameter combinations
  - Tests context property getter/setter with validation
  - Tests provider and tool management (add_providers, add_tools)
  - Tests filtering of invalid inputs
  - Tests abstract method enforcement
- **TestBasePrompt**: Tests for BasePrompt abstract class
  - Tests initialization with sections
  - Tests `__str__` delegation to `render()`
  - Tests abstract method enforcement

### test_data.py
- Tests `CsvDataProvider`/`SqliteProvider`/`FileDataProvider` return raw `TableData`
  (not pre-rendered markdown) from `run()`
- Tests the `proompt.providers` namespace re-exports the same objects as `proompt.data`
- Tests empty-result handling (zero rows, header-only CSV) renders "No results found."

### test_package.py
- Tests the top-level `proompt` package exposes the curated public API via `__all__`

## Design Principles

1. **Minimal but Robust**: Only tests essential behavior and edge cases
2. **SOLID Compliance**: Tests follow single responsibility and proper abstraction
3. **No Mocking**: Uses concrete implementations instead of mocks where possible
4. **Fixtures**: Leverages pytest fixtures for DRY principle
5. **Parametrization**: Uses `@pytest.mark.parametrize` for testing multiple scenarios
6. **Class Organization**: Groups related tests in logical classes

## Coverage

The test suite covers:
- ✅ Abstract class behavior and enforcement
- ✅ Property getters and setters
- ✅ Method delegation patterns
- ✅ Input validation and filtering
- ✅ Error handling and edge cases
- ✅ String representation methods
- ✅ Initialization with various parameters

All 70 tests pass, ensuring the library's functionality is working correctly.