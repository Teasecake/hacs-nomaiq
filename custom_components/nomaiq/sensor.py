from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfElectricPotential
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NomaIQConfigEntry
from .const import DOMAIN
from .coordinator import NomaIQDataUpdateCoordinator
import ayla_iot_unofficial.device

async def async_setup_entry(hass, entry: NomaIQConfigEntry, async_add_entities):
    coordinator: NomaIQDataUpdateCoordinator = entry.runtime_data

    entities = []
    for device in coordinator.data:
        if "battery" in device.properties_full:
            entities.append(NomaIQBatterySensor(coordinator, device.serial_number))

    async_add_entities(entities)

class NomaIQBatterySensor(CoordinatorEntity, SensorEntity):
    """Battery level sensor for NOMA devices."""

    def __init__(self, coordinator: NomaIQDataUpdateCoordinator, serial_number: str):
        super().__init__(coordinator)
        self._serial = serial_number
        device = self._get_device()
        self._attr_name = f"{device.name} Battery"
        self._attr_unique_id = f"nomaiq_battery_{serial_number}"
        self._attr_device_class = SensorDeviceClass.VOLTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfElectricPotential.MILLIVOLT
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            name=device.name,
        )

    def _get_device(self) -> ayla_iot_unofficial.device.Device:
        return next(d for d in self.coordinator.data if d.serial_number == self._serial)

    @property
    def native_value(self):
        device = self._get_device()
        return device.get_property_value("battery")