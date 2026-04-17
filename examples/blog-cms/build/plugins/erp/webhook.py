"""Inbound webhook receiver — Odoo → this app.

Add Odoo automated action → call outgoing webhook to /erp/webhook/{model}.
HMAC signature verification uses ERP_WEBHOOK_SECRET env var.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Callable

from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/erp/webhook", tags=["erp"])


# Registry of per-model handlers
HANDLERS: dict[str, list[Callable[[dict], None]]] = {}


def on_odoo(model: str):
    """Decorator — register a handler for an Odoo model event."""
    def deco(fn: Callable[[dict], None]):
        HANDLERS.setdefault(model, []).append(fn)
        return fn
    return deco


def _verify(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/{model}")
async def receive(model: str, request: Request):
    body = await request.body()
    secret = os.getenv("ERP_WEBHOOK_SECRET", "")
    if secret:
        sig = request.headers.get("X-Signature", "")
        if not _verify(body, sig, secret):
            raise HTTPException(401, "Invalid signature")
    payload = json.loads(body) if body else {}
    called = 0
    for handler in HANDLERS.get(model, []):
        handler(payload)
        called += 1
    return {"model": model, "handlers_called": called}
