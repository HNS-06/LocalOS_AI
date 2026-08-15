import logging
import platform

logger = logging.getLogger("LocalOS.Notifications")

class NotificationManager:
    def __init__(self):
        self.enabled = platform.system() == "Windows"

    def send_toast(self, title: str, message: str, icon_type: str = "warning"):
        if not self.enabled:
            logger.info(f"[Toast Notification] {title}: {message}")
            return
            
        try:
            # Try win10toast or win32gui notification
            from win32api import MessageBox
            # For non-blocking native toast, log & output cleanly
            logger.info(f"[Windows Toast] {title}: {message}")
        except Exception as e:
            logger.error(f"Failed to trigger Windows toast notification: {e}")

notification_manager = NotificationManager()
