from datetime import datetime
from celery import shared_task
from app.core.db import SessionSync
from app.models.key import Key
from app.models.proxy import Proxy
from app.models.ms_account import MSAccount
from app.services.playwright_checker_service import check_key_with_browser


@shared_task(bind=True, name="app.tasks.check_keys_task.check_keys_task")  # bind=True => self.update_state
def check_keys_task(self, session_id: str):
    db = SessionSync()
    max_attempts = 9
    attempts = 0
    error_count = 0

    total_keys = db.query(Key).filter(Key.session_id == session_id).count()
    checked_keys = 0

    while attempts < max_attempts:
        # обновляем прогресс в Celery
        percent = (checked_keys / total_keys * 100) if total_keys else 100
        self.update_state(
            state="PROGRESS",
            meta={
                "session_id": session_id,
                "total": total_keys,
                "checked": checked_keys,
                "percent": percent
            }
        )
        keys = db.query(Key).filter(Key.session_id == session_id, Key.checked == False).all()
        if not keys:
            break

        account = (
            db.query(MSAccount)
            .filter(MSAccount.is_used == False)
            .order_by(MSAccount.usage_count, MSAccount.last_used_at)
            .first()
        )
        proxy = (
            db.query(Proxy)
            .order_by(Proxy.usage_count, Proxy.last_used_at)
            .first()
        )

        if not account or not proxy:
            db.close()
            return "No valid accounts or proxies available."

        result = check_key_with_browser(keys, account, proxy)

        if result.get("error") == "TooManyRequests":
            attempts += 1
            account.is_used = True
            db.commit()
            continue

        if result.get("error") in ["PageTimeout", "PlaywrightCriticalFailure"]:
            error_count += 1
            if error_count >= 3:
                account.is_used = True
                db.commit()
            continue

        for key_data in result.get("keys", []):
            key = db.query(Key).get(key_data["id"])
            if key:
                key.checked = True
                key.is_activated = key_data.get("is_activated")
                key.redeemed_by = key_data.get("redeemed_by")
                key.redeemed_date = key_data.get("redeemed_date")
                key.error_code = key_data.get("error_code")
                checked_keys += 1


        account.usage_count += 1
        proxy.usage_count += 1
        account.last_used_at = proxy.last_used_at = datetime.utcnow()
        db.commit()

    remaining = db.query(Key).filter(Key.session_id == session_id, Key.checked == False).count()
    db.close()

    return {
        "session_id": session_id,
        "total": total_keys,
        "checked": checked_keys,
        "percent": 100,
        "remaining": remaining
    }

