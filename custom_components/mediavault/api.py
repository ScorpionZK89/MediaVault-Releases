"""Bounded, authenticated MediaVault transport; credentials never enter URLs."""

import asyncio
import re
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit
from uuid import uuid4

import aiohttp


class MediaVaultError(Exception):
    """An actionable transport or command failure, without secret details."""


class MediaVaultAuthError(MediaVaultError):
    """The integration credential is no longer valid."""


def normalize_url(value: str) -> str:
    """Allow a server base URL, never credentials, query parameters or fragments."""
    url = urlsplit(value.strip())
    if (
        url.scheme not in ("http", "https")
        or not url.hostname
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or url.path not in ("", "/")
    ):
        raise ValueError("Enter the server's HTTP(S) base URL without a path")
    _ = url.port  # Validate malformed/out-of-range ports.
    return urlunsplit((url.scheme, url.netloc, "", "", ""))


def identifier(value: str) -> str:
    """IDs are opaque local identifiers, not URLs or paths."""
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,160}", value):
        raise MediaVaultError("Invalid MediaVault identifier")
    return quote(value, safe="")


class MediaVaultApi:
    def __init__(self, session: aiohttp.ClientSession, url: str, token: str) -> None:
        self.session = session
        self.url = normalize_url(url)
        self._token = token.strip()
        if not self._token.startswith("mvha_") or len(self._token) > 128:
            raise MediaVaultAuthError("Use a MediaVault Home Assistant integration key")

    async def request(
        self,
        path: str,
        *,
        method: str = "GET",
        body=None,
        params=None,
        image: bool = False,
    ) -> Any:
        try:
            async with asyncio.timeout(15):
                async with self.session.request(
                    method,
                    f"{self.url}/api/v1/home-assistant/{path}",
                    headers={"Authorization": f"Bearer {self._token}"},
                    json=body,
                    params=params,
                    allow_redirects=False,
                ) as response:
                    if response.status == 401:
                        raise MediaVaultAuthError(
                            "MediaVault integration key was rejected"
                        )
                    if response.status == 403:
                        raise MediaVaultError(
                            "This integration key does not permit the action"
                        )
                    if image and response.status == 404:
                        return None
                    if response.status not in (200, 202, 204):
                        raise MediaVaultError(
                            f"MediaVault request failed (HTTP {response.status})"
                        )
                    if image:
                        content_type = response.headers.get("Content-Type", "").split(
                            ";"
                        )[0]
                        if content_type not in (
                            "image/jpeg",
                            "image/png",
                            "image/webp",
                        ):
                            raise MediaVaultError("Invalid artwork type")
                        data = bytearray()
                        async for chunk in response.content.iter_chunked(65536):
                            data.extend(chunk)
                            if len(data) > 10 * 1024 * 1024:
                                raise MediaVaultError("Artwork exceeds size limit")
                        return bytes(data), content_type
                    if response.status == 204 or response.content_length == 0:
                        return None
                    return await response.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as error:
            raise MediaVaultError("Cannot communicate with MediaVault") from error

    async def status(self) -> dict:
        result = await self.request("status")
        if (
            not isinstance(result, dict)
            or result.get("apiVersion") != 1
            or not all(
                result.get(key) for key in ("serverId", "profileId", "permissions")
            )
            or not isinstance(result.get("devices"), list)
        ):
            raise MediaVaultError("Unsupported MediaVault Home Assistant API")
        return result

    async def command(self, device_id: str, action: str, **parameters) -> None:
        """No automatic POST retries: avoid replaying playback after a timeout."""
        result = await self.request(
            f"devices/{identifier(device_id)}/commands",
            method="POST",
            body={"requestId": str(uuid4()), "action": action, **parameters},
        )
        try:
            async with asyncio.timeout(125 if action in ("play_media", "seek") else 20):
                while result["status"] in ("queued", "delivered"):
                    await asyncio.sleep(0.5)
                    result = await self.request(f"commands/{identifier(result['id'])}")
                if result["status"] != "succeeded":
                    raise MediaVaultError("The player did not complete the command")
        except TimeoutError as error:
            raise MediaVaultError(
                "The player did not confirm the command in time"
            ) from error

    async def media(self, offset: int = 0, query: str = "") -> list[dict]:
        return await self.request(
            "media", params={"limit": 100, "offset": offset, "query": query}
        )

    async def artwork(self, media_id: str):
        return await self.request(f"artwork/{identifier(media_id)}", image=True)
