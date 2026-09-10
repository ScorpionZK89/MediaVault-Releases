"""Shared coordinator-backed server entities."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class MediaVaultEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, key, name):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.unique_id}:{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.unique_id)},
            name=f"MediaVault · {coordinator.data.get('profileName', 'Profile')}",
            manufacturer="MediaVault",
            model="Media server",
            sw_version=coordinator.data.get("version"),
            configuration_url=coordinator.api.url,
        )
