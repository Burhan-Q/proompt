#!/usr/bin/env python3
"""
Advanced Proompt Example: Quarterly Business Performance Analysis

This example demonstrates the power of object-oriented prompt engineering by creating
a comprehensive quarterly business review prompt that combines multiple data sources,
custom analysis tools, and structured reporting sections.

The example showcases:
- 3 Custom DataProviders for different data sources
- 3 Custom PromptSections for different analysis perspectives
- Multiple analysis tools with proper documentation
- A complete custom Prompt that orchestrates everything
- Real-world business intelligence use case
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
        return f"Fetches key business metrics for {self.quarter} from internal API, including revenue, user growth, and operational KPIs for {self.department} department(s)."

    def run(self) -> dict:
        """Simulate API call and return business metrics as structured data."""
        # Simulate API data returned
        return {
            "quarter": self.quarter,
            "department": self.department,
            "revenue": random.randint(2500000, 3500000),
            "user_growth_rate": round(random.uniform(0.08, 0.25), 3),
            "customer_acquisition_cost": random.randint(45, 85),
            "monthly_recurring_revenue": random.randint(800000, 1200000),
            "churn_rate": round(random.uniform(0.02, 0.08), 3),
            "net_promoter_score": random.randint(65, 85),
            "active_users": random.randint(125000, 180000),
            "conversion_rate": round(random.uniform(0.12, 0.28), 3),
            "server_uptime": round(random.uniform(0.995, 0.999), 4),
            "support_ticket_resolution_time": round(random.uniform(2.1, 4.8), 1),
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
        return f"Analyzes {self.service_name} service logs over {self.log_period} to extract performance metrics, error rates, and usage patterns."

    def run(self) -> str:
        """Analyze logs and return performance summary."""
        # Simulate log analysis results
        error_types = [
            "Authentication Error",
            "Database Timeout",
            "Rate Limit Exceeded",
            "Service Unavailable",
            "Invalid Request",
        ]

        analysis = {
            "period": self.log_period,
            "service": self.service_name,
            "total_requests": random.randint(2500000, 4200000),
            "error_rate": round(random.uniform(0.005, 0.025), 4),
            "avg_response_time": random.randint(125, 350),
            "peak_requests_per_second": random.randint(850, 1500),
            "top_errors": [(error, random.randint(12, 156)) for error in random.sample(error_types, 3)],
        }

        # Create detailed log analysis report with proper indentation
        error_details = "\n".join([f"- **{error}:** {count} occurrences" for error, count in analysis["top_errors"]])
        error_details = indent(error_details, INDENT_12)

        report = dedent(f"""\
            ## System Performance Analysis - {self.log_period}
            **Service:** {self.service_name}
            **Analysis Period:** {self.log_period}

            ### Request Volume & Performance
            - **Total Requests Processed:** {analysis["total_requests"]:,}
            - **Average Response Time:** {analysis["avg_response_time"]}ms
            - **Peak Load:** {analysis["peak_requests_per_second"]} req/sec
            - **Overall Error Rate:** {analysis["error_rate"]:.2%}

            ### Error Analysis:\n{error_details}

            ### Performance Insights
            - System handled {analysis["total_requests"]:,} requests with {analysis["error_rate"]:.2%} error rate
            - Response times averaged {analysis["avg_response_time"]}ms, within acceptable SLA bounds
            - Peak load of {analysis["peak_requests_per_second"]} req/sec indicates strong capacity utilization
            """).strip()

        return report


class MarketDataProvider(BaseProvider[list[dict]]):
    """Provides competitive market analysis and industry benchmarks."""

    def __init__(self, industry: str, region: str = "North America"):
        self.industry = industry
        self.region = region

    @property
    def name(self) -> str:
        return f"Market Analysis for {self.industry} in {self.region}"

    @property
    def provider_ctx(self) -> str:
        return f"Provides competitive benchmarking and market trend analysis for {self.industry} sector in {self.region}, including industry averages and competitor positioning."

    def run(self) -> list[dict]:
        """Generate market analysis data as structured competitor list."""
        # Simulate market research data
        competitors = ["CompetitorA", "CompetitorB", "CompetitorC", "CompetitorD"]

        # Return structured market data as a list of dictionaries
        market_analysis = []

        # Add our company data
        our_data = {
            "company": "Our Company",
            "market_share": round(random.uniform(0.03, 0.12), 3),
            "revenue_estimate": random.randint(180, 350),  # millions
            "employee_count": random.randint(800, 1500),
            "founded_year": 2018,
            "primary_focus": "AI-Powered Analytics",
            "growth_rate": round(random.uniform(0.15, 0.35), 3),
            "funding_round": "Series C",
            "is_public": False,
            "industry": self.industry,
            "region": self.region,
        }
        market_analysis.append(our_data)

        # Add competitor data
        for i, comp in enumerate(competitors[:4]):
            competitor_data = {
                "company": comp,
                "market_share": round(random.uniform(0.02, 0.15), 3),
                "revenue_estimate": random.randint(200, 800),  # millions
                "employee_count": random.randint(500, 3000),
                "founded_year": random.randint(2010, 2020),
                "primary_focus": random.choice(
                    [
                        "Enterprise Software",
                        "Cloud Infrastructure",
                        "Data Analytics",
                        "SaaS Platforms",
                        "AI/ML Solutions",
                    ]
                ),
                "growth_rate": round(random.uniform(0.08, 0.25), 3),
                "funding_round": random.choice(["Series A", "Series B", "Series C", "IPO", "Private"]),
                "is_public": random.choice([True, False]),
                "industry": self.industry,
                "region": self.region,
            }
            market_analysis.append(competitor_data)

        # Add market overview metadata as the last entry
        market_overview = {
            "company": "_MARKET_OVERVIEW_",
            "total_market_size": random.randint(15, 45),  # billions
            "industry_growth_rate": round(random.uniform(0.06, 0.18), 3),
            "industry_avg_churn": round(random.uniform(0.04, 0.09), 3),
            "industry_avg_nps": random.randint(58, 74),
            "major_trends": ["AI/ML Integration", "Cloud Migration", "Data Privacy Focus", "Remote Work Solutions"],
            "industry": self.industry,
            "region": self.region,
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        }
        market_analysis.append(market_overview)

        return market_analysis


# ANALYSIS TOOLS


def calculate_trend_analysis(current_value: float, previous_value: float, periods: int = 4) -> dict[str, float | str]:
    """
    Calculate trend metrics including growth rate, momentum, and projections.

    Args:
        current_value: Current period value
        previous_value: Previous period value
        periods: Number of periods for projection

    Returns:
        Dictionary with trend analysis metrics
    """
    growth_rate = (current_value - previous_value) / previous_value if previous_value != 0 else 0
    momentum_score = min(abs(growth_rate) * 10, 10)  # Scale 0-10
    projected_value = current_value * (1 + growth_rate) ** periods

    return {
        "growth_rate": growth_rate,
        "momentum_score": momentum_score,
        "projected_value": projected_value,
        "trend_direction": "increasing" if growth_rate > 0 else "decreasing",
    }


def assess_risk_factors(metrics: dict[str, float], thresholds: dict[str, float] | None = None) -> dict[str, str]:
    """
    Assess business risk factors based on key metrics.

    Args:
        metrics: Dictionary of business metrics
        thresholds: Custom risk thresholds (optional)

    Returns:
        Risk assessment with recommendations
    """
    default_thresholds = {"churn_rate": 0.05, "error_rate": 0.02, "growth_rate": 0.10}
    thresholds = thresholds or default_thresholds

    risks = {}

    # Assess churn risk
    churn = metrics.get("churn_rate", 0)
    if churn > thresholds["churn_rate"]:
        risks["customer_retention"] = (
            f"HIGH - Churn rate of {churn:.1%} exceeds {thresholds['churn_rate']:.1%} threshold"
        )
    else:
        risks["customer_retention"] = f"LOW - Churn rate of {churn:.1%} is within acceptable range"

    # Assess technical risk
    error_rate = metrics.get("error_rate", 0)
    if error_rate > thresholds["error_rate"]:
        risks["technical_stability"] = f"MEDIUM - Error rate of {error_rate:.2%} requires monitoring"
    else:
        risks["technical_stability"] = f"LOW - Error rate of {error_rate:.2%} is acceptable"

    return risks


def generate_statistical_summary(data_points: list[float]) -> dict[str, float | str]:
    """
    Generate comprehensive statistical summary of data points.

    Args:
        data_points: List of numerical values

    Returns:
        Statistical summary including mean, median, std dev, etc.
    """
    if not data_points:
        return {"error": "No data points provided"}

    return {
        "mean": statistics.mean(data_points),
        "median": statistics.median(data_points),
        "std_dev": statistics.stdev(data_points) if len(data_points) > 1 else 0,
        "min_value": min(data_points),
        "max_value": max(data_points),
        "range": max(data_points) - min(data_points),
        "count": len(data_points),
    }


# BUSINESS CONTEXT


class BusinessContext(Context):
    """Context for quarterly business review with company and period information."""

    def __init__(self, company_name: str, quarter: str, year: int, analyst_name: str = "AI Assistant"):
        self.company_name = company_name
        self.quarter = quarter
        self.year = year
        self.analyst_name = analyst_name
        self.review_date = datetime.now().strftime("%Y-%m-%d")

    def render(self) -> str:
        return dedent(f"""\
            Business Review Context:
            Company: {self.company_name}
            Review Period: {self.quarter} {self.year}
            Analysis Date: {self.review_date}
            Analyst: {self.analyst_name}
            
            This analysis combines operational metrics, technical performance data, and market intelligence 
            to provide comprehensive insights for strategic decision making.
            """).strip()


# CUSTOM PROMPT SECTIONS


class ExecutiveSummarySection(PromptSection):
    """Creates executive-level summary focused on key business outcomes."""

    def _format_metrics_data(self, metrics: dict) -> str:
        """Format metrics dictionary into a readable report."""
        return dedent(f"""\
            ## Business Metrics Report - {metrics["quarter"]}
            **Department Scope:** {metrics["department"]}
            **Generated:** {metrics["generated_at"]}

            ### Financial Performance
            - **Revenue:** ${metrics["revenue"]:,}
            - **Monthly Recurring Revenue:** ${metrics["monthly_recurring_revenue"]:,}
            - **Customer Acquisition Cost:** ${metrics["customer_acquisition_cost"]}

            ### Growth & Engagement  
            - **User Growth Rate:** {metrics["user_growth_rate"]:.1%}
            - **Active Users:** {metrics["active_users"]:,}
            - **Conversion Rate:** {metrics["conversion_rate"]:.1%}
            - **Churn Rate:** {metrics["churn_rate"]:.1%}

            ### Operational Excellence
            - **Net Promoter Score:** {metrics["net_promoter_score"]}
            - **Server Uptime:** {metrics["server_uptime"]:.1%}
            - **Avg Support Resolution:** {metrics["support_ticket_resolution_time"]} hours""").strip()

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
        focus_list = "\n".join(f"• {area}" for area in focus_areas)
        focus_list = indent(focus_list, INDENT_12)

        return dedent(f"""\
            ## EXECUTIVE SUMMARY ANALYSIS

            You are conducting a quarterly executive briefing for senior leadership. Your analysis should be:
            - **Strategic**: Focus on high-level business impact and strategic implications
            - **Concise**: Summarize complex data into actionable insights
            - **Forward-looking**: Include trends and recommendations for next quarter

            ### Key Focus Areas:\n{focus_list}

            ### Available Data Sources:\n{data}

            ### Analysis Tools Available:
            {tools_desc}

            Please provide an executive summary that highlights the most critical findings, identifies key trends, and recommends strategic actions. Structure your response with clear sections for Performance Highlights, Key Challenges, and Strategic Recommendations.""").strip()

    def render(self) -> str:
        return self.formatter()


class TechnicalAnalysisSection(PromptSection):
    """Detailed technical performance analysis for engineering and operations teams."""

    def _format_metrics_data(self, metrics: dict) -> str:
        """Format metrics dictionary into a readable report."""
        return dedent(f"""\
            ## Business Metrics Report - {metrics["quarter"]}
            **Department Scope:** {metrics["department"]}
            **Generated:** {metrics["generated_at"]}

            ### Financial Performance
            - **Revenue:** ${metrics["revenue"]:,}
            - **Monthly Recurring Revenue:** ${metrics["monthly_recurring_revenue"]:,}
            - **Customer Acquisition Cost:** ${metrics["customer_acquisition_cost"]}

            ### Growth & Engagement  
            - **User Growth Rate:** {metrics["user_growth_rate"]:.1%}
            - **Active Users:** {metrics["active_users"]:,}
            - **Conversion Rate:** {metrics["conversion_rate"]:.1%}
            - **Churn Rate:** {metrics["churn_rate"]:.1%}

            ### Operational Excellence
            - **Net Promoter Score:** {metrics["net_promoter_score"]}
            - **Server Uptime:** {metrics["server_uptime"]:.1%}
            - **Avg Support Resolution:** {metrics["support_ticket_resolution_time"]} hours""").strip()

    def formatter(self, metrics_focus: list[str] | None = None) -> str:
        metrics_focus = metrics_focus or ["performance", "reliability", "scalability", "efficiency"]

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
        data = "\n\n".join(formatted_data)
        data = indent(data, INDENT_12)
        tools_info = "\n".join(f"- {tool.tool_name}: {tool.tool_description}" for tool in self.tools)
        tools_info = indent(tools_info, INDENT_12)
        metrics_scope = "\n".join(f"• {metric.title()}" for metric in metrics_focus)
        metrics_scope = indent(metrics_scope, INDENT_12)

        return dedent(f"""\
            ## TECHNICAL PERFORMANCE DEEP DIVE

            Conduct a comprehensive technical analysis focusing on system performance, reliability, and operational excellence. This analysis will inform technical roadmap decisions and infrastructure planning.

            ### Technical Analysis Scope:\n{metrics_scope}

            ### System Data Available:\n{data}

            ### Analysis Capabilities:\n{tools_info}

            Provide a detailed technical assessment covering:
            1. **Performance Metrics Analysis**: Response times, throughput, error rates
            2. **Reliability Assessment**: Uptime, failure patterns, recovery times  
            3. **Scalability Review**: Capacity utilization, bottlenecks, growth readiness
            4. **Operational Efficiency**: Resource utilization, cost optimization opportunities
            5. **Technical Risk Assessment**: Security, stability, and maintenance concerns
            6. **Infrastructure Recommendations**: Improvements for next quarter

            Use quantitative analysis where possible and provide specific technical recommendations.""").strip()

    def render(self) -> str:
        return self.formatter()


class RecommendationsSection(PromptSection):
    """Strategic recommendations and action items based on comprehensive analysis."""

    def _format_metrics_data(self, metrics: dict) -> str:
        """Format metrics dictionary into a readable report."""
        return dedent(f"""\
            ## Business Metrics Report - {metrics["quarter"]}
            **Department Scope:** {metrics["department"]}
            **Generated:** {metrics["generated_at"]}

            ### Financial Performance
            - **Revenue:** ${metrics["revenue"]:,}
            - **Monthly Recurring Revenue:** ${metrics["monthly_recurring_revenue"]:,}
            - **Customer Acquisition Cost:** ${metrics["customer_acquisition_cost"]}

            ### Growth & Engagement  
            - **User Growth Rate:** {metrics["user_growth_rate"]:.1%}
            - **Active Users:** {metrics["active_users"]:,}
            - **Conversion Rate:** {metrics["conversion_rate"]:.1%}
            - **Churn Rate:** {metrics["churn_rate"]:.1%}

            ### Operational Excellence
            - **Net Promoter Score:** {metrics["net_promoter_score"]}
            - **Server Uptime:** {metrics["server_uptime"]:.1%}
            - **Avg Support Resolution:** {metrics["support_ticket_resolution_time"]} hours""").strip()

    def formatter(self, time_horizon: str = "next quarter") -> str:
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
        data = "\n\n".join(formatted_data)
        data = indent(data, INDENT_12)
        available_tools = [f"• {tool.tool_name} (for {tool.tool_description.lower()})" for tool in self.tools]
        tools_list = "\n".join(available_tools)
        tools_list = indent(tools_list, INDENT_12)

        return dedent(f"""\
            ## STRATEGIC RECOMMENDATIONS & ACTION PLANNING

            Based on the comprehensive analysis of business metrics and technical performance data, provide actionable recommendations for {time_horizon}. Your recommendations should be:

            - **Prioritized**: Rank by impact and feasibility
            - **Specific**: Include concrete actions and success metrics
            - **Resource-aware**: Consider implementation complexity and requirements
            - **Measurable**: Define clear KPIs for tracking progress

            ### Data Foundation:\n{data}

            ### Analysis Tools Used:\n{tools_list}

            Structure your recommendations as follows:

            ### 1. HIGH PRIORITY ACTIONS (Immediate - 30 days)
            Identify 3-5 critical actions that need immediate attention

            ### 2. STRATEGIC INITIATIVES (Medium term - 90 days)  
            Outline 3-4 strategic projects for the quarter

            ### 3. LONG-TERM INVESTMENTS (6+ months)
            Suggest 2-3 major initiatives for future planning

            ### 4. RISK MITIGATION
            Address identified risks with specific mitigation strategies

            ### 5. SUCCESS METRICS
            Define measurable KPIs for tracking progress on each recommendation

            For each recommendation, include:
            - **Rationale**: Why this action is needed
            - **Expected Impact**: Quantified benefits where possible
            - **Implementation Complexity**: Low/Medium/High
            - **Resource Requirements**: Team/budget/time estimates
            - **Success Criteria**: How to measure success""").strip()

    def render(self) -> str:
        return self.formatter()


class CompetitiveAnalysisSection(PromptSection):
    """Specialized section for competitive intelligence and market positioning analysis."""

    def _format_market_data(self, market_data: list[dict]) -> str:
        """Format detailed competitive analysis from market data."""
        # Find market overview data
        market_overview = next((item for item in market_data if item.get("company") == "_MARKET_OVERVIEW_"), {})
        our_company = next((item for item in market_data if item.get("company") == "Our Company"), {})
        competitors = [item for item in market_data if item.get("company") not in ["_MARKET_OVERVIEW_", "Our Company"]]

        # Sort competitors by market share
        competitors.sort(key=lambda x: x.get("market_share", 0), reverse=True)

        # Detailed competitor analysis
        competitor_analysis = []
        for comp in competitors:
            analysis = dedent(f"""\
                ### {comp["company"]}
                - **Market Share:** {comp["market_share"]:.1%}
                - **Revenue:** ${comp["revenue_estimate"]}M (estimated)
                - **Employees:** {comp["employee_count"]:,}
                - **Founded:** {comp["founded_year"]}
                - **Focus:** {comp["primary_focus"]}
                - **Growth Rate:** {comp["growth_rate"]:.1%}
                - **Status:** {"Public" if comp["is_public"] else "Private"} ({comp["funding_round"]})""").strip()
            competitor_analysis.append(analysis)

        competitor_details = "\n\n".join(competitor_analysis)

        # Format major trends
        trends = market_overview.get("major_trends", [])
        trends_analysis = "\n".join([f"- **{trend}:** Key driver of market evolution" for trend in trends])

        # Ensure consistent indentation for dedent to work properly
        competitor_details = indent(competitor_details, INDENT_12)
        trends_analysis = indent(trends_analysis, INDENT_12)

        return dedent(f"""\
            ## Comprehensive Competitive Intelligence Report
            **Industry:** {market_overview.get("industry", "Unknown")}
            **Region:** {market_overview.get("region", "Unknown")}
            **Analysis Date:** {market_overview.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))}

            ### Market Landscape Overview
            - **Total Addressable Market:** ${market_overview.get("total_market_size", 0)}B annually
            - **Market Growth Rate:** {market_overview.get("industry_growth_rate", 0):.1%} year-over-year
            - **Industry Maturity:** {"Mature" if market_overview.get("industry_growth_rate", 0) < 0.10 else "Growth Stage"}
            - **Competitive Intensity:** {"High" if len(competitors) > 3 else "Moderate"}

            ### Our Position
            - **Market Share:** {our_company.get("market_share", 0):.1%}
            - **Revenue:** ${our_company.get("revenue_estimate", 0)}M
            - **Employees:** {our_company.get("employee_count", 0):,}
            - **Growth Rate:** {our_company.get("growth_rate", 0):.1%}
            - **Competitive Advantage:** {our_company.get("primary_focus", "AI-Powered Analytics")}

            ### Detailed Competitor Analysis:\n{competitor_details}

            ### Market Trends & Drivers:\n{trends_analysis}

            ### Competitive Positioning Insights
            - **Market Leaders:** {", ".join([comp["company"] for comp in competitors[:2]])}
            - **Growth Champions:** {", ".join([comp["company"] for comp in competitors if comp.get("growth_rate", 0) > 0.20])}
            - **Public Companies:** {", ".join([comp["company"] for comp in competitors if comp.get("is_public")])}
            - **Funding Leaders:** {", ".join([comp["company"] for comp in competitors if comp.get("funding_round") in ["Series C", "IPO"]])}""").strip()

    def formatter(self, analysis_focus: list[str] | None = None) -> str:
        analysis_focus = analysis_focus or [
            "market positioning",
            "competitive threats",
            "growth opportunities",
            "differentiation",
        ]

        # Collect data from providers - handle specific provider types
        formatted_data = []
        for provider in self.providers:
            if isinstance(provider, MarketDataProvider):
                market_data = provider.run()
                formatted_data.append(self._format_market_data(market_data))
            elif isinstance(provider, MetricsAPIProvider):
                metrics = provider.run()
                formatted_data.append(
                    f"**{metrics.get('quarter', 'Current Period')} Metrics:** Revenue ${metrics.get('revenue', 0):,}, Growth {metrics.get('user_growth_rate', 0):.1%}"
                )

        # Ensure consistent indentation for dedent to work properly
        data = "\n\n".join(formatted_data)
        data = indent(data, INDENT_12)
        tools_desc = ", ".join(tool.tool_name for tool in self.tools)
        focus_list = "\n".join(f"• {area}" for area in analysis_focus)
        focus_list = indent(focus_list, INDENT_12)

        return dedent(f"""\
            ## COMPETITIVE INTELLIGENCE & MARKET POSITIONING ANALYSIS

            You are conducting a comprehensive competitive analysis for strategic planning. Your analysis should be:
            - **Data-Driven**: Use quantitative metrics to support positioning decisions
            - **Strategic**: Identify competitive advantages and vulnerabilities
            - **Actionable**: Provide clear recommendations for competitive response
            - **Forward-Looking**: Anticipate market shifts and competitor moves

            ### Analysis Focus Areas:
{focus_list}

            ### Competitive Intelligence Data:
{data}

            ### Analysis Tools Available:
            {tools_desc}

            Provide a detailed competitive analysis covering:

            ### 1. COMPETITIVE POSITIONING
            Analyze our market position relative to key competitors

            ### 2. THREAT ASSESSMENT  
            Identify immediate and emerging competitive threats

            ### 3. OPPORTUNITY ANALYSIS
            Highlight market gaps and growth opportunities

            ### 4. DIFFERENTIATION STRATEGY
            Recommend how to strengthen competitive advantages

            ### 5. COMPETITIVE RESPONSE PLAN
            Outline tactical responses to competitor actions

            ### 6. MARKET INTELLIGENCE PRIORITIES
            Identify key metrics and competitors to monitor closely""").strip()

    def render(self) -> str:
        return self.formatter()


# CUSTOM PROMPT


class QuarterlyReviewPrompt(BasePrompt):
    """Comprehensive quarterly business review prompt combining all analysis sections."""

    def __init__(self, company_name: str, quarter: str, year: int, *sections: PromptSection):
        super().__init__(*sections)
        self.company_name = company_name
        self.quarter = quarter
        self.year = year
        self.generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def render(self) -> str:
        sections_content = "\n\n" + "=" * 80 + "\n\n".join(section.render() for section in self.sections)

        header = dedent(f"""\
            # QUARTERLY BUSINESS REVIEW: {self.company_name}
            ## {self.quarter} {self.year} Comprehensive Analysis

            **Generated:** {self.generated_at}
            **Analysis Type:** Multi-dimensional Business Intelligence Review
            **Scope:** Operational Performance, Technical Metrics, Market Position

            ---

            This comprehensive quarterly review integrates business metrics, technical performance data, and competitive market intelligence to provide actionable insights for strategic decision-making. The analysis is structured in three complementary sections: Executive Summary for leadership decisions, Technical Deep Dive for operational excellence, and Strategic Recommendations for forward planning.

            Please analyze all provided data sources thoroughly and deliver insights that are data-driven, actionable, and aligned with business objectives. Consider both short-term tactical adjustments and long-term strategic positioning in your analysis.""").strip()

        footer = dedent(f"""\

            {"=" * 80}

            ## ANALYSIS FRAMEWORK SUMMARY

            This prompt leverages the power of object-oriented prompt engineering to:
            - **Integrate Multiple Data Sources**: Business APIs, system logs, and market research
            - **Apply Specialized Analysis Tools**: Statistical analysis, trend calculation, and risk assessment
            - **Structure Complex Analysis**: Executive, technical, and strategic perspectives
            - **Ensure Consistency**: Standardized data formats and analysis approaches
            - **Enable Reusability**: Modular components for different business contexts

            The modular design allows for easy customization of data sources, analysis tools, and reporting sections while maintaining analytical rigor and consistency across quarterly reviews.

            **Total Data Providers:** {len([p for section in self.sections for p in section.providers if p is not None])}
            **Analysis Tools:** {len([t for section in self.sections for t in section.tools])}
            **Report Sections:** {len(self.sections)}""").strip()

        return header + sections_content + footer


# EXAMPLE EXECUTION


def main():
    """Demonstrate the complete quarterly review prompt system."""

    print("🚀 Proompt Advanced Example: Quarterly Business Review")
    print("=" * 60)

    # Initialize data providers
    print("\n📊 Initializing Data Providers...")
    metrics_provider = MetricsAPIProvider("Q3 2024", "engineering")
    logs_provider = LogAnalysisProvider("September 2024", "web-api")
    market_provider = MarketDataProvider("SaaS Technology", "North America")

    # Initialize analysis tools
    print("🔧 Setting up Analysis Tools...")
    trend_tool = ToolContext(calculate_trend_analysis)
    risk_tool = ToolContext(assess_risk_factors)
    stats_tool = ToolContext(generate_statistical_summary)

    # Create business context
    business_context = BusinessContext("TechCorp Solutions", "Q3", 2024, "Senior Data Analyst")

    # Create prompt sections with providers and tools
    print("📝 Building Prompt Sections...")

    executive_section = ExecutiveSummarySection(business_context, [trend_tool, stats_tool], metrics_provider)

    technical_section = TechnicalAnalysisSection(
        business_context, [stats_tool, risk_tool], logs_provider, metrics_provider
    )

    competitive_section = CompetitiveAnalysisSection(
        business_context, [trend_tool, stats_tool], market_provider, metrics_provider
    )

    recommendations_section = RecommendationsSection(
        business_context, [trend_tool, risk_tool, stats_tool], metrics_provider, logs_provider
    )

    # Create the complete quarterly review prompt
    print("🎯 Assembling Complete Quarterly Review...")
    quarterly_prompt = QuarterlyReviewPrompt(
        "TechCorp Solutions",
        "Q3",
        2024,
        executive_section,
        technical_section,
        competitive_section,
        recommendations_section,
    )

    # Render and display the final prompt
    print("\n" + "=" * 80)
    print("GENERATED QUARTERLY REVIEW PROMPT")
    print("=" * 80)

    final_prompt = quarterly_prompt.render()
    print(final_prompt)

    print("\n\n📈 Prompt Statistics:")
    print(f"   • Total Characters: {len(final_prompt):,}")
    print(f"   • Total Words: {len(final_prompt.split()):,}")
    print("   • Data Sources: 3 custom providers (dict, str, list[dict])")
    print("   • Analysis Tools: 3 statistical functions")
    print("   • Prompt Sections: 4 specialized sections")
    print("   • Context Integration: Business-specific context")

    print("\n✅ Complete! This prompt demonstrates the power of object-oriented")
    print("   prompt engineering for complex, multi-dimensional business analysis.")
    print("   🔄 SIMPLIFIED: Clean provider type checking and focused data responsibility!")
    print("   📊 Market data is now exclusively handled by CompetitiveAnalysisSection")


if __name__ == "__main__":
    main()
