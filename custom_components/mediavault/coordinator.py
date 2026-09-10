"""A single bounded poll per configured profile; slow server diagnostics separately."""

import logging
from datetime import timedelta
from time import monotonic

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MediaVaultAuthError, MediaVaultError

LOGGER = logging.getLogger(__name__)


class MediaVaultCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry, api):
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name="MediaVault",
            update_interval=timedelta(seconds=5),
        )
        self.api = api
        self._slow_at = 0.0
        self._slow = {}

    async def _async_update_data(self):
        try:
            data = await self.api.status()
            if f"{data['serverId']}:{data['profileId']}" != self.config_entry.unique_id:
                raise ConfigEntryAuthFailed(
                    "The server or profile changed; reconfigure MediaVault"
                )
            if data["permissions"].get("server"):
                if monotonic() >= self._slow_at:
                    self._slow_at = monotonic() + 60
                    for path in ("activity", "updates"):
                        try:
                            self._slow[path] = await self.api.request(path)
                        except MediaVaultAuthError:
                            raise
                        except MediaVaultError:
                            self._slow[path] = None
                data.update(self._slow)
            else:
                self._slow.clear()
            return data
        except MediaVaultAuthError as error:
            raise ConfigEntryAuthFailed(str(error)) from error
        except MediaVaultError as error:
            raise UpdateFailed(str(error)) from error
