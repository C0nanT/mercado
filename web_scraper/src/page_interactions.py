"""Page interaction and extraction helpers for SeleniumWebScraper."""
from __future__ import annotations

import time
from typing import Any, Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def handle_zipcode_modal(driver, zipcode: str | None = None, timeout: int = 10) -> None:
    """Best-effort attempt to fill zipcode modal if it appears.

    This is intentionally defensive: if elements aren't found, it just returns.
    """
    if not zipcode:
        return
    try:
        wait = WebDriverWait(driver, timeout)
        # Heuristics: common inputs/buttons for CEP modals on Brazilian e-commerces
        selectors = [
            (By.CSS_SELECTOR, "input[name='cep'], input[name='zipcode'], input[aria-label*='CEP']"),
            (By.CSS_SELECTOR, "input[type='text'][maxlength='8']"),
        ]
        input_el = None
        for by, sel in selectors:
            try:
                input_el = wait.until(EC.presence_of_element_located((by, sel)))
                if input_el:
                    break
            except Exception:
                continue
        if not input_el:
            return

        input_el.clear()
        input_el.send_keys(zipcode)

        # Try to find a submit/confirm button nearby and wait until enabled
        button_selectors = [
            (By.XPATH, "//button[contains(., 'OK') or contains(., 'Confirmar') or contains(., 'Calcular')]")
        ]
        for by, sel in button_selectors:
            try:
                btn = wait.until(EC.presence_of_element_located((by, sel)))
                # Wait until button is enabled (not disabled)
                wait.until(lambda d: btn.is_enabled() and btn.get_attribute("disabled") is None)
                btn.click()
                break
            except Exception:
                continue
    except Exception:
        # Non-fatal: just proceed
        return


def wait_for_complete_loading(driver, timeout: int = 30, zipcode: str | None = None) -> None:
    """Wait until the page is fully loaded and dynamic content likely present."""
    print(f"   ⏳ Aguardando carregamento completo da página ({timeout}s)...")

    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")

    print(f"   🌐 URL atual: {driver.current_url}")

    # Optional zipcode modal handling
    handle_zipcode_modal(driver, zipcode=zipcode)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "aside, [data-test='product-details-info']"))
        )
    except Exception:
        print("   ⚠️  Não foi possível confirmar o aside; continuando mesmo assim.")

    print("   ⏳ Aguardando conteúdo dinâmico (2s)...")
    time.sleep(2)
    print("   ✅ Página carregada completamente!")


def extract_aside_content_with_monitoring(driver) -> Dict[str, Any]:
    """Extract text-like content from likely product info aside and emulate monitoring info.

    Returns a structure compatible with existing database.save_price expectations.
    """
    try:
        candidates = driver.find_elements(By.CSS_SELECTOR, "[data-test='product-details-info'] p, aside p")
        p_tags = []
        for idx, el in enumerate(candidates, 1):
            try:
                text = (el.text or "").strip()
                html = (el.get_attribute("innerHTML") or "").strip()
                classes = el.get_attribute("class") or ""
                has_price = ("R$" in text) or ("R$" in html)
                p_tags.append({
                    "index": idx,
                    "textContent": text,
                    "innerHTML": html,
                    "classes": classes,
                    "hasPrice": has_price,
                })
            except Exception:
                continue

        return {
            "aside_found": True if p_tags else False,
            "p_tags": p_tags,
            "total_p_tags": len(p_tags),
            "monitoring_history": [],
            "total_captures": 1,
            "error": None if p_tags else "Aside ou conteúdos não encontrados",
        }
    except Exception as e:
        return {
            "aside_found": False,
            "p_tags": [],
            "total_p_tags": 0,
            "monitoring_history": [],
            "total_captures": 0,
            "error": str(e),
        }


def extract_price_via_js_selector(driver, price_js_expr: str) -> Dict[str, Any]:
    """Evaluate a JS expression to locate a price element and normalize output."""
    if not price_js_expr or not isinstance(price_js_expr, str):
        return {
            "aside_found": False,
            "p_tags": [],
            "total_p_tags": 0,
            "monitoring_history": [],
            "total_captures": 0,
            "error": "price_js inválido ou não informado",
        }

    js_code = f"""
var el = (function() {{ try {{ return {price_js_expr}; }} catch (e) {{ return null; }} }})();
if (!el) {{ return {{ found: false }}; }}
var text = el.textContent || el.innerText || '';
var html = el.innerHTML || '';
var classes = el.className || '';
return {{ found: true, text: text, html: html, classes: classes }};
"""

    try:
        result = driver.execute_script(js_code)
    except Exception as e:
        return {
            "aside_found": False,
            "p_tags": [],
            "total_p_tags": 0,
            "monitoring_history": [],
            "total_captures": 0,
            "error": f"Erro executando JS: {e}",
        }

    if not result or not result.get("found"):
        return {
            "aside_found": False,
            "p_tags": [],
            "total_p_tags": 0,
            "monitoring_history": [],
            "total_captures": 0,
            "error": "Elemento de preço não encontrado via JS",
        }

    text = (result.get("text") or "").strip()
    html = (result.get("html") or "").strip()
    classes = result.get("classes") or ""
    has_price = ("R$" in text) or ("R$" in html)

    p_tag_like = {
        "index": 1,
        "textContent": text,
        "innerHTML": html,
        "classes": classes,
        "hasPrice": has_price,
    }

    return {
        "aside_found": True,
        "p_tags": [p_tag_like],
        "total_p_tags": 1,
        "monitoring_history": [],
        "total_captures": 1,
        "error": None,
    }
