"""
ConstructMind AI - CPM (Critical Path Method) Engine
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Full CPM implementation using NetworkX for:
- Building directed activity-on-node (AON) network
- Forward pass  → Early Start (ES) / Early Finish (EF)
- Backward pass → Late Start (LS) / Late Finish (LF)
- Total Float and Free Float calculation
- Critical path identification
- Calendar-aware date calculations

Supports FS, FF, SS, SF relationship types with lag/lead.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# CALENDAR HELPER
# ══════════════════════════════════════════════════════════════════

class WorkCalendar:
    """
    Simple working-day calendar that skips non-working days.
    Supports 5-day (Mon-Fri), 6-day (Mon-Sat), and 7-day weeks.
    """

    # Days of the week: Monday=0 .. Sunday=6
    CALENDARS = {
        "5_day": {5, 6},       # Saturday, Sunday off
        "6_day": {6},          # Sunday off
        "7_day": set(),        # No days off
    }

    def __init__(self, calendar_type: str = "6_day", holidays: Optional[List[date]] = None):
        self.non_working_days: Set[int] = self.CALENDARS.get(calendar_type, {6})
        self.holidays: Set[date] = set(holidays or [])

    def is_working_day(self, d: date) -> bool:
        """Check if a given date is a working day."""
        return d.weekday() not in self.non_working_days and d not in self.holidays

    def add_working_days(self, start: date, days: float) -> date:
        """
        Add a number of working days to a start date.
        If days is 0, returns the start date.
        Handles fractional days by rounding up.
        """
        if days <= 0:
            return start

        remaining = int(days) if days == int(days) else int(days) + 1
        current = start

        # Make sure we start on a working day
        while not self.is_working_day(current):
            current += timedelta(days=1)

        while remaining > 0:
            current += timedelta(days=1)
            if self.is_working_day(current):
                remaining -= 1

        return current

    def subtract_working_days(self, end: date, days: float) -> date:
        """Subtract a number of working days from an end date."""
        if days <= 0:
            return end

        remaining = int(days) if days == int(days) else int(days) + 1
        current = end

        while not self.is_working_day(current):
            current -= timedelta(days=1)

        while remaining > 0:
            current -= timedelta(days=1)
            if self.is_working_day(current):
                remaining -= 1

        return current

    def working_days_between(self, start: date, end: date) -> int:
        """Count working days between two dates (inclusive of end, exclusive of start)."""
        if end <= start:
            return 0
        count = 0
        current = start + timedelta(days=1)
        while current <= end:
            if self.is_working_day(current):
                count += 1
            current += timedelta(days=1)
        return count


# ══════════════════════════════════════════════════════════════════
# CPM ENGINE
# ══════════════════════════════════════════════════════════════════

class CPMEngine:
    """
    Critical Path Method calculation engine using NetworkX.

    Builds a directed acyclic graph (DAG) of activities and their
    dependencies, then performs forward and backward passes to
    determine the critical path.
    """

    def __init__(
        self,
        calendar_type: str = "6_day",
        holidays: Optional[List[date]] = None,
    ):
        self.calendar = WorkCalendar(calendar_type, holidays)
        self.graph: nx.DiGraph = nx.DiGraph()
        self._activities: Dict[str, Dict[str, Any]] = {}
        self._relationships: List[Dict[str, Any]] = []

    def add_activity(
        self,
        activity_db_id: str,
        activity_id: str,
        name: str,
        duration: float,
        activity_type: str = "task",
    ) -> None:
        """
        Add an activity node to the CPM network.

        Args:
            activity_db_id: Database UUID of the activity.
            activity_id: Human-readable activity ID (e.g., A1010).
            name: Activity name.
            duration: Duration in working days.
            activity_type: task / milestone / summary.
        """
        # Milestones have zero duration
        if activity_type == "milestone":
            duration = 0

        self._activities[activity_db_id] = {
            "activity_db_id": activity_db_id,
            "activity_id": activity_id,
            "name": name,
            "duration": duration,
            "activity_type": activity_type,
            # CPM values (will be computed)
            "ES": 0.0,
            "EF": 0.0,
            "LS": float("inf"),
            "LF": float("inf"),
            "total_float": 0.0,
            "free_float": 0.0,
            "is_critical": False,
            # Date values
            "early_start_date": None,
            "early_finish_date": None,
            "late_start_date": None,
            "late_finish_date": None,
        }
        self.graph.add_node(activity_db_id, **self._activities[activity_db_id])

    def add_relationship(
        self,
        predecessor_id: str,
        successor_id: str,
        relationship_type: str = "FS",
        lag_days: float = 0,
    ) -> None:
        """
        Add a dependency relationship between two activities.

        Args:
            predecessor_id: Database UUID of the predecessor activity.
            successor_id: Database UUID of the successor activity.
            relationship_type: FS, FF, SS, SF.
            lag_days: Lag (positive) or lead (negative).
        """
        if predecessor_id not in self._activities:
            logger.warning(f"Predecessor {predecessor_id} not found in activities, skipping.")
            return
        if successor_id not in self._activities:
            logger.warning(f"Successor {successor_id} not found in activities, skipping.")
            return

        rel = {
            "predecessor_id": predecessor_id,
            "successor_id": successor_id,
            "relationship_type": relationship_type.upper(),
            "lag_days": lag_days,
        }
        self._relationships.append(rel)
        self.graph.add_edge(
            predecessor_id,
            successor_id,
            relationship_type=relationship_type.upper(),
            lag_days=lag_days,
        )

    def _check_cycles(self) -> bool:
        """Check for circular dependencies in the network."""
        return not nx.is_directed_acyclic_graph(self.graph)

    def calculate(self, project_start: date) -> Dict[str, Any]:
        """
        Run the full CPM calculation.

        Args:
            project_start: The project start date.

        Returns:
            CPM result dict with all calculated values.
        """
        warnings: List[str] = []

        if not self._activities:
            return {
                "project_start": project_start,
                "project_finish": project_start,
                "total_duration_days": 0,
                "critical_path": [],
                "critical_path_duration": 0,
                "activities": [],
                "num_critical_activities": 0,
                "num_total_activities": 0,
                "has_circular_dependency": False,
                "warnings": ["No activities to schedule."],
            }

        # ── Check for cycles ─────────────────────────────────────
        has_cycle = self._check_cycles()
        if has_cycle:
            return {
                "project_start": project_start,
                "project_finish": None,
                "total_duration_days": 0,
                "critical_path": [],
                "critical_path_duration": 0,
                "activities": [],
                "num_critical_activities": 0,
                "num_total_activities": len(self._activities),
                "has_circular_dependency": True,
                "warnings": ["Circular dependency detected! Cannot compute CPM. "
                             "Please review activity relationships."],
            }

        # ── Topological order ────────────────────────────────────
        try:
            topo_order = list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            return {
                "project_start": project_start,
                "project_finish": None,
                "total_duration_days": 0,
                "critical_path": [],
                "critical_path_duration": 0,
                "activities": [],
                "num_critical_activities": 0,
                "num_total_activities": len(self._activities),
                "has_circular_dependency": True,
                "warnings": ["Cannot determine topological order."],
            }

        # Include isolated nodes (activities with no relationships)
        all_nodes = set(self._activities.keys())
        ordered_nodes = set(topo_order)
        isolated = all_nodes - ordered_nodes
        topo_order.extend(isolated)

        # ── FORWARD PASS (ES, EF) ───────────────────────────────
        for node_id in topo_order:
            act = self._activities[node_id]
            predecessors = list(self.graph.predecessors(node_id))

            if not predecessors:
                # Start activity — ES = 0
                act["ES"] = 0
            else:
                max_es = 0
                for pred_id in predecessors:
                    pred = self._activities[pred_id]
                    edge = self.graph.edges[pred_id, node_id]
                    rel_type = edge.get("relationship_type", "FS")
                    lag = edge.get("lag_days", 0)

                    if rel_type == "FS":
                        # ES(succ) = EF(pred) + lag
                        constraint = pred["EF"] + lag
                    elif rel_type == "SS":
                        # ES(succ) = ES(pred) + lag
                        constraint = pred["ES"] + lag
                    elif rel_type == "FF":
                        # EF(succ) = EF(pred) + lag → ES(succ) = EF(pred) + lag - dur(succ)
                        constraint = pred["EF"] + lag - act["duration"]
                    elif rel_type == "SF":
                        # EF(succ) = ES(pred) + lag → ES(succ) = ES(pred) + lag - dur(succ)
                        constraint = pred["ES"] + lag - act["duration"]
                    else:
                        constraint = pred["EF"] + lag

                    max_es = max(max_es, constraint)

                act["ES"] = max(0, max_es)

            act["EF"] = act["ES"] + act["duration"]

        # ── Project finish (maximum EF) ──────────────────────────
        max_ef = max(act["EF"] for act in self._activities.values())

        # ── BACKWARD PASS (LS, LF) ──────────────────────────────
        for node_id in reversed(topo_order):
            act = self._activities[node_id]
            successors = list(self.graph.successors(node_id))

            if not successors:
                # End activity — LF = project duration
                act["LF"] = max_ef
            else:
                min_lf = float("inf")
                for succ_id in successors:
                    succ = self._activities[succ_id]
                    edge = self.graph.edges[node_id, succ_id]
                    rel_type = edge.get("relationship_type", "FS")
                    lag = edge.get("lag_days", 0)

                    if rel_type == "FS":
                        # LF(pred) = LS(succ) - lag
                        constraint = succ["LS"] - lag
                    elif rel_type == "SS":
                        # LS(pred) = LS(succ) - lag → LF(pred) = LS(succ) - lag + dur(pred)
                        constraint = succ["LS"] - lag + act["duration"]
                    elif rel_type == "FF":
                        # LF(pred) = LF(succ) - lag
                        constraint = succ["LF"] - lag
                    elif rel_type == "SF":
                        # LS(pred) = LF(succ) - lag → LF(pred) = LF(succ) - lag + dur(pred)
                        constraint = succ["LF"] - lag + act["duration"]
                    else:
                        constraint = succ["LS"] - lag

                    min_lf = min(min_lf, constraint)

                act["LF"] = min_lf

            act["LS"] = act["LF"] - act["duration"]

        # ── FLOAT CALCULATION ────────────────────────────────────
        for node_id in topo_order:
            act = self._activities[node_id]

            # Total Float = LS - ES = LF - EF
            act["total_float"] = act["LS"] - act["ES"]

            # Free Float = min(ES(successors)) - EF(current)
            successors = list(self.graph.successors(node_id))
            if successors:
                min_succ_es = float("inf")
                for succ_id in successors:
                    succ = self._activities[succ_id]
                    edge = self.graph.edges[node_id, succ_id]
                    rel_type = edge.get("relationship_type", "FS")
                    lag = edge.get("lag_days", 0)

                    if rel_type == "FS":
                        min_succ_es = min(min_succ_es, succ["ES"] - lag)
                    elif rel_type == "SS":
                        min_succ_es = min(min_succ_es, succ["ES"] - lag + act["duration"])
                    elif rel_type == "FF":
                        min_succ_es = min(min_succ_es, succ["EF"] - lag)
                    elif rel_type == "SF":
                        min_succ_es = min(min_succ_es, succ["EF"] - lag + act["duration"])

                act["free_float"] = max(0, min_succ_es - act["EF"])
            else:
                act["free_float"] = max(0, max_ef - act["EF"])

            # Critical if total float ≈ 0
            act["is_critical"] = abs(act["total_float"]) < 0.001

        # ── Convert to calendar dates ────────────────────────────
        for act in self._activities.values():
            act["early_start_date"] = self.calendar.add_working_days(project_start, act["ES"])
            act["early_finish_date"] = self.calendar.add_working_days(project_start, act["EF"])
            act["late_start_date"] = self.calendar.add_working_days(project_start, act["LS"])
            act["late_finish_date"] = self.calendar.add_working_days(project_start, act["LF"])

        # ── Identify critical path ───────────────────────────────
        critical_activities = [
            act for act in self._activities.values() if act["is_critical"]
        ]
        critical_ids = [act["activity_id"] for act in critical_activities]
        critical_duration = max(
            (act["EF"] for act in critical_activities), default=0
        )

        project_finish = self.calendar.add_working_days(project_start, max_ef)

        # ── Build results ────────────────────────────────────────
        activity_results = []
        for act in self._activities.values():
            activity_results.append({
                "activity_id": act["activity_id"],
                "activity_db_id": act["activity_db_id"],
                "name": act["name"],
                "duration": act["duration"],
                "early_start": act["early_start_date"],
                "early_finish": act["early_finish_date"],
                "late_start": act["late_start_date"],
                "late_finish": act["late_finish_date"],
                "total_float": round(act["total_float"], 2),
                "free_float": round(act["free_float"], 2),
                "is_critical": act["is_critical"],
            })

        # Sort by ES then EF
        activity_results.sort(key=lambda a: (a["early_start"] or date.min, a["early_finish"] or date.min))

        return {
            "project_start": project_start,
            "project_finish": project_finish,
            "total_duration_days": max_ef,
            "critical_path": critical_ids,
            "critical_path_duration": critical_duration,
            "activities": activity_results,
            "num_critical_activities": len(critical_activities),
            "num_total_activities": len(self._activities),
            "has_circular_dependency": False,
            "warnings": warnings,
        }

    def get_longest_path(self) -> Tuple[List[str], float]:
        """
        Find the longest path through the network (critical path).
        Uses NetworkX's dag_longest_path with duration as weight.

        Returns:
            Tuple of (list of activity IDs on longest path, total duration).
        """
        if self._check_cycles():
            return [], 0

        if not self._activities:
            return [], 0

        try:
            # Set weight to duration for longest path calculation
            for node_id in self.graph.nodes():
                self.graph.nodes[node_id]["weight"] = self._activities[node_id]["duration"]

            longest = nx.dag_longest_path(self.graph, weight="weight")
            path_ids = [self._activities[n]["activity_id"] for n in longest]
            total_dur = sum(self._activities[n]["duration"] for n in longest)
            return path_ids, total_dur
        except Exception as e:
            logger.error(f"Error finding longest path: {e}")
            return [], 0

    def get_network_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the CPM network."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
            "connected_components": (
                nx.number_weakly_connected_components(self.graph)
                if self.graph.number_of_nodes() > 0 else 0
            ),
            "isolated_nodes": len(list(nx.isolates(self.graph))),
        }
