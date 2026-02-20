"""
Interstove HA - Config Flow
Interface graphique de configuration de l'intégration.
"""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_BRIDGE_TYPE,
    CONF_TEMP_SOURCE,
    CONF_TEMP_ENTITY,
    CONF_DELAI_RALLUMAGE,
    CONF_PUISSANCE_MIN,
    CONF_PUISSANCE_MAX,
    CONF_HYSTERESIS,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_DELAI_RALLUMAGE,
    DEFAULT_PUISSANCE_MIN,
    DEFAULT_PUISSANCE_MAX,
    DEFAULT_HYSTERESIS,
    BRIDGE_ESPLINK,
    BRIDGE_ESPHOME,
    BRIDGE_TYPES,
    TEMP_SOURCE_INTERNE,
    TEMP_SOURCE_ZIGBEE,
    TEMP_SOURCES,
    TCP_TIMEOUT,
    TRAME_START,
    CMD_STATUS,
    TRAME_END,
)

_LOGGER = logging.getLogger(__name__)


async def _test_connection(host: str, port: int) -> bool:
    """Teste la connexion TCP vers l'ESP32."""
    try:
        trame = f"{TRAME_START}{CMD_STATUS}{TRAME_END}"
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=TCP_TIMEOUT,
        )
        writer.write(trame.encode())
        await writer.drain()
        data = await asyncio.wait_for(reader.read(10), timeout=TCP_TIMEOUT)
        writer.close()
        await writer.wait_closed()
        return len(data) > 0
    except Exception:
        return False


class InterstoveConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Flux de configuration de l'intégration Interstove."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialisation."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 1 : Connexion à l'ESP32."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Test de connexion
            ok = await _test_connection(host, port)
            if ok:
                self._data.update(user_input)
                return await self.async_step_temperature()
            else:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
            vol.Required(CONF_BRIDGE_TYPE, default=BRIDGE_ESPLINK): vol.In(BRIDGE_TYPES),
            vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_temperature(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 2 : Source de température."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)

            # Si Zigbee, demander l'entité
            if user_input[CONF_TEMP_SOURCE] == TEMP_SOURCE_ZIGBEE:
                return await self.async_step_zigbee()

            return await self.async_step_regulation()

        schema = vol.Schema({
            vol.Required(CONF_TEMP_SOURCE, default=TEMP_SOURCE_INTERNE): vol.In(TEMP_SOURCES),
        })

        return self.async_show_form(
            step_id="temperature",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_zigbee(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 3 (optionnelle) : Entité Zigbee."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entity = user_input.get(CONF_TEMP_ENTITY, "")
            # Vérification que l'entité existe dans HA
            state = self.hass.states.get(entity)
            if state is None:
                errors[CONF_TEMP_ENTITY] = "entity_not_found"
            else:
                self._data.update(user_input)
                return await self.async_step_regulation()

        schema = vol.Schema({
            vol.Required(CONF_TEMP_ENTITY): str,
        })

        return self.async_show_form(
            step_id="zigbee",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_regulation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Étape 4 : Paramètres de régulation."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=f"Poêle Pellets ({self._data[CONF_HOST]})",
                data=self._data,
            )

        schema = vol.Schema({
            vol.Required(CONF_PUISSANCE_MIN, default=DEFAULT_PUISSANCE_MIN): vol.In([1, 2, 3, 4, 5]),
            vol.Required(CONF_PUISSANCE_MAX, default=DEFAULT_PUISSANCE_MAX): vol.In([1, 2, 3, 4, 5]),
            vol.Required(CONF_HYSTERESIS, default=DEFAULT_HYSTERESIS): vol.Coerce(float),
            vol.Required(CONF_DELAI_RALLUMAGE, default=DEFAULT_DELAI_RALLUMAGE): int,
        })

        return self.async_show_form(
            step_id="regulation",
            data_schema=schema,
        )
