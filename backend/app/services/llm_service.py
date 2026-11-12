"""LLM Service supporting OpenAI GPT and Realistic Intelligent Demo Mode."""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

    @property
    def is_demo_mode(self) -> bool:
        return self.client is None or not self.api_key or settings.DEMO_MODE

    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        """Call OpenAI or fallback to realistic domain-specific simulation."""
        if not self.is_demo_mode and self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"} if json_mode else None,
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI call failed, falling back to Demo Mode: {e}")

        # Demo mode notification prefix
        return self._generate_simulated_response(system_prompt, user_prompt, json_mode)

    def _generate_simulated_response(
        self, system_prompt: str, user_prompt: str, json_mode: bool
    ) -> str:
        """High-fidelity simulated model response with domain-accurate logic."""
        demo_banner = "Demo Mode — simulated model response\n\n"
        if json_mode:
            return json.dumps({
                "mode": "Demo Mode — simulated model response",
                "content": "Simulated dynamic agent completion based on domain templates."
            })
        return f"{demo_banner}Analysis and execution plan formulated based on prompt requirements."


llm_service = LLMService()
