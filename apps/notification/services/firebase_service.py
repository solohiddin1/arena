import os
import firebase_admin
from django.conf import settings
from firebase_admin import credentials, messaging

from apps.shared.middleware.middleware import get_logger

logger = get_logger()
_firebase_app: firebase_admin.App | None = None


def _get_firebase_app() -> firebase_admin.App | None:
    global _firebase_app
    if _firebase_app is None:
        cred_path = getattr(settings, "FIREBASE_CREDENTIALS_FILE", None)
        if not cred_path or not os.path.exists(cred_path):
            logger.warning(f"Firebase credentials file not found at: {cred_path}")
            return None
        try:
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.warning(f"Failed to initialize firebase_admin: {e}")
            return None
    return _firebase_app


class FirebaseService:
    @staticmethod
    def send_to_token(
        token: str,
        title: str,
        body: str,
        data: dict | None = None,
        image: str | None = None,
    ) -> str:
        app = _get_firebase_app()
        if app is None:
            logger.warning("Firebase app not available; skipped sending notification.")
            return ""
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body, image=image),
            data={str(k): str(v) for k, v in (data or {}).items()},
            token=token,
            android=messaging.AndroidConfig(priority="high"),
        )
        return messaging.send(message, app=app)
