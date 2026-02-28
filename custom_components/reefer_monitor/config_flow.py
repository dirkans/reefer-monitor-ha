import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD
import aiohttp

from .const import DOMAIN

class ReeferMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            data = aiohttp.FormData()
            data.add_field('username', user_input[CONF_USERNAME])
            data.add_field('password', user_input[CONF_PASSWORD])

            try:
                async with aiohttp.ClientSession() as session:
                    login_url = f"{user_input[CONF_HOST]}/token"
                    
                    async with session.post(login_url, data=data, timeout=10) as res:
                        if res.status == 200:
                            return self.async_create_entry(
                                title=f"Reefer ({user_input[CONF_USERNAME]})", 
                                data=user_input
                            )
                        elif res.status == 401:
                            errors["base"] = "invalid_auth"
                        else:
                            errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST, default="https://reefermonitor.com.ar"): str,
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)