"""Constants for Interstove HA integration."""

# Nom du domaine de l'intégration
DOMAIN = "interstove"

# Version
VERSION = "1.0.0"

# Informations du fabricant
MANUFACTURER = "Interstove / Marina"

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────

CONF_HOST              = "host"
CONF_PORT              = "port"
CONF_SCAN_INTERVAL     = "scan_interval"
CONF_BRIDGE_TYPE       = "bridge_type"
CONF_TEMP_SOURCE       = "temp_source"
CONF_TEMP_ENTITY       = "temp_entity"
CONF_DELAI_RALLUMAGE   = "delai_rallumage"
CONF_PUISSANCE_MIN     = "puissance_min"
CONF_PUISSANCE_MAX     = "puissance_max"
CONF_HYSTERESIS        = "hysteresis"

# ─────────────────────────────────────────
# Valeurs par défaut
# ─────────────────────────────────────────

DEFAULT_PORT             = 2000
DEFAULT_SCAN_INTERVAL    = 60       # secondes
DEFAULT_DELAI_RALLUMAGE  = 1800     # secondes (30 min)
DEFAULT_PUISSANCE_MIN    = 1
DEFAULT_PUISSANCE_MAX    = 5
DEFAULT_HYSTERESIS       = 0.5      # °C
DEFAULT_MIN_TEMP         = 15.0     # °C
DEFAULT_MAX_TEMP         = 30.0     # °C

# ─────────────────────────────────────────
# Types de bridge
# ─────────────────────────────────────────

BRIDGE_ESPLINK   = "esp_link"
BRIDGE_ESPHOME   = "esphome"

BRIDGE_TYPES = [BRIDGE_ESPLINK, BRIDGE_ESPHOME]

# ─────────────────────────────────────────
# Sources de température
# ─────────────────────────────────────────

TEMP_SOURCE_INTERNE = "interne"   # Sonde interne du poêle
TEMP_SOURCE_ZIGBEE  = "zigbee"    # Sonde Zigbee externe

TEMP_SOURCES = [TEMP_SOURCE_INTERNE, TEMP_SOURCE_ZIGBEE]

# ─────────────────────────────────────────
# Protocole série du poêle
# ─────────────────────────────────────────

# Caractères de trame
TRAME_START = "\x1b"   # ESC
TRAME_END   = "&"

# Commandes
CMD_STATUS      = "RDA909005f"   # Lecture statut
CMD_TEMPERATURE = "RD100057"     # Lecture température ambiante
CMD_ALLUMAGE    = "RF001059"     # Allumage
CMD_EXTINCTION  = "RF000058"     # Extinction

# Réponse acquittement
ACK = "00000020"

# ─────────────────────────────────────────
# États du poêle
# ─────────────────────────────────────────

ETAT_ETEINT         = "00f9003f"   # Éteint, prêt à allumer
ETAT_ALLUME         = "00000000"   # En chauffe
ETAT_ALLUMAGE       = "01010022"   # Phase d'allumage
ETAT_REFROID_1      = "0802002a"   # Refroidissement
ETAT_REFROID_2      = "08010029"   # Refroidissement

ETATS_REFROIDISSEMENT = [ETAT_REFROID_1, ETAT_REFROID_2]

# ─────────────────────────────────────────
# Commandes de puissance (1 à 5)
# ─────────────────────────────────────────

PUISSANCE_CMDS = {
    1: "RF001059",
    2: "RF00205A",
    3: "RF00305B",
    4: "RF00405C",
    5: "RF00505D",
}

# ─────────────────────────────────────────
# Communication TCP
# ─────────────────────────────────────────

TCP_TIMEOUT        = 5    # secondes
TCP_BUFFER_SIZE    = 10   # bytes
