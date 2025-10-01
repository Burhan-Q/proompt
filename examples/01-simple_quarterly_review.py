#!/usr/bin/env python3
"""
Simple Proompt Example: Basic Quarterly Review

This simplified example demonstrates core prompt engineering concepts:
- 1 Custom DataProvider for business metrics
- 1 Custom PromptSection for analysis
- Basic analysis tool
- Complete custom Prompt
- Proper dedent usage for clean output
"""

import random
from textwrap import dedent, indent

from proompt.base.context import Context, ToolContext
from proompt.base.prompt import BasePrompt, PromptSection
from proompt.base.provider import BaseProvider

INDENT_12 = " " * 12

# CUSTOM DATA PROVIDER


class SimpleMetricsProvider(BaseProvider[dict]):
    """Fetches basic business metrics."""

    def __init__(self, quarter: str):
        self.quarter = quarter

    @property
    def name(self) -> str:
        return f"Metrics for {self.quarter}"

    @property
    def provider_ctx(self) -> str:
        return f"Basic business metrics for {self.quarter}."

    def run(self) -> dict:
        """Return basic business metrics."""
        return {
            "quarter": self.quarter,
            "revenue": random.randint(1000000, 2000000),
            "users": random.randint(50000, 100000),
            "growth": round(random.uniform(0.05, 0.15), 3),
        }


# ANALYSIS TOOL


def calculate_growth_rate(current: float, previous: float) -> dict[str, str]:
    """Calculate simple growth rate."""
    if previous == 0:
        return {"growth_rate": "N/A", "trend": "new"}
    
    rate = (current - previous) / previous
    trend = "up" if rate > 0 else "down"
    return {"growth_rate": f"{rate:.1%}", "trend": trend}


# BUSINESS CONTEXT


class SimpleContext(Context):
    """Basic context for quarterly review."""

    def __init__(self, company: str, quarter: str):
        self.company = company
        self.quarter = quarter

    def render(self) -> str:
        return dedent(f"""\
            Review Context:
            Company: {self.company}
            Period: {self.quarter}
            
            Basic quarterly analysis for key business metrics.
            """).strip()


# PROMPT SECTION


class MetricsSection(PromptSection):
    """Basic metrics analysis section."""

    def _format_data(self, metrics: dict) -> str:
        """Format metrics into readable report."""
        return dedent(f"""\
            ## Metrics Report - {metrics["quarter"]}
            - **Revenue:** ${metrics["revenue"]:,}
            - **Users:** {metrics["users"]:,}
            - **Growth:** {metrics["growth"]:.1%}""").strip()

    def formatter(self) -> str:
        # Get data from provider
        formatted_data = []
        for provider in self.providers:
            if isinstance(provider, SimpleMetricsProvider):
                metrics = provider.run()
                formatted_data.append(self._format_data(metrics))

        # Format with proper indentation
        data = "\n\n".join(formatted_data)
        data = indent(data, INDENT_12)
        
        tools_desc = ", ".join(tool.tool_name for tool in self.tools)
        tools_desc = indent(tools_desc, INDENT_12)

        return dedent(f"""\
            ## QUARTERLY METRICS ANALYSIS

            Analyze the quarterly business performance focusing on key metrics and trends.

            ### Available Data:\n{data}

            ### Analysis Tools:\n{tools_desc}

            Provide insights and recommendations based on the metrics.""").strip()

    def render(self) -> str:
        return self.formatter()


# CUSTOM PROMPT


class SimpleQuarterlyPrompt(BasePrompt):
    """Simple quarterly review prompt."""

    def __init__(self, company: str, quarter: str, *sections: PromptSection):
        super().__init__(*sections)
        self.company = company
        self.quarter = quarter

    def render(self) -> str:
        sections_content = "\n\n" + "=" * 40 + "\n\n".join(section.render() for section in self.sections)

        header = dedent(f"""\
            # QUARTERLY REVIEW: {self.company}
            ## {self.quarter} Analysis

            Simple quarterly business review focusing on core metrics.

            Analyze the data and provide actionable insights for business growth.""").strip()

        footer = dedent(f"""\

            {"=" * 40}

            ## SUMMARY

            This demonstrates basic prompt engineering with:
            - 1 Data Provider
            - 1 Analysis Tool  
            - 1 Prompt Section
            - Structured Output""").strip()

        return header + sections_content + footer


# EXAMPLE EXECUTION


def main():
    """Demonstrate the simple quarterly review."""
    
    print("🚀 Simple Quarterly Review Example")
    print("=" * 35)

    # Initialize components
    metrics_provider = SimpleMetricsProvider("Q3 2024")
    growth_tool = ToolContext(calculate_growth_rate)
    context = SimpleContext("StartupCorp", "Q3 2024")

    # Create section and prompt
    metrics_section = MetricsSection(context, [growth_tool], metrics_provider)
    prompt = SimpleQuarterlyPrompt("StartupCorp", "Q3 2024", metrics_section)

    # Display result
    print("\nGenerated Prompt:")
    print("=" * 40)
    final_prompt = prompt.render()
    print(final_prompt)

    print(f"\n📊 Stats: {len(final_prompt):,} chars, {len(final_prompt.split()):,} words")


if __name__ == "__main__":
    main()