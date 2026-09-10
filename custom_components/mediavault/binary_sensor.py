"""Release availability is read-only; never remotely install server updates."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.entity import EntityCategory

from .entity import MediaVaultEntity


async def async_setup_entry(hass, entry, async_add_entities):
    if entry.runtime_data.data["permissions"].get("server"):
        async_add_entities(
            [MediaVaultUpdate(entry.runtime_data, "update", "Update available")]
        )


class MediaVaultUpdate(MediaVaultEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.UPDATE
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def available(self):
        return (
            super().available
            and self.coordinator.data["permissions"].get("server", False)
            and (self.coordinator.data.get("updates") or {}).get("checkedAt")
            is not None
        )

    @property
    def is_on(self):
        return (self.coordinator.data.get("updates") or {}).get("updateAvailable")

    @property
    def extra_state_attributes(self):
        updates = self.coordinator.data.get("updates") or {}
        return {
            key: updates.get(key)
            for key in ("currentVersion", "latestVersion", "checkedAt")
        }
