from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SELENIUM_FAILURES = (
    "NoSuchElementException",
    "TimeoutException",
    "StaleElementReferenceException",
)


@dataclass
class FailureContext:
    failed_step: str
    selector_used: str | None
    intended_action: str
    error_type: str
    error_message: str
    dom_snapshot: str
    screenshot_path: str | None
    current_url: str | None


class FailureDetector:
    def is_recoverable(self, error: Exception) -> bool:
        name = error.__class__.__name__
        return name in SELENIUM_FAILURES or any(marker in str(error) for marker in SELENIUM_FAILURES)

    def capture_context(self, driver, step, error: Exception, artifacts_dir: Path) -> FailureContext:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        dom_snapshot = self._safe_dom(driver)
        dom_path = artifacts_dir / f"{step.id}.dom.html"
        dom_path.write_text(dom_snapshot, encoding="utf-8")

        screenshot_path = artifacts_dir / f"{step.id}.png"
        saved_screenshot = None
        try:
            if driver:
                driver.save_screenshot(str(screenshot_path))
                saved_screenshot = str(screenshot_path)
        except Exception:
            saved_screenshot = None

        return FailureContext(
            failed_step=step.description,
            selector_used=step.selector,
            intended_action=step.action.value,
            error_type=error.__class__.__name__,
            error_message=str(error),
            dom_snapshot=dom_snapshot[:20000],
            screenshot_path=saved_screenshot,
            current_url=getattr(driver, "current_url", None) if driver else None,
        )

    @staticmethod
    def _safe_dom(driver) -> str:
        try:
            return driver.page_source if driver else "<html><body>demo mode</body></html>"
        except Exception:
            return "<html><body>DOM capture unavailable</body></html>"

