from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
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
        if "alarm_status" in device.properties_full:
            entities.append(NomaIQLeakSensor(coordinator, device.serial_number))

    async_add_entities(entities)

class NomaIQLeakSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a NOMA water leak sensor"""

    def __init__(self, coordinator: NomaIQDataUpdateCoordinator, serial_number: str):
        super().__init__(coordinator)
        self._serial = serial_number
        device = self._get_device()
        self._attr_name = device.name
        self._attr_unique_id = f"nomaiq_leak_{serial_number}"
        self._attr_device_class = BinarySensorDeviceClass.MOISTURE
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial_number)},
            name=device.name,
        )

    def _get_device(self) -> ayla_iot_unofficial.device.Device:
        """Look up the current device object from the coordinator."""
        return next(
            d for d in self.coordinator.data if d.serial_number == self._serial
        )

    @property
    def is_on(self) -> bool:
        """Return True if water is detected."""
        device = self._get_device()
        return bool(device.get_property_value("alarm_status"))