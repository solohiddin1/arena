import time
import traceback

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.users.services.telegram import TgOtpService


class Command(BaseCommand):
    help = "Poll Telegram for updates (dev alternative to webhook)"

    def handle(self, *args, **kwargs):
        tokens = list({
            t for t in [
                getattr(settings, "TELEGRAM_ADMIN_BOT_TOKEN", None),
                getattr(settings, "TELEGRAM_BOT_TOKEN", None),
                getattr(settings, "TELEGRAM_TOKEN", None),
            ] if t
        })
        if not tokens:
            self.stderr.write("No Telegram bot token found in settings.")
            return

        for token in tokens:
            url = f"https://api.telegram.org/bot{token}"
            try:
                resp = requests.post(
                    f"{url}/deleteWebhook", json={"drop_pending_updates": False}, timeout=10
                )
                result = resp.json()
                if not result.get("ok"):
                    self.stderr.write(f"deleteWebhook failed for token ...{token[-8:]}: {result}")
            except Exception as e:
                self.stderr.write(f"Failed to delete webhook for token: {e}")

        self.stdout.write("Polling started for tokens...")
        offsets = {t: None for t in tokens}

        while True:
            for token in tokens:
                try:
                    url = f"https://api.telegram.org/bot{token}"
                    params = {"timeout": 10, "allowed_updates": '["message", "callback_query"]'}
                    if offsets[token]:
                        params["offset"] = offsets[token]
                    resp = requests.get(f"{url}/getUpdates", params=params, timeout=15)
                    data = resp.json()
                    if not data.get("ok"):
                        continue
                    for update in data.get("result", []):
                        offsets[token] = update["update_id"] + 1
                        try:
                            TgOtpService.handle_update(update)
                        except Exception:
                            self.stderr.write(traceback.format_exc())
                except Exception:
                    self.stderr.write(traceback.format_exc())
            time.sleep(1)
