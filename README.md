# 🔥 Interstove HA

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.1%2B-blue)](https://www.home-assistant.io/)

Intégration Home Assistant pour les poêles à pellets **Interstove / Marina** et toutes marques compatibles **Duepi EVO**.

Contrôle 100% **local**, sans cloud, via un bridge ESP32 (ESP-Link ou ESPHome).

---

## 🇫🇷 Français

### Fonctionnalités

- ✅ Allumage / Extinction automatique
- ✅ Régulation intelligente de la puissance (1 à 5)
- ✅ Lecture température ambiante (sonde interne ou Zigbee)
- ✅ Lecture état du poêle (allumé, éteint, allumage, refroidissement)
- ✅ Délai de sécurité configurable avant rallumage
- ✅ Configuration via interface graphique (config flow)
- ✅ Dashboard Lovelace inclus
- ✅ 100% local, zéro cloud

### Marques compatibles

- Interstove / Marina
- Duroflame (Carré, Pelle, Rembrand)
- AMG / Artel / Kalor / Tepor / Foco
- Casatelli Leonardo
- FireShop Dinamica
- Qlima Viola
- Wamsler Westminster
- Et toutes marques compatibles Duepi EVO

### Matériel nécessaire

- **ESP32** (ex: ESP32-WROOM-32)
- **Level shifter 3.3V/5V** bidirectionnel 4 canaux (BSS138)
- **Câbles Dupont**

### Installation matérielle

Connecter l'ESP32 au connecteur **JP8** du poêle via le level shifter :

| JP8 Poêle | Level Shifter | ESP32 |
|---|---|---|
| Broche 1 - GND | GND HV | GND |
| Broche 2 - RX | HV1 → LV1 | GPIO17 (TX2) |
| Broche 3 - TX | HV2 → LV2 | GPIO16 (RX2) |
| Broche 4 - +5V | HV + VIN ESP32 | VIN |

### Flash de l'ESP32

#### Option 1 : ESP-Link (recommandé)
Flasher l'ESP32 via : https://aceindy.github.io/esp-link/

Paramètres : 115200 baud, 8N1, port TCP 2000

#### Option 2 : ESPHome
Utiliser la config fournie dans le dossier `esphome/`.

### Installation HACS

1. Dans HACS → Intégrations → Menu → Dépôts personnalisés
2. Ajouter l'URL de ce dépôt, catégorie **Intégration**
3. Installer **Interstove Pellet Stove**
4. Redémarrer Home Assistant
5. Paramètres → Intégrations → Ajouter → **Interstove**

### Configuration

L'intégration se configure via l'interface graphique en 4 étapes :

1. **Connexion** : IP de l'ESP32, port (défaut: 2000), type de bridge
2. **Température** : source interne ou sonde Zigbee
3. **Sonde Zigbee** : entité HA (si choix Zigbee)
4. **Régulation** : puissance min/max, hystérésis, délai rallumage

### Dashboard Lovelace

Importer le fichier `lovelace/dashboard.yaml` dans votre tableau de bord.

---

## 🇬🇧 English

### Features

- ✅ Automatic ignition / shutdown
- ✅ Intelligent power regulation (1 to 5)
- ✅ Ambient temperature reading (internal sensor or Zigbee)
- ✅ Stove status reading (on, off, igniting, cooling)
- ✅ Configurable safety delay before re-ignition
- ✅ GUI configuration (config flow)
- ✅ Lovelace dashboard included
- ✅ 100% local, no cloud

### Hardware required

- **ESP32** (e.g. ESP32-WROOM-32)
- **3.3V/5V bidirectional level shifter** (BSS138, 4 channels)
- **Dupont wires**

### Hardware installation

Connect the ESP32 to the stove's **JP8** connector via the level shifter:

| JP8 Stove | Level Shifter | ESP32 |
|---|---|---|
| Pin 1 - GND | GND HV | GND |
| Pin 2 - RX | HV1 → LV1 | GPIO17 (TX2) |
| Pin 3 - TX | HV2 → LV2 | GPIO16 (RX2) |
| Pin 4 - +5V | HV + ESP32 VIN | VIN |

### ESP32 Flashing

#### Option 1: ESP-Link (recommended)
Flash via: https://aceindy.github.io/esp-link/

Settings: 115200 baud, 8N1, TCP port 2000

#### Option 2: ESPHome
Use the config provided in the `esphome/` folder.

### HACS Installation

1. In HACS → Integrations → Menu → Custom repositories
2. Add this repository URL, category **Integration**
3. Install **Interstove Pellet Stove**
4. Restart Home Assistant
5. Settings → Integrations → Add → **Interstove**

### Credits

- Protocol reverse engineering: [Pascal Bornat](mailto:pascal_bornat@hotmail.com)
- Duepi EVO integration: [aceindy](https://github.com/aceindy/Duepi_EVO)
- Interstove HA: Community contribution

---

⭐ Si ce projet vous est utile, n'hésitez pas à laisser une étoile sur GitHub !
