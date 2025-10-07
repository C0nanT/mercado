"""Utilities for configuring and closing the Selenium Chrome driver."""
from __future__ import annotations

import logging
import os
import shutil
from contextlib import redirect_stderr

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(headless: bool = True) -> webdriver.Chrome:
    """Create and configure a Chrome WebDriver instance.

    Args:
        headless: Run Chrome in headless mode.

    Returns:
        A configured webdriver.Chrome instance.
    """
    chrome_options = Options()

    # Modern headless is more stable
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

    # Performance and CI-friendly flags
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920,1080")

    # Reduce automation fingerprinting
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Conservative, reliable driver acquisition
    local_driver = shutil.which("chromedriver")
    if local_driver:
        service = Service(local_driver)
    else:
        # Speed up webdriver_manager and keep it quiet
        os.environ.setdefault("WDM_TIMEOUT", "15")
        os.environ.setdefault("WDM_LOG_LEVEL", "0")
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Hide webdriver flag
    try:
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
    except Exception:
        pass

    # Reasonable default timeouts
    try:
        driver.set_page_load_timeout(45)
    except Exception:
        pass

    return driver


def close_driver(driver: webdriver.Chrome | None) -> None:
    """Close the driver, suppressing noisy shutdown errors on Linux.

    Selenium/Chromedriver sometimes throws PermissionError during process
    termination. We silence the service logger and redirect stderr temporarily.
    """
    if not driver:
        return

    svc_logger = logging.getLogger("selenium.webdriver.common.service")
    prev_level = svc_logger.level
    prev_propagate = getattr(svc_logger, "propagate", True)
    svc_logger.setLevel(logging.CRITICAL)
    svc_logger.propagate = False

    try:
        with open(os.devnull, "w") as devnull:
            with redirect_stderr(devnull):
                try:
                    driver.quit()
                except PermissionError:
                    # Ignore Linux PermissionError on SIGTERM
                    pass
                except Exception:
                    try:
                        if getattr(driver, "service", None):
                            driver.service.stop()
                    except Exception:
                        pass
    finally:
        try:
            svc_logger.setLevel(prev_level)
            svc_logger.propagate = prev_propagate
        except Exception:
            pass
