#!/usr/bin/env python3
"""
API-Based DataProvider Example

This example demonstrates how to create custom DataProviders that fetch data from real APIs.
Shows practical patterns for:
- REST API integration with authentication
- Error handling and response validation
- Data transformation for LLM consumption
- Multiple API provider implementations
- Both synchronous and asynchronous operations

NOTE: This example uses publicly available APIs that don't require authentication.
For production use, add proper error handling, rate limiting, and authentication.
"""

import json
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from proompt.base.provider import BaseProvider
from proompt.data import TableData


# EXAMPLE 0: Mock API Provider (No Network Required)


class MockAPIProvider(BaseProvider[str]):
    """
    Mock API provider for testing and demonstration purposes.
    
    This provider simulates API responses without requiring network access.
    Useful for:
    - Testing your prompt engineering setup
    - Demonstrating API integration patterns
    - Development when API credentials are not available
    """

    def __init__(self, data_type: str = "users"):
        """
        Initialize mock API provider.
        
        Args:
            data_type: Type of mock data to return (users, products, metrics)
        """
        self.data_type = data_type
        self._mock_data = self._get_mock_data()

    @property
    def name(self) -> str:
        return f"Mock API Provider - {self.data_type}"

    @property
    def provider_ctx(self) -> str:
        return f"Simulated API providing mock {self.data_type} data for testing purposes."

    def _get_mock_data(self) -> dict[str, list[dict]]:
        """Generate mock data for different types."""
        return {
            "users": [
                {"id": 1, "name": "Alice Johnson", "role": "Engineer", "active": True},
                {"id": 2, "name": "Bob Smith", "role": "Designer", "active": True},
                {"id": 3, "name": "Carol White", "role": "Manager", "active": False},
            ],
            "products": [
                {"id": 101, "name": "Widget Pro", "price": 29.99, "stock": 150},
                {"id": 102, "name": "Gadget Max", "price": 49.99, "stock": 75},
                {"id": 103, "name": "Tool Plus", "price": 19.99, "stock": 200},
            ],
            "metrics": [
                {"metric": "Revenue", "value": 125000, "change": "+12%"},
                {"metric": "Users", "value": 5420, "change": "+8%"},
                {"metric": "Engagement", "value": 78.5, "change": "+3%"},
            ],
        }

    def run(self) -> str:
        """Return mock data as a formatted markdown table."""
        data = self._mock_data.get(self.data_type, [])
        
        if not data:
            return f"No mock data available for type: {self.data_type}"

        # Convert to TableData format
        headers = list(data[0].keys())
        rows = [[str(item[key]) for key in headers] for item in data]
        
        table = TableData.from_rows(headers, rows)
        return f"## Mock {self.data_type.title()} Data\n\n{table.to_md()}"


# EXAMPLE 1: Simple JSON API Provider


class JSONPlaceholderProvider(BaseProvider[str]):
    """
    Fetches data from JSONPlaceholder - a free fake REST API for testing.
    
    Example endpoints:
    - /posts - Blog posts
    - /users - User information
    - /comments - Comments on posts
    
    Website: https://jsonplaceholder.typicode.com
    """

    def __init__(self, endpoint: str = "posts", item_id: int | None = None):
        """
        Initialize the JSONPlaceholder API provider.
        
        Args:
            endpoint: API endpoint (posts, users, comments, etc.)
            item_id: Optional specific item ID to fetch
        """
        self.base_url = "https://jsonplaceholder.typicode.com"
        self.endpoint = endpoint
        self.item_id = item_id

    @property
    def name(self) -> str:
        item_info = f"/{self.item_id}" if self.item_id else ""
        return f"JSONPlaceholder API - /{self.endpoint}{item_info}"

    @property
    def provider_ctx(self) -> str:
        return f"Fetches {self.endpoint} data from JSONPlaceholder fake REST API for testing and prototyping."

    def run(self, limit: int = 5) -> str:
        """
        Fetch data from the API and format as markdown.
        
        Args:
            limit: Maximum number of items to return (ignored if item_id is set)
            
        Returns:
            Formatted markdown representation of the API response
        """
        # Build URL
        url = f"{self.base_url}/{self.endpoint}"
        if self.item_id:
            url += f"/{self.item_id}"

        try:
            # Make API request
            with urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            # Format the response
            if self.item_id:
                # Single item response
                return self._format_single_item(data)
            else:
                # List response - limit items
                items = data[:limit] if isinstance(data, list) else [data]
                return self._format_list(items)

        except HTTPError as e:
            return f"API Error {e.code}: {e.reason}"
        except URLError as e:
            return f"Network Error: {e.reason}"
        except Exception as e:
            return f"Error fetching data: {str(e)}"

    def _format_single_item(self, item: dict) -> str:
        """Format a single item as markdown."""
        lines = [f"## {self.endpoint.title()} Item {self.item_id}\n"]
        for key, value in item.items():
            # Truncate long values
            val_str = str(value)
            if len(val_str) > 100:
                val_str = val_str[:97] + "..."
            lines.append(f"- **{key}**: {val_str}")
        return "\n".join(lines)

    def _format_list(self, items: list[dict]) -> str:
        """Format a list of items as a markdown table."""
        if not items:
            return "No data found."

        # Get all unique keys from all items
        all_keys = set()
        for item in items:
            all_keys.update(item.keys())
        
        # Use first 4 most common keys for the table
        keys = list(all_keys)[:4]
        
        # Build table data
        headers = [key.title() for key in keys]
        rows = []
        for item in items:
            row = []
            for key in keys:
                value = item.get(key, "")
                # Truncate long values
                val_str = str(value)
                if len(val_str) > 50:
                    val_str = val_str[:47] + "..."
                row.append(val_str)
            rows.append(row)

        table = TableData.from_rows(headers, rows)
        return f"## {self.endpoint.title()} (showing {len(items)} items)\n\n{table.to_md()}"


# EXAMPLE 2: REST API with Custom Headers


class GitHubAPIProvider(BaseProvider[str]):
    """
    Fetches data from GitHub's public API.
    
    Example endpoints:
    - /users/{username} - User profile information
    - /repos/{owner}/{repo} - Repository details
    - /users/{username}/repos - User's repositories
    
    API docs: https://docs.github.com/en/rest
    """

    def __init__(self, endpoint: str, api_token: str | None = None):
        """
        Initialize GitHub API provider.
        
        Args:
            endpoint: GitHub API endpoint (e.g., "users/octocat")
            api_token: Optional GitHub personal access token for higher rate limits
        """
        self.base_url = "https://api.github.com"
        self.endpoint = endpoint.lstrip("/")
        self.api_token = api_token

    @property
    def name(self) -> str:
        return f"GitHub API - /{self.endpoint}"

    @property
    def provider_ctx(self) -> str:
        return f"Fetches data from GitHub REST API endpoint: {self.endpoint}"

    def run(self) -> str:
        """Fetch data from GitHub API and format as markdown."""
        url = f"{self.base_url}/{self.endpoint}"

        # Prepare headers
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Proompt-Example/1.0"
        }
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=10) as response:
                data = json.loads(response.read().decode())

            return self._format_github_data(data)

        except HTTPError as e:
            error_msg = e.read().decode() if e.fp else str(e)
            return f"GitHub API Error {e.code}: {error_msg}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _format_github_data(self, data: dict | list) -> str:
        """Format GitHub API response as markdown."""
        if isinstance(data, list):
            # Repository list or similar
            return self._format_list_response(data)
        else:
            # Single item (user, repo, etc.)
            return self._format_single_response(data)

    def _format_single_response(self, data: dict) -> str:
        """Format single GitHub resource."""
        # Common GitHub fields
        lines = ["## GitHub Resource\n"]
        
        important_fields = [
            "name", "full_name", "login", "description", "bio",
            "html_url", "public_repos", "followers", "following",
            "created_at", "updated_at", "language", "stargazers_count",
            "forks_count", "open_issues_count"
        ]
        
        for field in important_fields:
            if field in data:
                value = data[field]
                if value is not None:
                    lines.append(f"- **{field.replace('_', ' ').title()}**: {value}")
        
        return "\n".join(lines)

    def _format_list_response(self, data: list) -> str:
        """Format list of GitHub resources as table."""
        if not data:
            return "No items found."

        # Extract common fields for table
        common_fields = ["name", "description", "language", "stargazers_count", "forks_count"]
        headers = []
        for field in common_fields:
            if any(field in item for item in data):
                headers.append(field.replace("_", " ").title())
        
        if not headers:
            return f"Found {len(data)} items (structure varies)"

        # Build rows
        rows = []
        for item in data[:10]:  # Limit to 10 items
            row = []
            for field in [h.lower().replace(" ", "_") for h in headers]:
                value = item.get(field, "")
                val_str = str(value) if value is not None else ""
                if len(val_str) > 40:
                    val_str = val_str[:37] + "..."
                row.append(val_str)
            rows.append(row)

        table = TableData.from_rows(headers, rows)
        return f"## GitHub Resources (showing {len(rows)} of {len(data)})\n\n{table.to_md()}"


# EXAMPLE 3: Generic REST API Provider with Configuration


class RestAPIProvider(BaseProvider[Any]):
    """
    Generic REST API provider with flexible configuration.
    
    This is a template for building custom API providers.
    Supports:
    - Custom headers
    - Query parameters
    - Different HTTP methods
    - Response transformation
    """

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ):
        """
        Initialize a generic REST API provider.
        
        Args:
            url: Full API URL
            method: HTTP method (GET, POST, etc.)
            headers: Optional HTTP headers
            params: Optional query parameters
        """
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.params = params or {}

    @property
    def name(self) -> str:
        return f"REST API Provider - {self.url}"

    @property
    def provider_ctx(self) -> str:
        return f"Fetches data from {self.url} using {self.method} method"

    def run(self) -> Any:
        """Execute API request and return parsed response."""
        # Build URL with query parameters
        url = self.url
        if self.params:
            from urllib.parse import urlencode
            url += "?" + urlencode(self.params)

        try:
            request = Request(url, headers=self.headers, method=self.method)
            with urlopen(request, timeout=10) as response:
                content_type = response.headers.get("Content-Type", "")
                
                if "application/json" in content_type:
                    return json.loads(response.read().decode())
                else:
                    return response.read().decode()

        except HTTPError as e:
            return {"error": f"HTTP {e.code}", "message": str(e.reason)}
        except Exception as e:
            return {"error": "Request failed", "message": str(e)}


# USAGE EXAMPLE


def main():
    """Demonstrate API-based DataProviders."""
    
    print("🌐 API-Based DataProvider Examples")
    print("=" * 60)

    # Example 0: Mock API Provider (works without network)
    print("\n🎭 Example 0: Mock API Provider (No Network Required)")
    print("-" * 60)
    mock_users = MockAPIProvider("users")
    print(mock_users.run())

    print("\n\n🎭 Example 0b: Mock API - Products")
    print("-" * 60)
    mock_products = MockAPIProvider("products")
    print(mock_products.run())

    # Example 1: JSONPlaceholder API
    print("\n\n📝 Example 1: JSONPlaceholder API (Posts)")
    print("-" * 60)
    print("(Requires network access)")
    posts_provider = JSONPlaceholderProvider("posts")
    print(posts_provider.run(limit=3))

    print("\n\n📝 Example 2: JSONPlaceholder API (Single User)")
    print("-" * 60)
    print("(Requires network access)")
    user_provider = JSONPlaceholderProvider("users", item_id=1)
    print(user_provider.run())

    # Example 2: GitHub API
    print("\n\n🐙 Example 3: GitHub API (User Profile)")
    print("-" * 60)
    print("(Requires network access)")
    # Fetch GitHub user profile (no auth needed for public data)
    github_provider = GitHubAPIProvider("users/octocat")
    print(github_provider.run())

    print("\n\n🐙 Example 4: GitHub API (User Repositories)")
    print("-" * 60)
    print("(Requires network access)")
    repos_provider = GitHubAPIProvider("users/octocat/repos")
    print(repos_provider.run())

    # Example 3: Generic REST API
    print("\n\n🔧 Example 5: Generic REST API Provider")
    print("-" * 60)
    print("(Requires network access)")
    api_provider = RestAPIProvider(
        url="https://jsonplaceholder.typicode.com/posts/1",
        headers={"User-Agent": "Proompt-Example/1.0"}
    )
    result = api_provider.run()
    print(f"Fetched post: {result.get('title', 'N/A')}")
    print(f"Body preview: {str(result.get('body', ''))[:100]}...")

    # Summary
    print("\n\n" + "=" * 60)
    print("📊 Summary")
    print("-" * 60)
    print("✅ Demonstrated 4 API provider patterns:")
    print("   0. MockAPIProvider - Testing without network access")
    print("   1. JSONPlaceholderProvider - Simple REST API with formatting")
    print("   2. GitHubAPIProvider - API with custom headers and auth")
    print("   3. RestAPIProvider - Generic configurable API provider")
    print("\n💡 Key Takeaways:")
    print("   • Inherit from BaseProvider[T] where T is your return type")
    print("   • Implement name, provider_ctx, and run() methods")
    print("   • Add proper error handling for network requests")
    print("   • Transform API responses into LLM-friendly formats")
    print("   • Consider rate limiting and authentication in production")
    print("   • Use mock providers for testing and development")
    print("\n🔗 These providers can be used in PromptSections just like")
    print("   FileDataProvider, CsvDataProvider, etc.")
    print("\n📚 Example Usage in a PromptSection:")
    print("   section = PromptSection(")
    print("       context=my_context,")
    print("       tools=[tool1, tool2],")
    print("       MockAPIProvider('users'),  # or any other provider")
    print("   )")
    
    # Demonstration with actual PromptSection
    print("\n\n" + "=" * 60)
    print("🎯 Integration Example: API Provider in PromptSection")
    print("-" * 60)
    
    from proompt.base.prompt import PromptSection
    from proompt.base.context import Context
    
    class SimpleContext(Context):
        def render(self) -> str:
            return "Context: API data analysis for business intelligence"
    
    class DataAnalysisSection(PromptSection):
        def formatter(self) -> str:
            # Get data from all providers
            data_outputs = [provider.run() for provider in self.providers]
            combined_data = "\n\n".join(data_outputs)
            
            return f"""## Data Analysis Section
            
{combined_data}

Task: Analyze the above data and provide insights."""
        
        def render(self) -> str:
            return self.formatter()
    
    # Create section with mock API providers
    section = DataAnalysisSection(
        SimpleContext(),
        [],  # tools
        MockAPIProvider("users"),
        MockAPIProvider("products"),
    )
    
    print(section.render())
    print("\n✅ Successfully integrated API providers into PromptSection!")


if __name__ == "__main__":
    main()
