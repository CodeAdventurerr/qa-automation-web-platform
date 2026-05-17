from __future__ import annotations

import re

from backend.core.failure_detector import FailureContext


class SelfHealingEngine:
    """Ranks alternative locators from failure context.

    Production deployments can replace `suggest_selectors` with an LLM call that
    returns strict JSON. The local strategy intentionally favors stable selectors.
    """

    def suggest_selectors(self, context: FailureContext) -> list[str]:
        candidates: list[str] = []
        original = context.selector_used or ""
        if original:
            candidates.extend(self._relax_selector(original))

        text_candidates = self._text_candidates(context.failed_step)
        candidates.extend(text_candidates)
        candidates.extend(["[data-testid]", "button", "a", "input", "textarea"])
        return list(dict.fromkeys(candidate for candidate in candidates if candidate))

    def _relax_selector(self, selector: str) -> list[str]:
        relaxed = [selector]
        if "[data-testid=" in selector:
            relaxed.append(re.sub(r"\[data-testid=['\"]([^'\"]+)['\"]\]", r"[data-testid*='\1']", selector))
        if "#" in selector:
            relaxed.append(re.sub(r"#[A-Za-z0-9_-]+", "[id]", selector))
        if "." in selector:
            relaxed.append(re.sub(r"\.[A-Za-z0-9_-]+", "", selector).strip())
        return relaxed

    @staticmethod
    def _text_candidates(description: str) -> list[str]:
        words = [word.lower() for word in re.findall(r"[A-Za-z]{4,}", description)]
        selectors: list[str] = []
        for word in words[:4]:
            selectors.append(f"button[aria-label*='{word}' i]")
            selectors.append(f"a[aria-label*='{word}' i]")
            selectors.append(f"//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{word}')]")
        return selectors

