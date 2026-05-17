from __future__ import annotations

from pathlib import Path
from time import sleep

from backend.core.failure_detector import FailureDetector
from backend.core.self_healing import SelfHealingEngine
from backend.models.schemas import StepAction, StepLog, TestCase, TestResult, TestStatus


class SeleniumRunner:
    def __init__(self, artifacts_dir: Path | str = "reports/artifacts") -> None:
        self.artifacts_dir = Path(artifacts_dir)
        self.detector = FailureDetector()
        self.healer = SelfHealingEngine()

    def run_case(self, test_case: TestCase, headless: bool = True, demo_mode: bool = True) -> TestResult:
        if demo_mode:
            return self._run_demo_case(test_case)

        driver = self._build_driver(headless=headless)
        logs: list[StepLog] = []
        healed_steps = 0
        status = TestStatus.PASSED
        try:
            for step in test_case.steps:
                try:
                    self._execute_step(driver, step)
                    logs.append(StepLog(step_id=step.id, status=TestStatus.PASSED, message=step.description, selector_used=step.selector))
                except Exception as error:
                    context = self.detector.capture_context(driver, step, error, self.artifacts_dir / test_case.id)
                    healed = self._try_heal(driver, step, context)
                    if healed:
                        healed_steps += 1
                        status = TestStatus.HEALED
                        logs.append(StepLog(step_id=step.id, status=TestStatus.HEALED, message=f"Healed: {step.description}", selector_used=step.selector, healed_selector=healed, screenshot_path=context.screenshot_path))
                    else:
                        status = TestStatus.FAILED
                        logs.append(StepLog(step_id=step.id, status=TestStatus.FAILED, message=context.error_message, selector_used=step.selector, screenshot_path=context.screenshot_path))
                        break
        finally:
            driver.quit()

        return TestResult(test_id=test_case.id, title=test_case.title, status=status, healed_steps=healed_steps, logs=logs)

    def _build_driver(self, headless: bool):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        return webdriver.Chrome(options=options)

    def _execute_step(self, driver, step) -> None:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        wait = WebDriverWait(driver, step.timeout_seconds)
        if step.action == StepAction.NAVIGATE:
            driver.get(step.value)
        elif step.action == StepAction.WAIT:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector or "body")))
        elif step.action == StepAction.CLICK:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, step.selector))).click()
        elif step.action == StepAction.TYPE:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step.selector)))
            element.clear()
            element.send_keys(step.value or "")
        elif step.action == StepAction.ASSERT_TEXT:
            assert (step.expected or "").lower() in driver.page_source.lower()

    def _try_heal(self, driver, step, context) -> str | None:
        from selenium.webdriver.common.by import By

        for selector in self.healer.suggest_selectors(context)[:2]:
            try:
                if selector.startswith("//"):
                    element = driver.find_element(By.XPATH, selector)
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                if step.action == StepAction.CLICK:
                    element.click()
                elif step.action == StepAction.TYPE:
                    element.clear()
                    element.send_keys(step.value or "")
                return selector
            except Exception:
                continue
        return None

    def _run_demo_case(self, test_case: TestCase) -> TestResult:
        logs: list[StepLog] = []
        healed_steps = 0
        status = TestStatus.PASSED
        for index, step in enumerate(test_case.steps):
            sleep(0.04)
            if test_case.type == "edge" and index == 1:
                healed_steps += 1
                status = TestStatus.HEALED
                logs.append(StepLog(step_id=step.id, status=TestStatus.HEALED, message=f"Recovered locator for: {step.description}", selector_used=step.selector, healed_selector="input[name], textarea[name], [contenteditable='true']"))
            else:
                logs.append(StepLog(step_id=step.id, status=TestStatus.PASSED, message=step.description, selector_used=step.selector))
        return TestResult(test_id=test_case.id, title=test_case.title, status=status, healed_steps=healed_steps, logs=logs)

