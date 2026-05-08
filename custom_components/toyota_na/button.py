"""Button platform for Toyota (North America)."""

import logging
from typing import Any

from toyota_na.vehicle.base_vehicle import ToyotaVehicle

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .base_entity import ToyotaNABaseEntity
from .const import COMMAND_MAP, DOMAIN, ENGINE_START, ENGINE_STOP, HAZARDS_ON, HAZARDS_OFF

_LOGGER = logging.getLogger(__name__)

BUTTONS = [
    {
        "key": ENGINE_START,
        "name": "Engine Start",
        "icon": "mdi:engine",
    },
    {
        "key": ENGINE_STOP,
        "name": "Engine Stop",
        "icon": "mdi:engine-off",
    },
    {
        "key": HAZARDS_ON,
        "name": "Hazards On",
        "icon": "mdi:hazard-lights",
    },
    {
        "key": HAZARDS_OFF,
        "name": "Hazards Off",
        "icon": "mdi:car-light-dimmed",
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
):
    """Set up the button platform."""
    buttons = []

    coordinator: DataUpdateCoordinator[list[ToyotaVehicle]] = hass.data[DOMAIN][
        config_entry.entry_id
    ]["coordinator"]

    for vehicle in coordinator.data:
        if vehicle.subscribed is False:
            continue
        for button_def in BUTTONS:
            buttons.append(
                ToyotaButton(
                    button_def["key"],
                    button_def["name"],
                    button_def["icon"],
                    coordinator,
                    button_def["name"],
                    vehicle.vin,
                )
            )

    async_add_devices(buttons, True)


class ToyotaButton(ToyotaNABaseEntity, ButtonEntity):
    """Button entity for Toyota remote commands."""

    def __init__(
        self,
        command_key: str,
        button_name: str,
        icon: str,
        *args: Any,
    ):
        super().__init__(*args)
        self._command_key = command_key
        self._button_name = button_name
        self._icon = icon

    @property
    def icon(self):
        return self._icon

    async def async_press(self) -> None:
        """Handle the button press."""
        if self.vehicle is not None:
            await self.vehicle.send_command(COMMAND_MAP[self._command_key])

    @property
    def available(self):
        return self.vehicle is not None
