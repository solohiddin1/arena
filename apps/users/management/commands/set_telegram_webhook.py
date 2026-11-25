import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set, get or delete Telegram Bot Webhook!"

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            type=str,
            help="Base domain or full webhook URL (e.g. https://api.joyqidir.uz or https://api.joyqidir.uz/api/v1/user/auth/telegram/webhook/)",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete current webhook and drop pending updates",
        )
        parser.add_argument(
            "--info",
            action="store_true",
            help="Get current webhook info from Telegram",
        )

    def handle(self, *args, **options):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or getattr(settings, "TELEGRAM_TOKEN", None)
        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN is not set in settings or .env"))
            return

        api_url = f"https://api.telegram.org/bot{token}"

        if options["delete"]:
            resp = requests.post(
                f"{api_url}/deleteWebhook",
                json={"drop_pending_updates": True},
                timeout=15,
            )
            self.stdout.write(f"deleteWebhook result: {resp.json()}")
            return

        if options["info"] or not options["url"]:
            resp = requests.get(f"{api_url}/getWebhookInfo", timeout=15)
            self.stdout.write(f"Webhook Info: {resp.json()}")
            if not options["url"]:
                self.stdout.write(
                    self.style.WARNING(
                        "Tip: To set webhook, provide --url: python manage.py set_telegram_webhook --url https://api.yourdomain.com"
                    )
                )
            return

        base_url = options["url"].strip().rstrip("/")
        if base_url.endswith("/api/v1/user/auth/telegram/webhook") or base_url.endswith("/api/v1/users/auth/telegram/webhook"):
            webhook_url = f"{base_url}/"
        elif "/auth/telegram/webhook" in base_url:
            webhook_url = f"{base_url}/"
        else:
            webhook_url = f"{base_url}/api/v1/user/auth/telegram/webhook/"

        self.stdout.write(f"Setting webhook to: {webhook_url}")

        payload = {
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"],
            "drop_pending_updates": True,
        }

        resp = requests.post(f"{api_url}/setWebhook", json=payload, timeout=15)
        res_data = resp.json()
        if res_data.get("ok"):
            self.stdout.write(self.style.SUCCESS(f"Webhook successfully set: {res_data}"))
        else:
            self.stderr.write(self.style.ERROR(f"Failed to set webhook: {res_data}"))
