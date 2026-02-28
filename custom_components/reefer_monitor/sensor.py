from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature, UnitOfElectricCurrent
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Configurar los sensores físicos en Home Assistant."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    for device_id, device_data in coordinator.data.items():
        # Sensores de Temperatura
        entities.append(ReeferSensor(coordinator, device_id, "temperatura", "Return", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS))
        entities.append(ReeferSensor(coordinator, device_id, "temp_supply", "Supply", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS))
        entities.append(ReeferSensor(coordinator, device_id, "temp_evap", "Evaporador", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS))
        
        # Sensores de Amperaje
        entities.append(ReeferSensor(coordinator, device_id, "amp_r", "Amp R", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE))
        entities.append(ReeferSensor(coordinator, device_id, "amp_s", "Amp S", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE))
        entities.append(ReeferSensor(coordinator, device_id, "amp_t", "Amp T", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE))
        
    async_add_entities(entities)

class ReeferSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, device_id, key_json, name, device_class, unit):
        super().__init__(coordinator)
        self._device_id = device_id
        self._key = key_json
        
        self._attr_name = f"{device_id} {name}"
        self._attr_unique_id = f"reefer_{device_id}_{key_json}"
        
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"Reefer {self._device_id.capitalize()}",
            "manufacturer": "Dirkans IoT",
            "model": "Reefer Monitor Pro v1",
        }

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._device_id, {})
        lectura = data.get("lectura", {})
        
        if not lectura:
            return None
            
        return lectura.get(self._key)