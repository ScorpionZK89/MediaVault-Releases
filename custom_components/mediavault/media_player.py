"""Real MediaVault clients, never speculative players or optimistic state."""

import math
from typing import Any

from homeassistant.components.media_player import (
    BrowseMedia,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.components.media_player.browse_media import (
    SearchMedia,
    SearchMediaQuery,
)
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .api import MediaVaultError, identifier
from .const import DOMAIN

FEATURES = {
    "play": MediaPlayerEntityFeature.PLAY,
    "pause": MediaPlayerEntityFeature.PAUSE,
    "stop": MediaPlayerEntityFeature.STOP,
    "seek": MediaPlayerEntityFeature.SEEK,
    "play_media": MediaPlayerEntityFeature.PLAY_MEDIA,
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    added = set()

    def discover():
        entities = []
        for device in coordinator.data["devices"]:
            if device["id"] not in added:
                added.add(device["id"])
                entities.append(MediaVaultPlayer(coordinator, device))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class MediaVaultPlayer(CoordinatorEntity, MediaPlayerEntity):
    _attr_has_entity_name = True
    _attr_name = None
    _attr_media_image_remotely_accessible = False

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._id = device["id"]
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}:player:{self._id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=device["name"],
            manufacturer="MediaVault",
            model=device["clientType"],
            via_device=(DOMAIN, coordinator.config_entry.unique_id),
        )

    @property
    def device(self):
        return next(
            (
                item
                for item in self.coordinator.data["devices"]
                if item["id"] == self._id
            ),
            {},
        )

    @property
    def media(self):
        return self.coordinator.data.get("media", {}).get(
            self.device.get("mediaId"), {}
        )

    @property
    def available(self):
        return super().available and self.device.get("available", False)

    @property
    def state(self):
        return {
            "idle": MediaPlayerState.IDLE,
            "playing": MediaPlayerState.PLAYING,
            "paused": MediaPlayerState.PAUSED,
            "buffering": MediaPlayerState.BUFFERING,
        }.get(self.device.get("state"))

    @property
    def supported_features(self):
        features = (
            MediaPlayerEntityFeature.BROWSE_MEDIA
            | MediaPlayerEntityFeature.SEARCH_MEDIA
        )
        if self.coordinator.data["permissions"].get("control"):
            for action in self.device.get("commands", []):
                features |= FEATURES.get(action, MediaPlayerEntityFeature(0))
        return features

    @property
    def media_content_id(self):
        return self.device.get("mediaId")

    @property
    def media_content_type(self):
        return (
            MediaType.EPISODE
            if self.media.get("mediaType") in ("series", "episode")
            else MediaType.MOVIE
        )

    @property
    def media_title(self):
        return self.media.get("title")

    @property
    def media_series_title(self):
        return self.media.get("seriesTitle")

    @property
    def media_duration(self):
        return self.device.get("durationMs", 0) / 1000 or None

    @property
    def media_position(self):
        return self.device.get("positionMs", 0) / 1000

    @property
    def media_position_updated_at(self):
        value = self.device.get("updatedAt")
        return dt_util.parse_datetime(value) if value else None

    @property
    def media_image_url(self):
        # Used as the image-cache identity only. HA serves authenticated bytes below.
        return (
            f"{self.coordinator.api.url}/api/v1/home-assistant/artwork/{identifier(self.media_content_id)}"
            if self.media_content_id and self.media.get("posterUrl")
            else None
        )

    async def async_get_media_image(self):
        if not self.media_image_url:
            return None, None
        try:
            return await self.coordinator.api.artwork(self.media_content_id) or (
                None,
                None,
            )
        except MediaVaultError:
            return None, None

    async def _command(self, action, **parameters):
        if (
            not self.available
            or not self.coordinator.data["permissions"].get("control")
            or action not in self.device.get("commands", [])
        ):
            raise ServiceValidationError(
                "This player is unavailable or does not permit the action"
            )
        try:
            await self.coordinator.api.command(self._id, action, **parameters)
            await self.coordinator.async_request_refresh()
        except MediaVaultError as error:
            raise HomeAssistantError(str(error)) from error

    async def async_media_play(self):
        await self._command("play")

    async def async_media_pause(self):
        await self._command("pause")

    async def async_media_stop(self):
        await self._command("stop")

    async def async_media_seek(self, position):
        if not math.isfinite(position) or not 0 <= position <= 604800:
            raise ServiceValidationError("Invalid seek position")
        await self._command("seek", positionMs=round(position * 1000))

    async def async_play_media(self, media_type: str, media_id: str, **kwargs: Any):
        if (
            media_type
            not in (DOMAIN, MediaType.MOVIE, MediaType.EPISODE, MediaType.VIDEO)
            or kwargs.get("announce")
            or kwargs.get("enqueue") not in (None, "replace")
        ):
            raise ServiceValidationError(
                "Select a MediaVault library title; URLs and queues are unsupported"
            )
        identifier(media_id)
        await self._command("play_media", mediaId=media_id)

    async def async_search_media(self, query: SearchMediaQuery) -> SearchMedia:
        if len(query.search_query) > 200:
            raise ServiceValidationError("Search query is too long")
        try:
            items = await self.coordinator.api.media(query=query.search_query)
        except MediaVaultError as error:
            raise HomeAssistantError(str(error)) from error
        return SearchMedia(
            result=[
                BrowseMedia(
                    title=item["title"],
                    media_class="video",
                    media_content_id=item["id"],
                    media_content_type=DOMAIN,
                    can_play=bool(self.coordinator.data["permissions"].get("control")),
                    can_expand=False,
                )
                for item in items
            ]
        )

    async def async_browse_media(self, media_content_type=None, media_content_id=None):
        if media_content_type not in (None, DOMAIN):
            raise ServiceValidationError("Unsupported media browser")
        try:
            offset = int(media_content_id or "0")
            if not 0 <= offset <= 1_000_000:
                raise ValueError
        except ValueError as error:
            raise ServiceValidationError("Invalid library page") from error
        try:
            items = await self.coordinator.api.media(offset)
        except MediaVaultError as error:
            raise HomeAssistantError(str(error)) from error
        children = [
            BrowseMedia(
                title=item["title"],
                media_class="video",
                media_content_id=item["id"],
                media_content_type=DOMAIN,
                can_play=bool(self.coordinator.data["permissions"].get("control")),
                can_expand=False,
            )
            for item in items
        ]
        if len(items) == 100:
            children.append(
                BrowseMedia(
                    title="Next page",
                    media_class="directory",
                    media_content_type=DOMAIN,
                    media_content_id=str(offset + 100),
                    can_play=False,
                    can_expand=True,
                )
            )
        return BrowseMedia(
            title="MediaVault",
            media_class="directory",
            media_content_type=DOMAIN,
            media_content_id=str(offset),
            can_play=False,
            can_expand=True,
            children=children,
        )
