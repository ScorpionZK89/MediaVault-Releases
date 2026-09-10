"""Home Assistant integration for MediaVault."""

import voluptuous as vol
from homeassistant.const import CONF_URL
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MediaVaultApi, MediaVaultError, identifier
from .const import CONF_TOKEN, DOMAIN, PLATFORMS
from .coordinator import MediaVaultCoordinator


async def async_setup_entry(hass, entry):
    api = MediaVaultApi(
        async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_TOKEN]
    )
    coordinator = MediaVaultCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, "task_action"):

        async def task_action(call):
            target = hass.config_entries.async_get_entry(call.data["entry_id"])
            if (
                target is None
                or target.domain != DOMAIN
                or target.state.value != "loaded"
                or not hasattr(target, "runtime_data")
            ):
                raise ServiceValidationError("Select a loaded MediaVault integration")
            runtime = target.runtime_data
            if not runtime.data["permissions"].get("manage"):
                raise ServiceValidationError("This key does not allow task management")
            try:
                await runtime.api.request(
                    f"tasks/{identifier(call.data['task_id'])}/{call.data['action']}",
                    method="POST",
                )
                runtime._slow_at = 0
                await runtime.async_request_refresh()
            except MediaVaultError as error:
                raise HomeAssistantError(str(error)) from error

        hass.services.async_register(
            DOMAIN,
            "task_action",
            task_action,
            schema=vol.Schema(
                {
                    vol.Required("entry_id"): str,
                    vol.Required("task_id"): str,
                    vol.Required("action"): vol.In(["pause", "resume", "cancel"]),
                }
            ),
        )
    return True


async def async_unload_entry(hass, entry):
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded and not any(
        other.entry_id != entry.entry_id and other.state.value == "loaded"
        for other in hass.config_entries.async_entries(DOMAIN)
    ):
        hass.services.async_remove(DOMAIN, "task_action")
    return unloaded
