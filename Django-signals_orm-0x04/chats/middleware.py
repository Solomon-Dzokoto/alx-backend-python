import time
import threading
from collections import deque, defaultdict
from datetime import datetime
import logging

from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponse


class RequestLoggingMiddleware:
    """Logs each request to a file with timestamp, user and request path.

    The log file defaults to <BASE_DIR>/requests.log but can be overridden
    with the Django setting REQUESTS_LOG_PATH.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_logger")
        # Configure a file handler only once
        if not self.logger.handlers:
            log_path = getattr(settings, "REQUESTS_LOG_PATH", None)
            if not log_path:
                try:
                    log_path = str(settings.BASE_DIR / "requests.log")
                except Exception:
                    log_path = "requests.log"
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            user_repr = getattr(user, "username", str(user))
        else:
            user_repr = "Anonymous"

        self.logger.info(f"{datetime.now()} - User: {user_repr} - Path: {request.path}")
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    """Restricts access to chat endpoints outside allowed hours.

    Assumption: Chats endpoints contain the string "chats" in the path.
    Allowed window is 06:00 - 21:00 (6 AM to 9 PM). Requests outside that
    window will receive HTTP 403 Forbidden. This assumption can be adjusted.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = getattr(request, "path", "")
        if "chats" in path:
            now = datetime.now()
            hour = now.hour
            # Allow between 6:00 (inclusive) and 21:00 (exclusive)
            if hour >= 21 or hour < 6:
                return HttpResponseForbidden("Chats are available between 06:00 and 21:00")
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """Implements a simple rate-limit per IP for POST requests to chat endpoints.

    Tracks timestamps (in seconds) for each IP address and allows up to `limit`
    messages within `window` seconds. If exceeded, returns HTTP 429.
    """

    def __init__(self, get_response, limit: int = 5, window: int = 60):
        self.get_response = get_response
        self.limit = limit
        self.window = window
        self.lock = threading.Lock()
        self.requests = defaultdict(deque)  # ip -> deque[timestamp]

    def _get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")

    def __call__(self, request):
        if request.method == "POST" and "chats" in getattr(request, "path", ""):
            ip = self._get_client_ip(request)
            now_ts = time.time()
            dq = self.requests[ip]
            with self.lock:
                # remove old timestamps
                while dq and dq[0] <= now_ts - self.window:
                    dq.popleft()
                if len(dq) >= self.limit:
                    return HttpResponse("Message limit exceeded. Try again later.", status=429)
                dq.append(now_ts)

        return self.get_response(request)


class RolepermissionMiddleware:
    """Enforces that certain actions are only allowed for admin/moderator users.

    Rules (reasonable defaults / assumptions):
    - Any request to paths starting with '/chats/admin' or '/chats/moderate' is
      considered admin-only.
    - Any mutating HTTP method (DELETE/PUT/PATCH) is considered restricted.
    The middleware checks `request.user` for `is_staff`/`is_superuser` or a
    `role` attribute containing 'admin' or 'moderator'. Non-authorized users get
    HTTP 403.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = getattr(request, "path", "")
        restricted_paths = ("/chats/admin", "/chats/moderate")
        restricted_methods = ("DELETE", "PUT", "PATCH")

        needs_check = False
        if any(path.startswith(p) for p in restricted_paths):
            needs_check = True
        if request.method in restricted_methods and "chats" in path:
            needs_check = True

        if needs_check:
            user = getattr(request, "user", None)
            allowed = False
            if user and getattr(user, "is_authenticated", False):
                if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
                    allowed = True
                elif getattr(user, "role", None) in ("admin", "moderator"):
                    allowed = True

            if not allowed:
                return HttpResponseForbidden("You don't have permission to perform this action.")

        return self.get_response(request)
