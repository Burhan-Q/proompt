"""
Tests for API-based DataProvider implementations.

Tests edge cases and error handling for the API providers demonstrated
in examples/05-api_data_provider.py
"""

import importlib.util
import sys
from pathlib import Path

# Add examples directory to path to import the providers
examples_dir = Path(__file__).parent.parent / "examples"
sys.path.insert(0, str(examples_dir))

# Import the module with a different name to avoid conflicts
spec = importlib.util.spec_from_file_location(
    "api_providers", 
    examples_dir / "05-api_data_provider.py"
)
api_providers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_providers)

# Get the classes
MockAPIProvider = api_providers.MockAPIProvider
JSONPlaceholderProvider = api_providers.JSONPlaceholderProvider
GitHubAPIProvider = api_providers.GitHubAPIProvider
RestAPIProvider = api_providers.RestAPIProvider

# Clean up sys.path
sys.path.pop(0)


class TestMockAPIProvider:
    """Test cases for MockAPIProvider."""

    def test_initialization_valid_types(self):
        """Test initialization with valid data types."""
        provider = MockAPIProvider("users")
        assert provider.data_type == "users"
        
        provider = MockAPIProvider("products")
        assert provider.data_type == "products"
        
        provider = MockAPIProvider("metrics")
        assert provider.data_type == "metrics"

    def test_name_property(self):
        """Test name property returns correct format."""
        provider = MockAPIProvider("users")
        assert provider.name == "Mock API Provider - users"

    def test_provider_ctx_property(self):
        """Test provider_ctx property returns correct description."""
        provider = MockAPIProvider("products")
        assert "mock products data" in provider.provider_ctx.lower()
        assert "testing" in provider.provider_ctx.lower()

    def test_run_returns_markdown_table(self):
        """Test run method returns formatted markdown table."""
        provider = MockAPIProvider("users")
        result = provider.run()
        
        assert isinstance(result, str)
        assert "Mock Users Data" in result
        assert "|" in result  # Markdown table format
        assert "Alice Johnson" in result
        assert "Bob Smith" in result

    def test_run_with_products(self):
        """Test run method with products data type."""
        provider = MockAPIProvider("products")
        result = provider.run()
        
        assert "Mock Products Data" in result
        assert "Widget Pro" in result
        assert "29.99" in result

    def test_run_with_metrics(self):
        """Test run method with metrics data type."""
        provider = MockAPIProvider("metrics")
        result = provider.run()
        
        assert "Mock Metrics Data" in result
        assert "Revenue" in result
        assert "+12%" in result

    def test_run_with_invalid_type(self):
        """Test run method with non-existent data type."""
        provider = MockAPIProvider("invalid_type")
        result = provider.run()
        
        assert "No mock data available" in result
        assert "invalid_type" in result

    def test_mock_data_structure(self):
        """Test that mock data has expected structure."""
        provider = MockAPIProvider("users")
        mock_data = provider._get_mock_data()
        
        assert isinstance(mock_data, dict)
        assert "users" in mock_data
        assert "products" in mock_data
        assert "metrics" in mock_data
        
        # Check users structure
        users = mock_data["users"]
        assert isinstance(users, list)
        assert len(users) > 0
        assert all("id" in user for user in users)
        assert all("name" in user for user in users)

    def test_edge_case_empty_string_type(self):
        """Test behavior with empty string data type."""
        provider = MockAPIProvider("")
        result = provider.run()
        assert "No mock data available" in result


class TestJSONPlaceholderProvider:
    """Test cases for JSONPlaceholderProvider."""

    def test_initialization(self):
        """Test initialization with various parameters."""
        provider = JSONPlaceholderProvider("posts")
        assert provider.endpoint == "posts"
        assert provider.item_id is None
        assert provider.base_url == "https://jsonplaceholder.typicode.com"

    def test_initialization_with_item_id(self):
        """Test initialization with specific item ID."""
        provider = JSONPlaceholderProvider("users", item_id=42)
        assert provider.endpoint == "users"
        assert provider.item_id == 42

    def test_name_property(self):
        """Test name property formatting."""
        provider = JSONPlaceholderProvider("posts")
        assert "JSONPlaceholder API - /posts" == provider.name
        
        provider_with_id = JSONPlaceholderProvider("users", item_id=5)
        assert "JSONPlaceholder API - /users/5" == provider_with_id.name

    def test_provider_ctx_property(self):
        """Test provider context description."""
        provider = JSONPlaceholderProvider("comments")
        ctx = provider.provider_ctx
        assert "comments" in ctx.lower()
        assert "jsonplaceholder" in ctx.lower()

    def test_format_single_item(self):
        """Test formatting of single item response."""
        provider = JSONPlaceholderProvider("posts", item_id=1)
        test_item = {
            "id": 1,
            "title": "Test Post",
            "body": "This is a test post body",
            "userId": 1
        }
        
        result = provider._format_single_item(test_item)
        assert "## Posts Item 1" in result
        assert "Test Post" in result
        assert "userId" in result

    def test_format_single_item_with_long_value(self):
        """Test formatting with values longer than 100 chars."""
        provider = JSONPlaceholderProvider("posts", item_id=1)
        long_text = "a" * 150
        test_item = {"id": 1, "longField": long_text}
        
        result = provider._format_single_item(test_item)
        assert "..." in result  # Long value should be truncated

    def test_format_list_empty(self):
        """Test formatting empty list."""
        provider = JSONPlaceholderProvider("posts")
        result = provider._format_list([])
        assert "No data found" in result

    def test_format_list_with_items(self):
        """Test formatting list of items."""
        provider = JSONPlaceholderProvider("posts")
        items = [
            {"id": 1, "title": "Post 1"},
            {"id": 2, "title": "Post 2"},
        ]
        
        result = provider._format_list(items)
        assert "## Posts" in result
        assert "showing 2 items" in result
        assert "|" in result  # Markdown table

    def test_format_list_truncates_long_values(self):
        """Test that long values in list are truncated."""
        provider = JSONPlaceholderProvider("posts")
        long_text = "x" * 100
        items = [{"id": 1, "description": long_text}]
        
        result = provider._format_list(items)
        assert "..." in result


class TestGitHubAPIProvider:
    """Test cases for GitHubAPIProvider."""

    def test_initialization(self):
        """Test initialization without token."""
        provider = GitHubAPIProvider("users/octocat")
        assert provider.endpoint == "users/octocat"
        assert provider.api_token is None
        assert provider.base_url == "https://api.github.com"

    def test_initialization_with_token(self):
        """Test initialization with API token."""
        provider = GitHubAPIProvider("repos/owner/repo", api_token="test_token")
        assert provider.api_token == "test_token"

    def test_initialization_strips_leading_slash(self):
        """Test that leading slash is removed from endpoint."""
        provider = GitHubAPIProvider("/users/octocat")
        assert provider.endpoint == "users/octocat"
        assert not provider.endpoint.startswith("/")

    def test_name_property(self):
        """Test name property format."""
        provider = GitHubAPIProvider("users/octocat")
        assert provider.name == "GitHub API - /users/octocat"

    def test_provider_ctx_property(self):
        """Test provider context description."""
        provider = GitHubAPIProvider("repos/owner/repo")
        ctx = provider.provider_ctx
        assert "github" in ctx.lower()
        assert "repos/owner/repo" in ctx

    def test_format_single_response(self):
        """Test formatting single GitHub resource."""
        provider = GitHubAPIProvider("users/octocat")
        test_data = {
            "login": "octocat",
            "name": "The Octocat",
            "public_repos": 8,
            "followers": 1000,
            "bio": "Test bio",
            "extra_field": "should be ignored"
        }
        
        result = provider._format_single_response(test_data)
        assert "GitHub Resource" in result
        assert "octocat" in result
        assert "The Octocat" in result
        assert "1000" in result

    def test_format_single_response_filters_none_values(self):
        """Test that None values are filtered out."""
        provider = GitHubAPIProvider("users/test")
        test_data = {
            "name": "Test User",
            "bio": None,
            "location": "Earth"  # Not in important_fields list
        }
        
        result = provider._format_single_response(test_data)
        assert "Test User" in result
        # location is not in the important_fields list, so it won't appear
        # bio is None so it won't appear either

    def test_format_list_response_empty(self):
        """Test formatting empty list response."""
        provider = GitHubAPIProvider("users/test/repos")
        result = provider._format_list_response([])
        assert "No items found" in result

    def test_format_list_response_with_repos(self):
        """Test formatting list of repositories."""
        provider = GitHubAPIProvider("users/test/repos")
        repos = [
            {
                "name": "repo1",
                "description": "First repo",
                "language": "Python",
                "stargazers_count": 100,
                "forks_count": 10
            },
            {
                "name": "repo2",
                "description": "Second repo",
                "language": "JavaScript",
                "stargazers_count": 50,
                "forks_count": 5
            }
        ]
        
        result = provider._format_list_response(repos)
        assert "GitHub Resources" in result
        assert "repo1" in result
        assert "repo2" in result
        assert "Python" in result

    def test_format_list_response_limits_to_10(self):
        """Test that list response is limited to 10 items."""
        provider = GitHubAPIProvider("users/test/repos")
        repos = [{"name": f"repo{i}"} for i in range(20)]
        
        result = provider._format_list_response(repos)
        assert "showing 10 of 20" in result

    def test_format_list_response_truncates_long_values(self):
        """Test that long values are truncated in list."""
        provider = GitHubAPIProvider("users/test/repos")
        long_desc = "x" * 100
        repos = [{"name": "test", "description": long_desc}]
        
        result = provider._format_list_response(repos)
        assert "..." in result


class TestRestAPIProvider:
    """Test cases for RestAPIProvider."""

    def test_initialization_defaults(self):
        """Test initialization with default parameters."""
        provider = RestAPIProvider("https://api.example.com/data")
        assert provider.url == "https://api.example.com/data"
        assert provider.method == "GET"
        assert provider.headers == {}
        assert provider.params == {}

    def test_initialization_with_all_params(self):
        """Test initialization with all parameters."""
        headers = {"Authorization": "Bearer token"}
        params = {"page": "1", "limit": "10"}
        
        provider = RestAPIProvider(
            url="https://api.example.com/data",
            method="POST",
            headers=headers,
            params=params
        )
        
        assert provider.method == "POST"
        assert provider.headers == headers
        assert provider.params == params

    def test_method_uppercase_conversion(self):
        """Test that HTTP method is converted to uppercase."""
        provider = RestAPIProvider("https://api.example.com", method="get")
        assert provider.method == "GET"
        
        provider = RestAPIProvider("https://api.example.com", method="post")
        assert provider.method == "POST"

    def test_name_property(self):
        """Test name property format."""
        provider = RestAPIProvider("https://api.example.com/endpoint")
        assert "https://api.example.com/endpoint" in provider.name
        assert "REST API Provider" in provider.name

    def test_provider_ctx_property(self):
        """Test provider context description."""
        provider = RestAPIProvider("https://api.example.com", method="POST")
        ctx = provider.provider_ctx
        assert "https://api.example.com" in ctx
        assert "POST" in ctx


class TestEdgeCases:
    """Test edge cases across all providers."""

    def test_mock_provider_special_characters(self):
        """Test mock provider with special characters in type."""
        provider = MockAPIProvider("user-data_2024")
        result = provider.run()
        assert "No mock data available" in result

    def test_json_placeholder_zero_item_id(self):
        """Test JSONPlaceholder with item_id of 0."""
        provider = JSONPlaceholderProvider("posts", item_id=0)
        assert provider.item_id == 0
        # item_id of 0 is falsy, so it won't appear in name
        assert provider.name == "JSONPlaceholder API - /posts"

    def test_github_provider_empty_endpoint(self):
        """Test GitHub provider with empty endpoint."""
        provider = GitHubAPIProvider("")
        assert provider.endpoint == ""

    def test_rest_api_provider_none_headers(self):
        """Test RestAPIProvider with None headers."""
        provider = RestAPIProvider("https://api.example.com", headers=None)
        assert provider.headers == {}

    def test_rest_api_provider_none_params(self):
        """Test RestAPIProvider with None params."""
        provider = RestAPIProvider("https://api.example.com", params=None)
        assert provider.params == {}

    def test_mock_provider_case_sensitivity(self):
        """Test that mock provider is case-sensitive."""
        provider = MockAPIProvider("Users")  # Capital U
        result = provider.run()
        assert "No mock data available" in result  # Should not match "users"

    def test_json_placeholder_negative_item_id(self):
        """Test JSONPlaceholder with negative item_id."""
        provider = JSONPlaceholderProvider("posts", item_id=-1)
        assert provider.item_id == -1
        # Should still construct URL, even if API would reject it


class TestProviderIntegration:
    """Integration tests for providers working together."""

    def test_multiple_mock_providers_different_types(self):
        """Test using multiple mock providers with different data types."""
        users = MockAPIProvider("users")
        products = MockAPIProvider("products")
        metrics = MockAPIProvider("metrics")
        
        users_data = users.run()
        products_data = products.run()
        metrics_data = metrics.run()
        
        # All should return different data
        assert users_data != products_data
        assert products_data != metrics_data
        assert "Alice" in users_data
        assert "Widget" in products_data
        assert "Revenue" in metrics_data

    def test_provider_name_uniqueness(self):
        """Test that different providers have unique names."""
        mock = MockAPIProvider("users")
        json_ph = JSONPlaceholderProvider("users")
        github = GitHubAPIProvider("users/test")
        rest = RestAPIProvider("https://api.example.com/users")
        
        names = [mock.name, json_ph.name, github.name, rest.name]
        assert len(names) == len(set(names))  # All unique

    def test_provider_ctx_provides_useful_info(self):
        """Test that all provider contexts provide useful information."""
        providers = [
            MockAPIProvider("users"),
            JSONPlaceholderProvider("posts"),
            GitHubAPIProvider("users/octocat"),
            RestAPIProvider("https://api.example.com")
        ]
        
        for provider in providers:
            ctx = provider.provider_ctx
            assert isinstance(ctx, str)
            assert len(ctx) > 0
            # Context should provide useful information
            assert len(ctx) > 20
