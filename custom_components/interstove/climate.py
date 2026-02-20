"""
Interstove HA - Climate Platform
Gestion de l'entité climate pour les poêles à pellets Interstove/Marina
et toutes marques compatibles Duepi EVO.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import socket
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval

from .const import (
    DOMAIN,
    MANUFACTURER,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
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
    DEFAULT_MIN_TEMP,
    DEFAULT_MAX_TEMP,
    TEMP_SOURCE_INTERNE,
    TEMP_SOURCE_ZIGBEE,
    TRAME_START,
    TRAME_END,
    CMD_STATUS,
    CMD_TEMPERATURE,
    CMD_ALLUMAGE,
    CMD_EXTINCTION,
    PUISSANCE_CMDS,
    ETAT_ETEINT,
    ETAT_ALLUME,
    ETAT_ALLUMAGE,
    ETATS_REFROIDISSEMENT,
    TCP_TIMEOUT,
    TCP_BUFFER_SIZE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configuration de la plateforme climate."""
    config = config_entry.data
    entity = InterstoveClimate(hass, config)
    async_add_entities([entity])


class InterstoveClimate(ClimateEntity):
    """Entité climate pour poêle à pellets Interstove/Duepi EVO."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
    )
    _attr_fan_modes = ["1", "2", "3", "4", "5"]
    _attr_min_temp = DEFAULT_MIN_TEMP
    _attr_max_temp = DEFAULT_MAX_TEMP
    _attr_target_temperature_step = 1.0

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        """Initialisation de l'entité."""
        self.hass = hass

        # Configuration
        self._host             = config[CONF_HOST]
        self._port             = config.get(CONF_PORT, DEFAULT_PORT)
        self._scan_interval    = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        self._temp_source      = config.get(CONF_TEMP_SOURCE, TEMP_SOURCE_INTERNE)
        self._temp_entity      = config.get(CONF_TEMP_ENTITY)
        self._delai_rallumage  = config.get(CONF_DELAI_RALLUMAGE, DEFAULT_DELAI_RALLUMAGE)
        self._puissance_min    = config.get(CONF_PUISSANCE_MIN, DEFAULT_PUISSANCE_MIN)
        self._puissance_max    = config.get(CONF_PUISSANCE_MAX, DEFAULT_PUISSANCE_MAX)
        self._hysteresis       = config.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS)

        # États internes
        self._hvac_mode        = HVACMode.OFF
        self._hvac_action      = HVACAction.OFF
        self._current_temp     = None
        self._target_temp      = 20.0
        self._fan_mode         = "3"
        self._etat_poele       = None
        self._puissance        = 3
        self._heure_extinction = None
        self._available        = False

        # Identifiant unique
        self._attr_unique_id   = f"interstove_{self._host}_{self._port}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self._attr_unique_id)},
            "name": "Poêle à Pellets",
            "manufacturer": MANUFACTURER,
            "model": "EVO LCD 7",
        }

    async def async_added_to_hass(self) -> None:
        """Démarrage de la mise à jour périodique."""
        await self.async_update()
        async_track_time_interval(
            self.hass,
            self._async_update_scheduled,
            datetime.timedelta(seconds=self._scan_interval),
        )

    async def _async_update_scheduled(self, now=None) -> None:
        """Mise à jour planifiée."""
        await self.async_update()
        self.async_write_ha_state()

    # ─────────────────────────────────────────
    # Propriétés HA
    # ─────────────────────────────────────────

    @property
    def available(self) -> bool:
        return self._available

    @property
    def hvac_mode(self) -> HVACMode:
        return self._hvac_mode

    @property
    def hvac_action(self) -> HVACAction:
        return self._hvac_action

    @property
    def current_temperature(self) -> float | None:
        return self._current_temp

    @property
    def target_temperature(self) -> float | None:
        return self._target_temp

    @property
    def fan_mode(self) -> str:
        return self._fan_mode

    @property
    def extra_state_attributes(self) -> dict:
        """Attributs supplémentaires exposés dans HA."""
        return {
            "etat_poele": self._etat_poele,
            "puissance": self._puissance,
            "host": self._host,
            "port": self._port,
            "heure_extinction": (
                self._heure_extinction.isoformat()
                if self._heure_extinction else None
            ),
        }

    # ─────────────────────────────────────────
    # Commandes HA
    # ─────────────────────────────────────────

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Allumage ou extinction du poêle."""
        if hvac_mode == HVACMode.HEAT:
            # Vérification délai de sécurité
            if not self._check_delai_rallumage():
                return
            await self._send_command(CMD_ALLUMAGE)
            self._hvac_mode = HVACMode.HEAT
        elif hvac_mode == HVACMode.OFF:
            await self._send_command(CMD_EXTINCTION)
            self._hvac_mode = HVACMode.OFF
            self._heure_extinction = datetime.datetime.now()
            _LOGGER.info(
                "Poêle éteint — délai de sécurité de %d min avant rallumage",
                self._delai_rallumage // 60
            )
        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Mise à jour de la consigne de température."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            self._target_temp = temp
            await self._reguler_puissance()
            self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Réglage manuel de la puissance."""
        puissance = int(fan_mode)
        puissance = max(self._puissance_min, min(self._puissance_max, puissance))
        await self._set_puissance(puissance)
        self._fan_mode = str(puissance)
        self.async_write_ha_state()

    # ─────────────────────────────────────────
    # Mise à jour
    # ─────────────────────────────────────────

    async def async_update(self) -> None:
        """Mise à jour de l'état du poêle."""
        try:
            # Lecture statut
            reponse_statut = await self._send_command(CMD_STATUS)
            if reponse_statut:
                self._parse_statut(reponse_statut)

            # Lecture température interne si configurée
            if self._temp_source == TEMP_SOURCE_INTERNE:
                reponse_temp = await self._send_command(CMD_TEMPERATURE)
                if reponse_temp:
                    self._parse_temperature(reponse_temp)

            # Lecture température Zigbee si configurée
            elif self._temp_source == TEMP_SOURCE_ZIGBEE and self._temp_entity:
                state = self.hass.states.get(self._temp_entity)
                if state and state.state not in ("unavailable", "unknown"):
                    self._current_temp = float(state.state)

            # Régulation automatique si poêle allumé
            if self._hvac_mode == HVACMode.HEAT:
                await self._reguler_puissance()

            self._available = True

        except Exception as e:
            _LOGGER.error("Erreur mise à jour Interstove: %s", e)
            self._available = False

    # ─────────────────────────────────────────
    # Régulation intelligente
    # ─────────────────────────────────────────

    async def _reguler_puissance(self) -> None:
        """Régulation automatique de la puissance selon l'écart de température."""
        if self._current_temp is None or self._target_temp is None:
            return

        ecart = self._target_temp - self._current_temp

        # Extinction automatique si consigne dépassée
        if ecart <= -self._hysteresis:
            if self._hvac_mode == HVACMode.HEAT:
                _LOGGER.info("Consigne atteinte → Extinction automatique")
                await self.async_set_hvac_mode(HVACMode.OFF)
            return

        # Allumage automatique si nécessaire
        if self._hvac_mode == HVACMode.OFF and ecart > self._hysteresis:
            if self._check_delai_rallumage():
                _LOGGER.info("Écart %.1f°C → Allumage automatique", ecart)
                await self.async_set_hvac_mode(HVACMode.HEAT)
            return

        # Calcul et application de la puissance
        puissance = self._calculer_puissance(ecart)
        if puissance != self._puissance:
            await self._set_puissance(puissance)

    def _calculer_puissance(self, ecart: float) -> int:
        """
        Calcule la puissance selon l'écart de température.

        Écart > 4°C  → puissance 5
        Écart 3-4°C  → puissance 4
        Écart 2-3°C  → puissance 3
        Écart 1-2°C  → puissance 2
        Écart < 1°C  → puissance 1
        """
        if ecart > 4.0:
            puissance = 5
        elif ecart > 3.0:
            puissance = 4
        elif ecart > 2.0:
            puissance = 3
        elif ecart > 1.0:
            puissance = 2
        else:
            puissance = 1

        return max(self._puissance_min, min(self._puissance_max, puissance))

    async def _set_puissance(self, puissance: int) -> None:
        """Envoie la commande de puissance au poêle."""
        cmd = PUISSANCE_CMDS.get(puissance)
        if cmd:
            await self._send_command(cmd)
            self._puissance = puissance
            self._fan_mode = str(puissance)
            _LOGGER.debug("Puissance réglée à %d/5", puissance)

    def _check_delai_rallumage(self) -> bool:
        """Vérifie si le délai de sécurité après extinction est écoulé."""
        if self._heure_extinction is None:
            return True
        elapsed = (datetime.datetime.now() - self._heure_extinction).total_seconds()
        restant = self._delai_rallumage - elapsed
        if restant > 0:
            _LOGGER.info(
                "Délai de sécurité : encore %d min avant rallumage",
                int(restant / 60)
            )
            return False
        return True

    # ─────────────────────────────────────────
    # Parsing des réponses
    # ─────────────────────────────────────────

    def _parse_statut(self, reponse: str) -> None:
        """Parse la réponse de statut du poêle."""
        self._etat_poele = reponse

        if reponse == ETAT_ETEINT:
            self._hvac_mode   = HVACMode.OFF
            self._hvac_action = HVACAction.OFF
        elif reponse == ETAT_ALLUME:
            self._hvac_mode   = HVACMode.HEAT
            self._hvac_action = HVACAction.HEATING
        elif reponse == ETAT_ALLUMAGE:
            self._hvac_mode   = HVACMode.HEAT
            self._hvac_action = HVACAction.PREHEATING
        elif reponse in ETATS_REFROIDISSEMENT:
            self._hvac_mode   = HVACMode.OFF
            self._hvac_action = HVACAction.COOLING
        else:
            _LOGGER.warning("Statut inconnu reçu: %s", reponse)

    def _parse_temperature(self, reponse: str) -> None:
        """
        Parse la réponse de température.
        Format : XXXX00YY → valeur hex / 10 = température en °C
        Exemple : 00E9003E → 0xE9 = 233 → 233/10 = 23.3°C
        """
        try:
            valeur_hex = reponse[:4]
            valeur_dec = int(valeur_hex, 16)
            self._current_temp = round(valeur_dec / 10, 1)
        except (ValueError, IndexError) as e:
            _LOGGER.error("Erreur parsing température: %s", e)

    # ─────────────────────────────────────────
    # Communication TCP
    # ─────────────────────────────────────────

    async def _send_command(self, cmd: str) -> str | None:
        """
        Envoie une commande au poêle via TCP et retourne la réponse.
        Format trame : <ESC>commande<&>
        """
        trame = f"{TRAME_START}{cmd}{TRAME_END}"
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=TCP_TIMEOUT,
            )
            writer.write(trame.encode())
            await writer.drain()

            data = await asyncio.wait_for(
                reader.read(TCP_BUFFER_SIZE),
                timeout=TCP_TIMEOUT,
            )
            writer.close()
            await writer.wait_closed()

            reponse = data.hex()
            _LOGGER.debug("CMD: %s → REP: %s", cmd, reponse)
            return reponse

        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout connexion ESP32 (%s:%s)", self._host, self._port)
            return None
        except ConnectionRefusedError:
            _LOGGER.warning("Connexion refusée ESP32 (%s:%s)", self._host, self._port)
            return None
        except Exception as e:
            _LOGGER.error("Erreur TCP: %s", e)
            return None
