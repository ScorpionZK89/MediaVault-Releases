"""Explicit incremental library scans for keys granted management access."""

from homeassistant.components.button import ButtonEntity
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory

from .api import MediaVaultError, identifier
from .entity import MediaVaultEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    added = set()

    def discover():
        if not coordinator.data["permissions"].get("manage"):
            return
        entities = []
        for library in coordinator.data.get("libraries") or []:
            if library["id"] not in added:
                added.add(library["id"])
                entities.append(MediaVaultScan(coordinator, library))
        async_add_entities(entities)

    discover()
    entry.async_on_unload(coordinator.async_add_listener(discover))


class MediaVaultScan(MediaVaultEntity, ButtonEntity):
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator, library):
        self._id = library["id"]
        super().__init__(coordinator, f"scan:{self._id}", f"Scan {library['name']}")

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.data["permissions"].get("manage", False)
            and any(
                item["id"] == self._id
                for item in self.coordinator.data.get("libraries") or []
            )
        )

    async def async_press(self):
        if not self.available:
            raise HomeAssistantError("Library management is unavailable")
        try:
            await self.coordinator.api.request(
                f"libraries/{identifier(self._id)}/scan", method="POST"
            )
            self.coordinator._slow_at = 0
            await self.coordinator.async_request_refresh()
        except MediaVaultError as error:
            raise HomeAssistantError(str(error)) from error
