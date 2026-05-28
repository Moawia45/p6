"""
ConstructMind AI - Gemini AI Service
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Service class wrapping Google Gemini API for:
- BOQ analysis and classification
- Activity generation from project descriptions
- Duration estimation assistance
- Delay analysis
- Report generation

Uses the official google-genai SDK.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from google import genai

from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Wrapper around the Google Gemini generative AI API.
    Provides construction-domain-specific AI methods.
    """

    def __init__(self) -> None:
        """Initialize the Gemini client with the configured API key."""
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. Gemini features will be unavailable.")
            self._client = None
        else:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self._model = settings.GEMINI_MODEL

    @property
    def is_available(self) -> bool:
        """Check if the Gemini service is configured and available."""
        return self._client is not None

    def _ensure_available(self) -> None:
        """Raise an error if the service is not configured."""
        if not self.is_available:
            raise RuntimeError(
                "Gemini AI service is not available. Please set GEMINI_API_KEY in your environment."
            )

    async def _generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.7,
        max_tokens: int = 8192,
    ) -> str:
        """
        Core generation method that calls the Gemini API.

        Args:
            prompt: The user prompt / question.
            system_instruction: Optional system instruction for context.
            temperature: Sampling temperature (0.0 – 1.0).
            max_tokens: Maximum output tokens.

        Returns:
            Generated text response.
        """
        self._ensure_available()

        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

            response = self._client.models.generate_content(
                model=self._model,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )
            return response.text or ""

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"Gemini AI generation failed: {e}") from e

    async def _generate_json(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.4,
    ) -> Any:
        """
        Generate content and parse the result as JSON.
        Instructs Gemini to return valid JSON only.
        """
        json_instruction = (
            "IMPORTANT: Respond with valid JSON only. No markdown code fences, "
            "no explanatory text, no backticks. Just raw JSON."
        )
        combined_system = f"{system_instruction}\n\n{json_instruction}" if system_instruction else json_instruction

        raw = await self._generate(
            prompt=prompt,
            system_instruction=combined_system,
            temperature=temperature,
        )

        # Strip any markdown fences that Gemini might still add
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove opening fence
            first_newline = cleaned.index("\n") if "\n" in cleaned else 3
            cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {e}\nRaw: {raw[:500]}")
            raise ValueError(f"Gemini returned invalid JSON: {e}") from e

    # ═══════════════════════════════════════════════════════════════
    # BOQ ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    async def analyze_boq(self, boq_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze Bill of Quantities items using Gemini AI.

        Classifies each item into CSI categories, validates quantities,
        identifies missing items, and provides cost insights.

        Args:
            boq_items: List of BOQ item dicts with item_no, description,
                       quantity, unit, unit_rate, total_amount.

        Returns:
            Analysis dict with categorized_items, missing_items,
            cost_observations, and summary.
        """
        system_instruction = """You are a senior construction quantity surveyor and cost engineer.
Analyze the following Bill of Quantities (BOQ) items from a construction project.

For each item:
1. Assign the most appropriate CSI MasterFormat division code and category name.
2. Validate if the quantity and unit seem reasonable for the description.
3. Flag any potential issues (unusual rates, missing items, duplicates).

Also provide:
- A list of commonly missing BOQ items for this type of project.
- Cost observations and optimization suggestions.
- An overall summary assessment."""

        prompt = f"""Analyze these BOQ items and return a JSON object with this structure:
{{
    "categorized_items": [
        {{
            "item_no": "string",
            "description": "string",
            "csi_code": "string (e.g., 03 30 00)",
            "csi_category": "string (e.g., Cast-in-Place Concrete)",
            "validation_status": "ok|warning|error",
            "validation_notes": "string",
            "suggested_unit_rate_range": {{"min": 0, "max": 0, "currency": "PKR"}}
        }}
    ],
    "missing_items": [
        {{
            "description": "string",
            "csi_code": "string",
            "reason": "string"
        }}
    ],
    "cost_observations": ["string"],
    "summary": {{
        "total_items": 0,
        "total_amount": 0,
        "items_with_warnings": 0,
        "completeness_score": 0.0
    }}
}}

BOQ Items:
{json.dumps(boq_items, indent=2, default=str)}"""

        return await self._generate_json(prompt, system_instruction)

    # ═══════════════════════════════════════════════════════════════
    # ACTIVITY GENERATION
    # ═══════════════════════════════════════════════════════════════

    async def generate_activities(
        self,
        project_description: str,
        project_type: str = "building",
        detail_level: str = "detailed",
        boq_items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a complete activity list with WBS structure and dependencies
        from a project description and/or BOQ items.

        Args:
            project_description: Textual description of the project.
            project_type: Type of construction project.
            detail_level: summary / detailed / comprehensive.
            boq_items: Optional BOQ items to derive activities from.

        Returns:
            Dict with wbs, activities, and relationships arrays.
        """
        system_instruction = f"""You are an expert construction planner and scheduler (Primavera P6 / MS Project specialist).
Generate a complete Work Breakdown Structure (WBS) and activity list for a {project_type} construction project.

Detail level: {detail_level}
- summary: Top-level activities only (20-30 activities)
- detailed: Standard scheduling detail (50-100 activities)
- comprehensive: Full CPM-level detail (100-200 activities)

Include realistic:
1. WBS hierarchy (up to 3 levels)
2. Activities with IDs (like A1010, A1020, etc.)
3. Logical relationships (predecessors/successors)
4. Estimated durations in days
5. Activity types (task, milestone, summary)"""

        boq_context = ""
        if boq_items:
            boq_context = f"\n\nBOQ Items for reference:\n{json.dumps(boq_items[:50], indent=2, default=str)}"

        prompt = f"""Generate a complete project plan and return a JSON object with this structure:
{{
    "wbs": [
        {{
            "code": "1.0",
            "name": "string",
            "level": 1,
            "parent_code": null
        }}
    ],
    "activities": [
        {{
            "activity_id": "A1010",
            "name": "string",
            "description": "string",
            "activity_type": "task",
            "wbs_code": "1.1",
            "original_duration": 5,
            "duration_unit": "days",
            "quantity": 0,
            "unit": "m³"
        }}
    ],
    "relationships": [
        {{
            "predecessor_activity_id": "A1010",
            "successor_activity_id": "A1020",
            "relationship_type": "FS",
            "lag_days": 0
        }}
    ],
    "ai_notes": "string with key assumptions and notes"
}}

Project Description: {project_description}
Project Type: {project_type}{boq_context}"""

        return await self._generate_json(prompt, system_instruction, temperature=0.5)

    # ═══════════════════════════════════════════════════════════════
    # DURATION ESTIMATION
    # ═══════════════════════════════════════════════════════════════

    async def estimate_durations(
        self,
        activities: List[Dict[str, Any]],
        project_context: str = "",
        mode: str = "realistic",
    ) -> List[Dict[str, Any]]:
        """
        Use AI to estimate or refine activity durations based on
        quantities, productivity rates, and project context.

        Args:
            activities: List of activity dicts with name, quantity, unit.
            project_context: Additional project context.
            mode: aggressive / realistic / conservative.

        Returns:
            List of dicts with activity_id and estimated_duration.
        """
        system_instruction = f"""You are a construction scheduling expert specializing in duration estimation.
Estimation mode: {mode}
- aggressive: Optimistic, best-case scenario with experienced crews and ideal conditions
- realistic: Most likely scenario based on typical productivity
- conservative: Pessimistic, accounts for common delays and learning curves

Consider Pakistan/South Asian construction conditions, typical crew sizes, and equipment availability."""

        prompt = f"""Estimate durations for these activities and return a JSON array:
[
    {{
        "activity_id": "string",
        "estimated_duration_days": 0,
        "productivity_rate": "description of assumed productivity",
        "crew_size": "assumed crew composition",
        "assumptions": "key assumptions",
        "confidence": 0.0 to 1.0
    }}
]

Project Context: {project_context}

Activities:
{json.dumps(activities, indent=2, default=str)}"""

        return await self._generate_json(prompt, system_instruction)

    # ═══════════════════════════════════════════════════════════════
    # DELAY ANALYSIS
    # ═══════════════════════════════════════════════════════════════

    async def analyze_delays(
        self,
        project_data: Dict[str, Any],
        critical_path: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze project schedule for potential delays and provide
        root cause analysis and recovery recommendations.

        Args:
            project_data: Project metadata and activity list.
            critical_path: List of critical path activity IDs.

        Returns:
            Analysis dict with delay_analysis, root_causes,
            recovery_plan, and risk_assessment.
        """
        system_instruction = """You are a construction delay analysis expert familiar with:
- AACE (Association for the Advancement of Cost Engineering) delay analysis methods
- As-Planned vs As-Built analysis
- Time Impact Analysis (TIA)
- Windows Analysis

Provide professional-grade delay analysis suitable for construction claims."""

        prompt = f"""Analyze this project for delays and return JSON:
{{
    "delay_analysis": {{
        "total_delay_days": 0,
        "excusable_delays": [],
        "non_excusable_delays": [],
        "concurrent_delays": []
    }},
    "root_causes": [
        {{
            "cause": "string",
            "category": "owner|contractor|third_party|force_majeure",
            "impact_days": 0,
            "affected_activities": []
        }}
    ],
    "recovery_plan": [
        {{
            "action": "string",
            "expected_recovery_days": 0,
            "cost_impact": 0,
            "feasibility": "high|medium|low"
        }}
    ],
    "risk_assessment": {{
        "current_risk_level": "low|medium|high|critical",
        "completion_probability": 0.0,
        "recommended_actions": []
    }}
}}

Project Data:
{json.dumps(project_data, indent=2, default=str)}

Critical Path Activities: {json.dumps(critical_path)}"""

        return await self._generate_json(prompt, system_instruction)

    # ═══════════════════════════════════════════════════════════════
    # REPORT GENERATION
    # ═══════════════════════════════════════════════════════════════

    async def generate_report(
        self,
        project_data: Dict[str, Any],
        report_type: str = "progress",
    ) -> Dict[str, Any]:
        """
        Generate a professional construction project report.

        Args:
            project_data: Complete project data including activities,
                         resources, BOQ, baselines, and risks.
            report_type: progress / delay_analysis / cost / risk / executive_summary.

        Returns:
            Report dict with title, sections, recommendations.
        """
        report_templates = {
            "progress": "Weekly/Monthly Progress Report with SPI/CPI metrics",
            "delay_analysis": "Forensic Delay Analysis Report",
            "cost": "Cost Performance Report with EVM metrics (BCWS, BCWP, ACWP)",
            "risk": "Risk Assessment and Mitigation Report",
            "executive_summary": "Executive Summary Dashboard Report",
        }

        report_desc = report_templates.get(report_type, report_templates["progress"])

        system_instruction = f"""You are a construction project controls engineer generating a {report_desc}.
Follow professional report writing standards. Include:
- Executive summary
- Data-driven analysis with specific numbers
- Graphical data suggestions (chart types and data)
- Professional recommendations
- Next period forecast

Report format should be suitable for client presentation."""

        prompt = f"""Generate a {report_type} report and return JSON:
{{
    "title": "string",
    "report_date": "YYYY-MM-DD",
    "executive_summary": "string",
    "sections": [
        {{
            "title": "string",
            "content": "string (markdown formatted)",
            "charts": [
                {{
                    "type": "bar|line|pie|gantt",
                    "title": "string",
                    "data": {{}}
                }}
            ]
        }}
    ],
    "key_metrics": {{
        "spi": 0.0,
        "cpi": 0.0,
        "percent_complete": 0.0,
        "days_ahead_behind": 0,
        "budget_variance": 0.0
    }},
    "recommendations": ["string"],
    "risks_and_issues": ["string"],
    "next_period_forecast": "string"
}}

Project Data:
{json.dumps(project_data, indent=2, default=str)}"""

        return await self._generate_json(prompt, system_instruction, temperature=0.5)


# ── Singleton Instance ───────────────────────────────────────────
gemini_service = GeminiService()
