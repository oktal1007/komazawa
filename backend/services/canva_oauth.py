"""Canva OAuth 2.0 + PKCE トークン管理サービス"""

import base64
import hashlib
import json
import os
import secrets
import time
from pathlib import Path
from typing import Optional

import httpx

CANVA_AUTH_URL = "https://www.canva.com/api/oauth/authorize"
CANVA_TOKEN_URL = "https://api.canva.com/rest/v1/oauth/token"

# このシステムで必要なスコープ
REQUIRED_SCOPES = (
    "design:content:read design:content:write "
    "design:meta:read "
    "asset:read asset:write "
    "brandtemplate:meta:read brandtemplate:content:read "
    "folder:read folder:write "
    "profile:read"
)

TOKEN_FILE = Path(__file__).resolve().parent.parent / ".canva_tokens.json"


def _generate_code_verifier() -> str:
    """PKCE code_verifier を生成（43-128文字のURL-safe文字列）"""
    return secrets.token_urlsafe(96)[:128]


def _generate_code_challenge(verifier: str) -> str:
    """code_verifier から code_challenge (S256) を生成"""
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


class CanvaOAuth:
    """Canva OAuth 2.0 + PKCE フロー管理"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self._pending_verifiers: dict[str, str] = {}

    def get_authorization_url(self) -> dict:
        """認可URLを生成。state と code_verifier を返す"""
        code_verifier = _generate_code_verifier()
        code_challenge = _generate_code_challenge(code_verifier)
        state = secrets.token_urlsafe(32)

        self._pending_verifiers[state] = code_verifier

        url = (
            f"{CANVA_AUTH_URL}"
            f"?code_challenge={code_challenge}"
            f"&code_challenge_method=S256"
            f"&scope={REQUIRED_SCOPES}"
            f"&response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
        )

        return {"authorization_url": url, "state": state}

    async def exchange_code(self, code: str, state: str) -> dict:
        """認可コードをアクセストークンに交換"""
        code_verifier = self._pending_verifiers.pop(state, None)
        if not code_verifier:
            raise ValueError("Invalid or expired state parameter")

        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                CANVA_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        token_data["obtained_at"] = int(time.time())
        _save_tokens(token_data)
        return token_data

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """リフレッシュトークンでアクセストークンを更新"""
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                CANVA_TOKEN_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()
            token_data = response.json()

        token_data["obtained_at"] = int(time.time())
        _save_tokens(token_data)
        return token_data

    async def get_valid_access_token(self) -> Optional[str]:
        """有効なアクセストークンを取得。期限切れなら自動リフレッシュ"""
        tokens = _load_tokens()
        if not tokens:
            return None

        obtained_at = tokens.get("obtained_at", 0)
        expires_in = tokens.get("expires_in", 14400)
        # 5分のバッファを持たせて期限切れ判定
        if time.time() > obtained_at + expires_in - 300:
            refresh_token = tokens.get("refresh_token")
            if not refresh_token:
                return None
            tokens = await self.refresh_access_token(refresh_token)

        return tokens.get("access_token")


def _save_tokens(token_data: dict) -> None:
    """トークンをファイルに保存"""
    TOKEN_FILE.write_text(json.dumps(token_data, indent=2), encoding="utf-8")


def _load_tokens() -> Optional[dict]:
    """保存済みトークンを読み込み"""
    if not TOKEN_FILE.exists():
        return None
    try:
        return json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
