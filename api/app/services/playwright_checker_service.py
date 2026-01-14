import os
import traceback
from datetime import datetime, timezone as dt_timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import logging

logger = logging.getLogger()

def check_key_with_browser(keys, account, proxy=None):
    results = []
    proxy_config = proxy.as_playwright_dict() if proxy else None
    browser = None
    context = None
    
    try:
        with sync_playwright() as p:
            try:
                logger.warning("Launching browser...")

                browser = p.chromium.launch(
                headless=True,
                proxy=proxy_config,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
                )


                logger.warning("Browser launched successfully")
                context = browser.new_context(locale="en-US")
                page = context.new_page()

                page.goto("https://setup.office.com/redeem/enter-key")
                page.get_by_text("Sign in", exact=True).click()
                page.fill('input[id="usernameEntry"]', account.email)
                page.get_by_text("Next", exact=True).click()
                page.fill('input[name="passwd"]', account.password)
                page.get_by_text("Next", exact=True).click(timeout=4000)
                page.wait_for_timeout(4000)

                if "We're unable to complete your request" in page.content():
                    return {"error": "PlaywrightStartupFailure"}

                skip_intermediate_windows(page)

                for key in keys:
                    data = {
                        "id": key.id,
                        "is_activated": None,
                        "redeemed_by": None,
                        "redeemed_date": None,
                        "error_code": None,
                    }

                    try:
                        result = process_key(page, key)
                        if result == "TooManyRequests":
                            break
                        if result:
                            data.update(result)
                            results.append(data)

                    except Exception as e:
                        save_debug_info(page, key.id)
                        return {
                            "keys": results,
                            "error": "PlaywrightCriticalFailure",
                            "message": str(e),
                            "traceback": traceback.format_exc(),
                        }

            finally:
                
                if context:
                    try:
                        context.close()
                    except Exception:
                        pass
                if browser:
                    try:
                        browser.close()
                    except Exception:
                        pass

    except Exception as e:
        return {
            "error": "PlaywrightStartupFailure",
            "message": str(e),
            "traceback": traceback.format_exc(),
        }

    return {"keys": results}


def skip_intermediate_windows(page):
    """Пропускает окна входа/настроек Microsoft."""
    try:
        while True:
            try:
                page.wait_for_selector("#iShowSkip", timeout=4000)
                page.locator("#iShowSkip").click()
                page.wait_for_timeout(1000)
            except PlaywrightTimeoutError:
                page.goto("https://setup.office.com/redeem/enter-key")
                break

        while True:
            try:
                page.get_by_text("No", exact=True).click(timeout=4000)
                page.wait_for_timeout(1000)
            except:
                break

        while True:
            try:
                page.get_by_text("Get started", exact=True).first.click(timeout=4000)
                page.wait_for_timeout(1000)
            except:
                break
    except Exception:
        pass


def process_key(page, key):
    """Обрабатывает один ключ."""
    page.fill('input[aria-label="Enter your product key"]', key.key)
    page.get_by_text("Next", exact=True).click()
    page.wait_for_timeout(3000)

    error_el = page.locator('[data-testid="errorCode"]')
    if not error_el.is_visible():
        return None

    error_code = error_el.inner_text().strip()

    # Разбор типов ошибок
    if "TooManyRequests" in error_code:
        return "TooManyRequests"

    if "TokenAlreadyRedeemedByOtherMSA" in error_code:
        redeemed_by, redeemed_date = extract_redeem_info(page)
        return {
            "is_activated": True,
            "error_code": "TokenAlreadyRedeemedByOtherMSA",
            "redeemed_by": redeemed_by,
            "redeemed_date": redeemed_date,
        }

    if "GeoBlocked" in error_code:
        return {"is_activated": False, "error_code": "GeoBlocked"}

    if "TokenStateScrapped" in error_code:
        return {"is_activated": True, "error_code": "TokenStateScrapped"}

    return {"is_activated": True, "error_code": "UnknownError"}


def extract_redeem_info(page):
    """Извлекает почту и дату из блока с информацией о активации."""
    try:
        redeem_info_p = page.locator("p", has_text="This product key was redeemed by")
        if redeem_info_p.is_visible():
            strongs = redeem_info_p.locator("strong")
            email = strongs.nth(0).inner_text().strip()
            date_text = strongs.nth(1).inner_text().strip()
            return email, parse_date(date_text)
    except Exception:
        pass
    return None, None


def parse_date(date_str):
    """Парсит дату в UTC, если формат неизвестен — возвращает текущую дату."""
    try:
        dt = datetime.strptime(date_str, "%B %d, %Y")
        return dt.replace(tzinfo=dt_timezone.utc)
    except Exception:
        return datetime.now(dt_timezone.utc)


def save_debug_info(page, key_id):
    """Сохраняет скриншот и HTML для отладки."""
    try:
        debug_dir = "./debug"
        os.makedirs(debug_dir, exist_ok=True)
        page.screenshot(path=f"{debug_dir}/screenshot_{key_id}.png")
        with open(f"{debug_dir}/page_{key_id}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception:
        pass
