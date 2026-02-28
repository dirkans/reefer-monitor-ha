import logging
from datetime import timedelta
import aiohttp
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_HOST, CONF_USERNAME, CONF_PASSWORD

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class ReeferCoordinator(DataUpdateCoordinator):
    """El cerebro que busca los datos a tu API y auto-renueva tokens."""

    def __init__(self, hass, entry):
        super().__init__(
            hass,
            _LOGGER,
            name="Reefer Monitor Data",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self.host = entry.data[CONF_HOST]
        self.username = entry.data[CONF_USERNAME]
        self.password = entry.data[CONF_PASSWORD]
        self.session = async_get_clientsession(hass)
        self.token = None 

    async def _get_valid_token(self):
        """Se loguea por detrás y consigue un token fresco."""
        data = aiohttp.FormData()
        data.add_field('username', self.username)
        data.add_field('password', self.password)
        
        async with self.session.post(f"{self.host}/token", data=data, timeout=10) as res:
            if res.status == 200:
                json_resp = await res.json()
                self.token = json_resp["access_token"]
                return self.token
            else:
                raise UpdateFailed("Error de autenticación: Usuario o contraseña cambiados.")

    async def _async_update_data(self):
        """Buscar los datos de la API cada 30 segundos."""
        if not self.token:
            await self._get_valid_token()

        headers = {"Authorization": f"Bearer {self.token}"}
        data = {}
        
        try:
            async with self.session.get(f"{self.host}/my/devices", headers=headers, timeout=10) as res:
                if res.status == 401:
                    _LOGGER.info("El token de Reefer Monitor venció. Renovando automáticamente...")
                    await self._get_valid_token()
                    headers = {"Authorization": f"Bearer {self.token}"}
                    res = await self.session.get(f"{self.host}/my/devices", headers=headers, timeout=10)
                
                if res.status != 200:
                    raise UpdateFailed(f"Error HTTP obteniendo equipos: {res.status}")
                devices = await res.json()

            for dev in devices:
                dev_id = dev["device_id"]
                async with self.session.get(f"{self.host}/api/estado_actual/{dev_id}", headers=headers, timeout=10) as res_est:
                    if res_est.status == 200:
                        estado_json = await res_est.json()
                        estado_json["segundos_atras"] = dev.get("segundos_atras") 
                        data[dev_id] = estado_json
                        
            return data
            
        except Exception as err:
            raise UpdateFailed(f"Error de conexión con Reefer Monitor: {err}")