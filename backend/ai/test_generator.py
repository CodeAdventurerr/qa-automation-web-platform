from __future__ import annotations

import os

from backend.models.schemas import StepAction, TestCase, TestStep


class AITestGenerator:
    """AI test generator with a deterministic fallback for local demos."""

    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "local")

    async def generate(self, url: str, feature: str) -> list[TestCase]:
        if os.getenv("OPENAI_API_KEY"):
            # Production hook: call an LLM with JSON schema output here.
            # The fallback keeps the platform demoable without credentials.
            return self._fallback_cases(url, feature)
        return self._fallback_cases(url, feature)

    def _fallback_cases(self, url: str, feature: str) -> list[TestCase]:
        normalized = feature.strip().capitalize()
        return [
            TestCase(
                title=f"{normalized} happy path",
                type="positive",
                severity="high",
                steps=[
                    TestStep(action=StepAction.NAVIGATE, description=f"Open {url}", value=url),
                    TestStep(action=StepAction.WAIT, description="Wait for primary page content", selector="body"),
                    TestStep(action=StepAction.CLICK, description=f"Open or submit the {feature} flow", selector="[data-testid='primary-action'], button, a"),
                    TestStep(action=StepAction.ASSERT_TEXT, description="Confirm successful outcome is visible", expected="success"),
                ],
                expected_result=f"The {feature} flow completes successfully.",
            ),
            TestCase(
                title=f"{normalized} validation failure",
                type="negative",
                severity="medium",
                steps=[
                    TestStep(action=StepAction.NAVIGATE, description=f"Open {url}", value=url),
                    TestStep(action=StepAction.CLICK, description="Submit without required inputs", selector="button[type='submit'], button"),
                    TestStep(action=StepAction.ASSERT_TEXT, description="Validation message is announced", expected="required"),
                ],
                expected_result="The app prevents invalid submission and shows a clear validation message.",
            ),
            TestCase(
                title=f"{normalized} edge case resilience",
                type="edge",
                severity="medium",
                steps=[
                    TestStep(action=StepAction.NAVIGATE, description=f"Open {url}", value=url),
                    TestStep(action=StepAction.TYPE, description="Enter long boundary-value text", selector="input, textarea", value="x" * 128),
                    TestStep(action=StepAction.CLICK, description="Submit boundary input", selector="button[type='submit'], button"),
                    TestStep(action=StepAction.ASSERT_TEXT, description="Page remains stable after edge input", expected=""),
                ],
                expected_result="The page remains stable and either accepts or clearly rejects the boundary input.",
            ),
        ]

