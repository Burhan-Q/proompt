#!/usr/bin/env python3
"""
Intermediate Proompt Example: Quarterly Business Review

This simplified example demonstrates key object-oriented prompt engineering concepts:
- 2 Custom DataProviders for different data sources
- 2 Custom PromptSections for different analysis perspectives
- Multiple analysis tools with proper documentation
- A complete custom Prompt that orchestrates everything
- Proper dedent usage for clean output and readable code

Simplified from the advanced example while maintaining core architectural concepts.
"""

import random
import statistics
from datetime import datetime
from textwrap import dedent, indent

from proompt.base.context import Context, ToolContext
from proompt.base.prompt import BasePrompt, PromptSection
from proompt.base.provider import BaseProvider

INDENT_12 = " " * 12

# CUSTOM DATA PROVIDERS


class MetricsAPIProvider(BaseProvider[dict]):
    """Simulates fetching business metrics from an API endpoint."""

    def __init__(self, quarter: str, department: str = "all"):
        self.quarter = quarter
        self.department = department

    @property
    def name(self) -> str:
        return f"Business Metrics API for {self.quarter} ({self.department})"

    @property
    def provider_ctx(self) -> str:
        return f"Fetches key business metrics for {self.quarter} from internal API."

    def run(self) -> dict:
        """Simulate API call and return business metrics as structured data."""
        return {
            "quarter": self.quarter,
            "revenue": random.randint(2500000, 3500000),
            "user_growth_rate": round(random.uniform(0.08, 0.25), 3),
            "active_users": random.randint(125000, 180000),
            "churn_rate": round(random.uniform(0.02, 0.08), 3),
            "net_promoter_score": random.randint(65, 85),
            "server_uptime": round(random.uniform(0.995, 0.999), 4),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }


class LogAnalysisProvider(BaseProvider[str]):
    """Analyzes system logs to extract performance insights."""

    def __init__(self, log_period: str, service_name: str = "web-api"):
        self.log_period = log_period
        self.service_name = service_name

    @property
    def name(self) -> str:
        return f"Log Analysis for {self.service_name} ({self.log_period})"

    @property
    def provider_ctx(self) -> str:
        return f"Analyzes {self.service_name} service logs over {self.log_period}."

    def run(self) -> str:
        """Analyze logs and return performance summary."""
        error_types = ["Authentication Error", "Database Timeout", "Rate Limit Exceeded", "Service Unavailable"]

        analysis = {
            "period": self.log_period,
            "service": self.service_name,
            "total_requests": random.randint(2500000, 4200000),
            "error_rate": round(random.uniform(0.005, 0.025), 4),
            "avg_response_time": random.randint(125, 350),
            "peak_requests_per_second": random.randint(850, 1500),
            "top_errors": [(error, random.randint(12, 156)) for error in random.sample(error_types, 2)],
        }

        # Create detailed log analysis report with proper indentation for dedent
        error_details = "\n".join([f"- **{error}:** {count} occurrences" for error, count in analysis["top_errors"]])
        error_details = indent(error_details, INDENT_12)

        return dedent(f"""\
            ## System Performance Analysis - {self.log_period}
            **Service:** {self.service_name}

            ### Request Volume & Performance
            - **Total Requests:** {analysis["total_requests"]:,}
            - **Average Response Time:** {analysis["avg_response_time"]}ms
            - **Peak Load:** {analysis["peak_requests_per_second"]} req/sec
            - **Error Rate:** {analysis["error_rate"]:.2%}

            ### Error Analysis:\n{error_details}

            ### Performance Summary
            System handled {analysis["total_requests"]:,} requests with {analysis["error_rate"]:.2%} error rate.
            Response times averaged {analysis["avg_response_time"]}ms within acceptable SLA bounds.
            """).strip()


# ANALYSIS TOOLS


def calculate_trend_analysis(current_value: float, previous_value: float, periods: int = 4) -> dict[str, float | str]:
    """Calculate trend metrics including growth rate and projections."""
    growth_rate = (current_value - previous_value) / previous_value if previous_value != 0 else 0
    projected_value = current_value * (1 + growth_rate) ** periods

    return {
        "growth_rate": growth_rate,
        "projected_value": projected_value,
        "trend_direction": "increasing" if growth_rate > 0 else "decreasing",
    }


def generate_statistical_summary(data_points: list[float]) -> dict[str, float | str]:
    """Generate statistical summary of data points."""
    if not data_points:
        return {"error": "No data points provided"}

    return {
        "mean": statistics.mean(data_points),
        "median": statistics.median(data_points),
        "std_dev": statistics.stdev(data_points) if len(data_points) > 1 else 0,
        "count": len(data_points),
    }


# BUSINESS CONTEXT


class BusinessContext(Context):
    """Context for quarterly business review with company and period information."""

    def __init__(self, company_name: str, quarter: str, year: int):
        self.company_name = company_name
        self.quarter = quarter
        self.year = year
        self.review_date = datetime.now().strftime("%Y-%m-%d")

    def render(self) -> str:
        return dedent(f"""\
            Business Review Context:
            Company: {self.company_name}
            Review Period: {self.quarter} {self.year}
            Analysis Date: {self.review_date}
            
            This analysis combines operational metrics and technical performance data 
            to provide comprehensive insights for strategic decision making.
            """).strip()


# CUSTOM PROMPT SECTIONS


class ExecutiveSummarySection(PromptSection):
    """Creates executive-level summary focused on key business outcomes."""

    def _format_metrics_data(self, metrics: dict) -> str:
        """Format metrics dictionary into a readable report."""
        return dedent(f"""\
            ## Business Metrics Report - {metrics["quarter"]}
            **Generated:** {metrics["generated_at"]}

            ### Key Metrics
            - **Revenue:** ${metrics["revenue"]:,}
            - **User Growth Rate:** {metrics["user_growth_rate"]:.1%}
            - **Active Users:** {metrics["active_users"]:,}
            - **Churn Rate:** {metrics["churn_rate"]:.1%}
            - **Net Promoter Score:** {metrics["net_promoter_score"]}
            - **Server Uptime:** {metrics["server_uptime"]:.1%}""").strip()

    def formatter(self, focus_areas: list[str] | None = None) -> str:
        focus_areas = focus_areas or ["revenue", "growth", "performance"]

        # Collect data from providers - only handle MetricsAPIProvider
        formatted_data = []
        for provider in self.providers:
            if isinstance(provider, MetricsAPIProvider):
                metrics = provider.run()
                formatted_data.append(self._format_metrics_data(metrics))

        # Ensure consistent indentation for dedent to work properly
        data = "\n\n".join(formatted_data)
        data = indent(data, INDENT_12)
        tools_desc = ", ".join(tool.tool_name for tool in self.tools)
        tools_desc = indent(tools_desc, INDENT_12)
        focus_list = "\n".join(f"• {area}" for area in focus_areas)
        focus_list = indent(focus_list, INDENT_12)

        return dedent(f"""\
            ## EXECUTIVE SUMMARY ANALYSIS

            You are conducting a quarterly executive briefing for senior leadership. Focus on high-level 
            business impact, actionable insights, and recommendations for next quarter.

            ### Key Focus Areas:\n{focus_list}

            ### Available Data Sources:\n{data}

            ### Analysis Tools Available:\n{tools_desc}

            Provide an executive summary with critical findings and strategic actions.""").strip()

    def render(self) -> str:
        return self.formatter()


class TechnicalAnalysisSection(PromptSection):
    """Detailed technical performance analysis for engineering and operations teams."""

    def _format_metrics_data(self, metrics: dict) -> str:
        """Format metrics dictionary into a readable report."""
        return dedent(f"""\
            ## Business Metrics - {metrics["quarter"]}
            ### Key Metrics
            - **Revenue:** ${metrics["revenue"]:,}
            - **Active Users:** {metrics["active_users"]:,}
            - **Server Uptime:** {metrics["server_uptime"]:.1%}""").strip()

    def formatter(self, metrics_focus: list[str] | None = None) -> str:
        metrics_focus = metrics_focus or ["performance", "reliability", "scalability"]

        # Collect data from providers - handle specific provider types
        formatted_data = []
        for provider in self.providers:
            if isinstance(provider, MetricsAPIProvider):
                metrics = provider.run()
                formatted_data.append(self._format_metrics_data(metrics))
            elif isinstance(provider, LogAnalysisProvider):
                log_report = provider.run()
                formatted_data.append(log_report)

        # Ensure consistent indentation for dedent to work properly
        data = "\n\n".join(indent(fd, INDENT_12) for fd in formatted_data)
        tools_info = "\n".join(indent(f"- {tool.tool_name}: {tool.tool_description}", INDENT_12) for tool in self.tools)
        metrics_scope = "\n".join(indent(f"• {metric.title()}", INDENT_12) for metric in metrics_focus)

        return dedent(f"""\
            ## TECHNICAL PERFORMANCE DEEP DIVE

            Conduct a comprehensive technical analysis focusing on system performance and operational excellence.

            ### Technical Analysis Scope:\n{metrics_scope}

            ### System Data Available:\n{data}

            ### Analysis Capabilities:\n{tools_info}

            Provide technical assessment covering performance metrics, reliability, and operational efficiency.
            Use quantitative analysis and provide specific recommendations.""").strip()

    def render(self) -> str:
        return self.formatter()


# FULL CUSTOM PROMPT


class QuarterlyReviewPrompt(BasePrompt):
    """Comprehensive quarterly business review prompt combining all analysis sections."""

    def __init__(self, company_name: str, quarter: str, year: int, *sections: PromptSection):
        super().__init__(*sections)
        self.company_name = company_name
        self.quarter = quarter
        self.year = year
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def render(self) -> str:
        sections_content = "\n\n" + "=" * 60 + "\n\n".join(section.render() for section in self.sections)

        header = dedent(f"""\
            # QUARTERLY BUSINESS REVIEW: {self.company_name}
            ## {self.quarter} {self.year} Analysis

            **Generated:** {self.generated_at}
            **Analysis Type:** Multi-dimensional Business Intelligence Review

            This quarterly review integrates business metrics and technical performance data to provide 
            actionable insights for strategic decision-making.

            Please analyze all provided data sources thoroughly and deliver insights that are data-driven, 
            actionable, and aligned with business objectives.""").strip()

        footer = dedent(f"""\

            {"=" * 60}

            ## ANALYSIS FRAMEWORK SUMMARY

            This prompt demonstrates object-oriented prompt engineering by:
            - **Integrating Multiple Data Sources**: Business APIs and system logs
            - **Applying Specialized Analysis Tools**: Statistical analysis and trend calculation
            - **Structuring Analysis**: Executive and technical perspectives
            - **Ensuring Consistency**: Standardized data formats and analysis approaches

            **Total Data Providers:** {len([p for section in self.sections for p in section.providers if p is not None])}
            **Analysis Tools:** {len([t for section in self.sections for t in section.tools])}
            **Report Sections:** {len(self.sections)}""").strip()

        return header + sections_content + footer


# EXAMPLE EXECUTION


def main():
    """Demonstrate the intermediate quarterly review prompt system."""

    print("🚀 Proompt Intermediate Example: Quarterly Business Review")
    print("=" * 55)

    # Initialize data providers
    print("\n📊 Initializing Data Providers...")
    metrics_provider = MetricsAPIProvider("Q3 2024", "engineering")
    logs_provider = LogAnalysisProvider("September 2024", "web-api")

    # Initialize analysis tools
    print("🔧 Setting up Analysis Tools...")
    trend_tool = ToolContext(calculate_trend_analysis)
    stats_tool = ToolContext(generate_statistical_summary)

    # Create business context
    business_context = BusinessContext("TechCorp Solutions", "Q3", 2024)

    # Create prompt sections with providers and tools
    print("📝 Building Prompt Sections...")

    executive_section = ExecutiveSummarySection(business_context, [trend_tool, stats_tool], metrics_provider)

    technical_section = TechnicalAnalysisSection(business_context, [stats_tool], logs_provider, metrics_provider)

    # Create the complete quarterly review prompt
    print("🎯 Assembling Complete Quarterly Review...")
    quarterly_prompt = QuarterlyReviewPrompt("TechCorp Solutions", "Q3", 2024, executive_section, technical_section)

    # Render and display the final prompt
    print("\n" + "=" * 60)
    print("GENERATED QUARTERLY REVIEW PROMPT")
    print("=" * 60)

    final_prompt = quarterly_prompt.render()
    print(final_prompt)

    print("\n\n📈 Prompt Statistics:")
    print(f"   • Total Characters: {len(final_prompt):,}")
    print(f"   • Total Words: {len(final_prompt.split()):,}")
    print("   • Data Sources: 2 custom providers (dict, str)")
    print("   • Analysis Tools: 2 statistical functions")
    print("   • Prompt Sections: 2 specialized sections")
    print("   • Context Integration: Business-specific context")

    print("\n✅ Complete! This intermediate example demonstrates core object-oriented")
    print("   prompt engineering concepts in a simplified, digestible format.")
    print("   🔄 Clean provider type checking and proper dedent usage!")


if __name__ == "__main__":
    main()
