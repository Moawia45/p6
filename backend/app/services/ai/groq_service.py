"""
ConstructMind AI - Groq AI Service
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Service class wrapping the Groq API (OpenAI-compatible SDK) for:
- Real-time AI copilot chat (streaming SSE)
- Quick construction insights
- Activity suggestions

Primary model: meta-llama/llama-4-scout-17b-16e-instruct
"""

from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# ── Construction-specific system prompt ──────────────────────────
CONSTRUCTION_SYSTEM_PROMPT = """You are ConstructMind AI, an expert AI assistant for construction project planning, scheduling, and management. You were created by Moawia Husnain, Civil Engineer from UET Taxila.

Your expertise includes:
- Construction project scheduling (CPM, PERT, Gantt charts)
- Primavera P6 and MS Project planning concepts
- Bill of Quantities (BOQ) analysis and cost estimation
- Resource leveling and allocation
- Earned Value Management (EVM) - SPI, CPI, BCWS, BCWP, ACWP
- Construction productivity rates and crew planning
- Risk management (qualitative and quantitative)
- Delay analysis (As-Planned vs As-Built, TIA, Windows)
- Contract administration (FIDIC, AIA, NEC)
- Construction methods and best practices
- Health, Safety, and Environment (HSE) on construction sites
- Pakistani and South Asian construction standards and practices

Guidelines:
- Always provide practical, actionable advice
- Use construction industry terminology accurately
- Reference relevant standards (ACI, ASTM, BS, Pakistan Building Code) when applicable
- Include specific numbers, rates, and quantities when possible
- If asked about scheduling, consider critical path, float, and resource constraints
- For cost questions, consider Pakistan market rates when appropriate
- Format responses clearly with headings, bullet points, and tables when helpful
- If you're uncertain, say so and suggest where to find authoritative information
"""


class GroqService:
    """
    Wrapper around the Groq API using the OpenAI-compatible SDK.
    Provides construction-domain-specific chat and insight methods.
    """

    def __init__(self) -> None:
        """Initialize the Groq client with OpenAI-compatible SDK."""
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. Groq/copilot features will be unavailable.")
            self._client = None
        else:
            self._client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        self._model = settings.GROQ_MODEL
        self._max_tokens = settings.GROQ_MAX_TOKENS
        self._temperature = settings.GROQ_TEMPERATURE

    @property
    def is_available(self) -> bool:
        """Check if the Groq service is configured."""
        return self._client is not None

    def _ensure_available(self) -> None:
        """Raise an error if the service is not configured."""
        if not self.is_available:
            raise RuntimeError(
                "Groq AI service is not available. Please set GROQ_API_KEY in your environment."
            )

    def _build_messages(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        project_context: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Build the messages array for the chat completion API.

        Args:
            user_message: The current user message.
            conversation_history: Previous conversation messages.
            system_prompt: Override for the default system prompt.
            project_context: Optional project-specific context to prepend.

        Returns:
            List of message dicts for the API.
        """
        messages: List[Dict[str, str]] = []

        # System prompt
        sys_prompt = system_prompt or CONSTRUCTION_SYSTEM_PROMPT
        if project_context:
            sys_prompt += f"\n\n--- ACTIVE PROJECT CONTEXT ---\n{project_context}"
        messages.append({"role": "system", "content": sys_prompt})

        # Conversation history (limit to last 20 messages to respect context window)
        if conversation_history:
            for msg in conversation_history[-20:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        # Current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    # ═══════════════════════════════════════════════════════════════
    # SYNCHRONOUS CHAT (non-streaming)
    # ═══════════════════════════════════════════════════════════════

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        project_context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send a chat message to Groq and return the complete response.

        Args:
            message: User message.
            conversation_history: Previous messages.
            project_context: Optional project context string.
            temperature: Override sampling temperature.
            max_tokens: Override max output tokens.

        Returns:
            Dict with message, model, and usage info.
        """
        self._ensure_available()

        messages = self._build_messages(
            user_message=message,
            conversation_history=conversation_history,
            project_context=project_context,
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._temperature,
                max_tokens=max_tokens or self._max_tokens,
                stream=False,
            )

            return {
                "message": response.choices[0].message.content or "",
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
            }

        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise RuntimeError(f"Groq AI chat failed: {e}") from e

    # ═══════════════════════════════════════════════════════════════
    # STREAMING CHAT (SSE)
    # ═══════════════════════════════════════════════════════════════

    def stream_chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        project_context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Any:
        """
        Send a chat message and return a streaming response generator.

        Yields chunks of the response as they arrive from the Groq API.
        Designed to be wrapped in an SSE event generator for FastAPI.

        Args:
            message: User message.
            conversation_history: Previous messages.
            project_context: Optional project context string.
            temperature: Override sampling temperature.
            max_tokens: Override max output tokens.

        Returns:
            Streaming response iterator from the Groq API.
        """
        self._ensure_available()

        messages = self._build_messages(
            user_message=message,
            conversation_history=conversation_history,
            project_context=project_context,
        )

        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature or self._temperature,
                max_tokens=max_tokens or self._max_tokens,
                stream=True,
            )
            return stream

        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            raise RuntimeError(f"Groq AI streaming failed: {e}") from e

    # ═══════════════════════════════════════════════════════════════
    # QUICK INSIGHT
    # ═══════════════════════════════════════════════════════════════

    def quick_insight(
        self,
        topic: str,
        context: str = "",
    ) -> str:
        """
        Get a quick construction-related insight or answer.
        Uses lower temperature for more factual responses.

        Args:
            topic: The topic or question to get insight on.
            context: Additional context.

        Returns:
            Insight text string.
        """
        self._ensure_available()

        system_prompt = (
            "You are a concise construction expert. Provide brief, "
            "accurate, and actionable insights. Keep responses under 200 words "
            "unless more detail is specifically needed."
        )

        prompt = topic
        if context:
            prompt = f"{topic}\n\nContext: {context}"

        messages = self._build_messages(
            user_message=prompt,
            system_prompt=system_prompt,
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                stream=False,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Groq quick_insight error: {e}")
            raise RuntimeError(f"Groq quick insight failed: {e}") from e

    # ═══════════════════════════════════════════════════════════════
    # ACTIVITY SUGGESTIONS
    # ═══════════════════════════════════════════════════════════════

    def suggest_activities(
        self,
        description: str,
        project_type: str = "building",
        existing_activities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Suggest additional or missing activities based on project context.

        Args:
            description: Project or work package description.
            project_type: Type of construction project.
            existing_activities: Names of activities already in the schedule.

        Returns:
            List of suggested activity dicts.
        """
        self._ensure_available()

        existing_str = ""
        if existing_activities:
            existing_str = f"\n\nExisting activities in the schedule:\n" + "\n".join(
                f"- {a}" for a in existing_activities
            )

        system_prompt = (
            "You are a construction scheduling expert. Suggest missing or "
            "additional activities for the project. Return a JSON array of objects "
            "with fields: activity_id, name, description, estimated_duration_days, "
            "predecessor_suggestion, trade. Return ONLY valid JSON array, no other text."
        )

        prompt = (
            f"Project type: {project_type}\n"
            f"Description: {description}{existing_str}\n\n"
            f"Suggest activities that should be included. Return JSON array only."
        )

        messages = self._build_messages(
            user_message=prompt,
            system_prompt=system_prompt,
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.4,
                max_tokens=4096,
                stream=False,
            )

            raw = response.choices[0].message.content or "[]"

            # Clean up any markdown formatting
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                first_nl = cleaned.index("\n") if "\n" in cleaned else 3
                cleaned = cleaned[first_nl + 1:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            return json.loads(cleaned)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse activity suggestions JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Groq suggest_activities error: {e}")
            raise RuntimeError(f"Groq activity suggestion failed: {e}") from e


# ── Singleton Instance ───────────────────────────────────────────
groq_service = GroqService()
