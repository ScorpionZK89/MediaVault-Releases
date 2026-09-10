"""UI setup, credential replacement and server address changes."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_URL
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import MediaVaultApi, MediaVaultAuthError, MediaVaultError, normalize_url
from .const import CONF_TOKEN, DOMAIN


class MediaVaultConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return await self._form("user", user_input)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        return await self._form("reauth_confirm", user_input)

    async def async_step_reconfigure(self, user_input=None):
        return await self._form("reconfigure", user_input)

    async def _form(self, step, user_input):
        errors = {}
        entry = (
            self._get_reauth_entry()
            if step == "reauth_confirm"
            else self._get_reconfigure_entry()
            if step == "reconfigure"
            else None
        )
        if user_input is not None:
            try:
                data = {
                    CONF_URL: normalize_url(user_input[CONF_URL]),
                    CONF_TOKEN: user_input[CONF_TOKEN].strip(),
                }
                api = MediaVaultApi(
                    async_get_clientsession(self.hass), data[CONF_URL], data[CONF_TOKEN]
                )
                status = await api.status()
                unique_id = f"{status['serverId']}:{status['profileId']}"
                if entry:
                    if unique_id != entry.unique_id:
                        errors["base"] = "wrong_account"
                    else:
                        return self.async_update_reload_and_abort(
                            entry, data_updates=data
                        )
                else:
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"MediaVault · {status.get('profileName', 'Profile')}",
                        data=data,
                    )
            except MediaVaultAuthError:
                errors["base"] = "invalid_auth"
            except MediaVaultError:
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_url"
        return self.async_show_form(
            step_id=step,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL, default=entry.data[CONF_URL] if entry else "http://"
                    ): str,
                    vol.Required(CONF_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
            errors=errors,
        )
