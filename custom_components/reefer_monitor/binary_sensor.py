from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configurar el sensor de conexión."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    
    for device_id in coordinator.data.keys():
        entities.append(ReeferConnectionSensor(coordinator, device_id))
        
    async_add_entities(entities)

class ReeferConnectionSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(self, coordinator, device_id):
        super().__init__(coordinator)
        self._device_id = device_id
        
        self._attr_name = f"{device_id} Conexión"
        self._attr_unique_id = f"reefer_{device_id}_conexion"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Reefer {self._device_id.capitalize()}",
            "manufacturer": "Dirkans IoT",
            "model": "Reefer Monitor Pro v1",
        }

    @property
    def is_on(self):
        """Devuelve True si está conectado (menos de 65 seg), False si se cayó."""
        data = self.coordinator.data.get(self._device_id, {})
        segundos = data.get("segundos_atras")
        
        if segundos is not None and segundos < 65:
            return True
        return False