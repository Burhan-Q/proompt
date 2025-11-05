#!/usr/bin/env python3
"""
Pydantic-AI Tools Integration Example

This example demonstrates how to use pydantic-ai Tool and FunctionToolset objects
with proompt's PromptSection. It shows:
- Creating pydantic-ai Tool objects
- Creating a FunctionToolset
- Mixing ToolContext and pydantic-ai tools
- Using tools in a PromptSection
"""

from textwrap import dedent, indent

from pydantic_ai import FunctionToolset, RunContext, Tool

from proompt.base.context import ToolContext
from proompt.base.prompt import BasePrompt, PromptSection

# ===== DEFINE SOME TOOLS USING PYDANTIC-AI =====


def search_documents(query: str, max_results: int = 5) -> str:
    """Search through company documents."""
    return f"Found {max_results} documents matching '{query}'"


def get_company_metrics(metric_type: str) -> dict:
    """Retrieve company metrics."""
    return {"revenue": 1000000, "users": 50000, "growth": 0.15}


def calculate_percentage(numerator: float, denominator: float) -> float:
    """Calculate percentage from two numbers."""
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100


# Create pydantic-ai Tool objects
search_tool = Tool(search_documents, takes_ctx=False)
metrics_tool = Tool(get_company_metrics, takes_ctx=False)
calc_tool = Tool(calculate_percentage, takes_ctx=False)

# Create a FunctionToolset
analysis_toolset = FunctionToolset(tools=[search_tool, metrics_tool])


# You can also add tools using the decorator
@analysis_toolset.tool
def summarize_data(ctx: RunContext, data: str) -> str:
    """Summarize the provided data."""
    return f"Summary of {len(data)} characters of data"


# ===== DEFINE A TRADITIONAL PROOMPT TOOL =====


def format_report(data: dict) -> str:
    """Format data into a readable report."""
    return "\n".join(f"{k}: {v}" for k, v in data.items())


proompt_tool = ToolContext(format_report)


# ===== CREATE A PROMPT SECTION WITH MIXED TOOLS =====


class AnalysisSection(PromptSection):
    """A section that uses both proompt and pydantic-ai tools."""

    def formatter(self) -> str:
        tools_list = "\n" + "\n".join(f"- {tool.tool_name}: {tool.tool_description}" for tool in self.tools)
        return dedent(f"""\
            ## ANALYSIS TOOLS
            
            You have access to the following tools:
            {indent(tools_list, " " * 12)}
            
            Use these tools to gather and analyze data for your report.
            """).strip()

    def render(self) -> str:
        return self.formatter()


# ===== CREATE THE PROMPT =====


class MixedToolsPrompt(BasePrompt):
    """Example prompt using both proompt and pydantic-ai tools."""

    def render(self) -> str:
        return "\n\n".join(section.render() for section in self.sections)


# ===== DEMONSTRATE THE INTEGRATION =====


def main():
    print("=" * 80)
    print("Pydantic-AI Tools Integration Demo")
    print("=" * 80)
    print()

    # Method 1: Pass individual pydantic-ai Tool objects
    print("Method 1: Individual Tool objects")
    print("-" * 80)
    section1 = AnalysisSection(tools=[search_tool, metrics_tool, calc_tool])
    print(f"Tools in section: {len(section1.tools)}")
    print()

    # Method 2: Pass a FunctionToolset (tools are extracted automatically)
    print("Method 2: FunctionToolset")
    print("-" * 80)
    section2 = AnalysisSection(tools=[analysis_toolset])
    print(f"Tools in section: {len(section2.tools)}")
    print("Tool names:", [t.tool_name for t in section2.tools])
    print()

    # Method 3: Mix ToolContext and pydantic-ai tools
    print("Method 3: Mixed tools (ToolContext + pydantic-ai Tool + FunctionToolset)")
    print("-" * 80)
    section3 = AnalysisSection(
        tools=[
            proompt_tool,  # Traditional proompt tool
            calc_tool,  # Individual pydantic-ai Tool
            analysis_toolset,  # FunctionToolset (extracts multiple tools)
        ]
    )
    print(f"Tools in section: {len(section3.tools)}")
    print("Tool names:", [t.tool_name for t in section3.tools])
    print()

    # Create a full prompt
    print("Full Prompt Output:")
    print("=" * 80)
    prompt = MixedToolsPrompt(section3)
    print(prompt.render())
    print()

    # Demonstrate add_tools method
    print("Using add_tools method:")
    print("-" * 80)
    section4 = AnalysisSection()
    print(f"Initial tools: {len(section4.tools)}")

    section4.add_tools(proompt_tool)
    print(f"After adding ToolContext: {len(section4.tools)}")

    section4.add_tools(search_tool, metrics_tool)
    print(f"After adding pydantic-ai Tools: {len(section4.tools)}")

    section4.add_tools(analysis_toolset)
    print(f"After adding FunctionToolset: {len(section4.tools)}")

    print("Final tool names:", [t.tool_name for t in section4.tools])
    print()

    # Show tool rendering
    print("Individual Tool Rendering:")
    print("=" * 80)
    for tool in section3.tools[:3]:  # Show first 3 tools
        print(f"\n{tool.tool_name}:")
        print("-" * 40)
        print(tool.render())


if __name__ == "__main__":
    main()
