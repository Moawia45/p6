"""
ConstructMind AI - Duration Calculation Engine
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Duration estimation service that:
- Loads productivity rates from the JSON database
- Calculates activity durations based on quantity, crew size, productivity
- Supports Aggressive / Realistic / Conservative estimation modes
- Applies adjustment factors for weather, overtime, and site constraints
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Path to the productivity rates JSON database
PRODUCTIVITY_RATES_PATH = Path(__file__).parent.parent / "data" / "productivity_rates.json"


class DurationEngine:
    """
    Calculates activity durations from quantities and productivity rates.
    Uses the comprehensive productivity rates database.
    """

    # Mode multipliers applied to the typical rate
    MODE_MULTIPLIERS = {
        "aggressive": {
            "rate_key": "max_rate",       # Use maximum productivity
            "safety_factor": 0.90,        # Minimal safety margin
            "description": "Best-case with experienced crews and ideal conditions",
        },
        "realistic": {
            "rate_key": "typical_rate",   # Use typical productivity
            "safety_factor": 1.00,        # Standard estimation
            "description": "Most likely scenario based on average conditions",
        },
        "conservative": {
            "rate_key": "min_rate",       # Use minimum productivity
            "safety_factor": 1.15,        # 15% safety margin
            "description": "Pessimistic with allowance for delays and learning curve",
        },
    }

    def __init__(self) -> None:
        """Load the productivity rates database."""
        self._rates: Dict[str, Dict[str, Any]] = {}
        self._rates_list: List[Dict[str, Any]] = []
        self._load_rates()

    def _load_rates(self) -> None:
        """Load productivity rates from the JSON file."""
        try:
            if not PRODUCTIVITY_RATES_PATH.exists():
                logger.warning(f"Productivity rates file not found: {PRODUCTIVITY_RATES_PATH}")
                return

            with open(PRODUCTIVITY_RATES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._rates_list = data.get("productivity_rates", [])
            # Index by ID for quick lookup
            for rate in self._rates_list:
                self._rates[rate["id"]] = rate

            logger.info(f"Loaded {len(self._rates)} productivity rates.")

        except Exception as e:
            logger.error(f"Error loading productivity rates: {e}")

    @property
    def rates(self) -> Dict[str, Dict[str, Any]]:
        """Access the loaded productivity rates dictionary."""
        return self._rates

    @property
    def rates_list(self) -> List[Dict[str, Any]]:
        """Access the loaded productivity rates as a list."""
        return self._rates_list

    def get_rate(self, rate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific productivity rate by its ID.

        Args:
            rate_id: The productivity rate ID (e.g., "BRK-001").

        Returns:
            The rate dict or None if not found.
        """
        return self._rates.get(rate_id)

    def search_rates(
        self,
        trade: Optional[str] = None,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search productivity rates by trade, category, or keyword.

        Args:
            trade: Filter by trade name (e.g., "Masonry").
            category: Filter by CSI category (e.g., "CSI-04").
            keyword: Search keyword in activity description.

        Returns:
            List of matching rate dicts.
        """
        results = self._rates_list

        if trade:
            results = [r for r in results if r.get("trade", "").lower() == trade.lower()]

        if category:
            results = [r for r in results if r.get("category", "").upper() == category.upper()]

        if keyword:
            kw = keyword.lower()
            results = [r for r in results if kw in r.get("activity", "").lower()]

        return results

    def calculate_duration(
        self,
        quantity: float,
        rate_id: str,
        mode: str = "realistic",
        crew_count: int = 1,
        weather_factor: float = 1.0,
        overtime_hours: float = 0.0,
        site_constraint_factor: float = 1.0,
        hours_per_day: float = 8.0,
    ) -> Dict[str, Any]:
        """
        Calculate the duration for an activity based on quantity and productivity.

        Args:
            quantity: Total quantity of work (in the rate's unit).
            rate_id: ID of the productivity rate to use.
            mode: "aggressive", "realistic", or "conservative".
            crew_count: Number of crews working in parallel.
            weather_factor: Weather adjustment (1.0 = normal, 0.7 = bad weather).
            overtime_hours: Additional hours per day beyond standard.
            site_constraint_factor: Site difficulty (1.0 = normal, 1.3 = congested).
            hours_per_day: Standard working hours per day.

        Returns:
            Dict with calculated duration, rate used, and breakdown.
        """
        rate_data = self.get_rate(rate_id)
        if not rate_data:
            return {
                "duration_days": 0,
                "error": f"Productivity rate '{rate_id}' not found.",
                "rate_used": None,
            }

        mode_config = self.MODE_MULTIPLIERS.get(mode, self.MODE_MULTIPLIERS["realistic"])
        rate_key = mode_config["rate_key"]
        safety_factor = mode_config["safety_factor"]

        # Get the base productivity rate for the selected mode
        base_rate = rate_data.get(rate_key, rate_data.get("typical_rate", 1))
        if base_rate <= 0:
            base_rate = rate_data.get("typical_rate", 1)

        # ── Apply adjustment factors ─────────────────────────────
        # Weather factor from the rate's own data
        rate_weather = rate_data.get("factors", {}).get("weather_impact", 1.0)
        effective_weather = min(weather_factor, rate_weather)

        # Site constraint factor
        effective_constraint = max(site_constraint_factor, 1.0)

        # Effective daily production per crew
        effective_rate = base_rate * effective_weather / effective_constraint

        # Overtime adjustment: additional hours increase daily output proportionally
        overtime_multiplier = 1.0
        if overtime_hours > 0 and hours_per_day > 0:
            # Overtime productivity is typically 85% of regular time
            overtime_efficiency = 0.85
            overtime_multiplier = 1 + (overtime_hours / hours_per_day) * overtime_efficiency

        effective_rate *= overtime_multiplier

        # Multi-crew parallelism
        total_daily_output = effective_rate * max(crew_count, 1)

        # ── Calculate raw duration ───────────────────────────────
        if total_daily_output <= 0:
            raw_duration = float("inf")
        else:
            raw_duration = quantity / total_daily_output

        # Apply safety factor
        adjusted_duration = raw_duration * safety_factor

        # Round up to nearest half-day (minimum 0.5 days)
        final_duration = max(0.5, math.ceil(adjusted_duration * 2) / 2)

        # ── Build result ─────────────────────────────────────────
        return {
            "duration_days": final_duration,
            "raw_duration_days": round(raw_duration, 2),
            "mode": mode,
            "rate_id": rate_id,
            "rate_description": rate_data.get("activity", ""),
            "rate_unit": rate_data.get("unit", ""),
            "base_rate": base_rate,
            "effective_rate_per_crew": round(effective_rate, 2),
            "total_daily_output": round(total_daily_output, 2),
            "quantity": quantity,
            "crew_count": crew_count,
            "crew_composition": rate_data.get("crew_composition", {}),
            "adjustments": {
                "weather_factor": effective_weather,
                "overtime_multiplier": round(overtime_multiplier, 3),
                "site_constraint_factor": effective_constraint,
                "safety_factor": safety_factor,
            },
            "notes": rate_data.get("notes", ""),
            "error": None,
        }

    def calculate_duration_auto(
        self,
        activity_name: str,
        quantity: float,
        unit: str,
        mode: str = "realistic",
        crew_count: int = 1,
        weather_factor: float = 1.0,
        overtime_hours: float = 0.0,
        site_constraint_factor: float = 1.0,
        hours_per_day: float = 8.0,
    ) -> Dict[str, Any]:
        """
        Auto-match an activity to a productivity rate and calculate duration.
        Uses keyword matching on the activity name.

        Args:
            activity_name: Name/description of the activity.
            quantity: Quantity of work.
            unit: Unit of measure.
            mode: Estimation mode.
            crew_count: Number of crews.
            weather_factor: Weather adjustment.
            overtime_hours: Daily overtime hours.
            site_constraint_factor: Site difficulty.
            hours_per_day: Standard hours per day.

        Returns:
            Duration calculation result with auto-matched rate.
        """
        # Keyword-based matching
        name_lower = activity_name.lower()
        best_match: Optional[Dict[str, Any]] = None
        best_score = 0

        for rate in self._rates_list:
            score = 0
            rate_activity = rate.get("activity", "").lower()
            rate_trade = rate.get("trade", "").lower()

            # Check for keyword overlap
            rate_words = set(rate_activity.split())
            name_words = set(name_lower.split())
            common = rate_words & name_words
            score = len(common)

            # Bonus for trade name match
            if rate_trade in name_lower:
                score += 3

            # Bonus for unit match
            rate_unit = rate.get("unit", "").lower()
            if unit and unit.lower() in rate_unit:
                score += 2

            # Common construction keywords
            keywords = {
                "brick": ["brick", "brickwork", "masonry"],
                "plaster": ["plaster", "plastering", "rendering"],
                "tile": ["tile", "tiling", "ceramic"],
                "paint": ["paint", "painting", "emulsion"],
                "concrete": ["concrete", "pouring", "casting", "rcc"],
                "rebar": ["rebar", "reinforcement", "bar bending", "steel fixing"],
                "formwork": ["formwork", "shuttering", "scaffolding"],
                "excavation": ["excavation", "excavate", "digging", "earthwork"],
                "asphalt": ["asphalt", "paving", "bituminous"],
                "steel": ["steel", "erection", "structural steel"],
                "electrical": ["electrical", "conduit", "wiring"],
                "plumbing": ["plumbing", "piping", "drainage"],
                "hvac": ["hvac", "duct", "air conditioning"],
                "waterproof": ["waterproof", "waterproofing", "membrane"],
                "ceiling": ["ceiling", "suspended ceiling", "false ceiling"],
                "drywall": ["drywall", "gypsum", "partition"],
                "flooring": ["floor", "flooring", "vinyl", "marble", "epoxy"],
                "roofing": ["roof", "roofing", "metal sheet"],
                "insulation": ["insulation", "thermal", "insulate"],
                "demolition": ["demolition", "demolish", "breaking"],
            }

            for kw_group, kw_list in keywords.items():
                name_has = any(k in name_lower for k in kw_list)
                rate_has = any(k in rate_activity for k in kw_list)
                if name_has and rate_has:
                    score += 5

            if score > best_score:
                best_score = score
                best_match = rate

        if best_match and best_score >= 2:
            result = self.calculate_duration(
                quantity=quantity,
                rate_id=best_match["id"],
                mode=mode,
                crew_count=crew_count,
                weather_factor=weather_factor,
                overtime_hours=overtime_hours,
                site_constraint_factor=site_constraint_factor,
                hours_per_day=hours_per_day,
            )
            result["auto_matched"] = True
            result["match_confidence"] = min(1.0, best_score / 10.0)
            return result
        else:
            return {
                "duration_days": 0,
                "auto_matched": False,
                "match_confidence": 0,
                "error": f"Could not auto-match activity '{activity_name}' to a productivity rate.",
                "suggestion": "Please manually assign a productivity rate ID.",
                "available_trades": list({r["trade"] for r in self._rates_list}),
            }

    def bulk_calculate(
        self,
        activities: List[Dict[str, Any]],
        mode: str = "realistic",
        weather_factor: float = 1.0,
        overtime_hours: float = 0.0,
        site_constraint_factor: float = 1.0,
        hours_per_day: float = 8.0,
    ) -> List[Dict[str, Any]]:
        """
        Calculate durations for multiple activities at once.

        Each activity dict should have:
        - activity_id: str
        - name: str
        - quantity: float
        - unit: str
        - productivity_rate_id: Optional[str] (if known)
        - crew_count: Optional[int] (default 1)

        Args:
            activities: List of activity dicts.
            mode: Estimation mode.
            weather_factor: Weather adjustment.
            overtime_hours: Daily overtime.
            site_constraint_factor: Site difficulty.
            hours_per_day: Standard hours.

        Returns:
            List of calculation results.
        """
        results = []

        for act in activities:
            act_id = act.get("activity_id", "")
            name = act.get("name", "")
            quantity = act.get("quantity", 0)
            unit = act.get("unit", "")
            rate_id = act.get("productivity_rate_id", "")
            crew_count = act.get("crew_count", 1)

            if rate_id and rate_id in self._rates:
                # Direct rate lookup
                result = self.calculate_duration(
                    quantity=quantity,
                    rate_id=rate_id,
                    mode=mode,
                    crew_count=crew_count,
                    weather_factor=weather_factor,
                    overtime_hours=overtime_hours,
                    site_constraint_factor=site_constraint_factor,
                    hours_per_day=hours_per_day,
                )
            elif quantity > 0 and name:
                # Auto-match
                result = self.calculate_duration_auto(
                    activity_name=name,
                    quantity=quantity,
                    unit=unit,
                    mode=mode,
                    crew_count=crew_count,
                    weather_factor=weather_factor,
                    overtime_hours=overtime_hours,
                    site_constraint_factor=site_constraint_factor,
                    hours_per_day=hours_per_day,
                )
            else:
                result = {
                    "duration_days": 0,
                    "error": "Insufficient data: need quantity > 0 and activity name or rate_id.",
                }

            result["activity_id"] = act_id
            result["activity_name"] = name
            results.append(result)

        return results


# ── Singleton Instance ───────────────────────────────────────────
duration_engine = DurationEngine()
