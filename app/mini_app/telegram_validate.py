"""Проверка подписи WebApp initData: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl


class WebAppAuthError(ValueError):
    pass


def parse_and_validate_init_data(
    init_data: str,
    bot_token: str,
    *,
    max_age_seconds: int = 86400,
) -> dict[str, Any]:
    if not init_data or not bot_token:
        raise WebAppAuthError("empty init_data or bot_token")
    parsed_list = parse_qsl(init_data, keep_blank_values=True, strict_parsing=False)
    parsed: dict[str, str] = dict(parsed_list)
    hash_received = parsed.pop("hash", None)
    if not hash_received:
        raise WebAppAuthError("no hash")

    auth_date_raw = parsed.get("auth_date")
    if auth_date_raw and auth_date_raw.isdigit():
        age = int(time.time()) - int(auth_date_raw)
        if age > max_age_seconds or age < -300:
            raise WebAppAuthError("stale auth_date")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    # PHP: hash_hmac('sha256', bot_token, 'WebAppData') → key WebAppData, data bot_token
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    calculated = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(calculated, hash_received):
        raise WebAppAuthError("invalid hash")

    out: dict[str, Any] = dict(parsed)
    user_raw = parsed.get("user")
    if user_raw:
        try:
            out["user"] = json.loads(user_raw)
        except json.JSONDecodeError:
            out["user"] = None
    return out


def telegram_user_id_from_validated(data: dict[str, Any]) -> int:
    user = data.get("user")
    if not isinstance(user, dict) or "id" not in user:
        raise WebAppAuthError("no user id")
    tid = user["id"]
    if not isinstance(tid, int):
        raise WebAppAuthError("bad user id")
    return tid
