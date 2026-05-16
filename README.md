# Scene Updater for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom integration for Home Assistant that allows you to dynamically overwrite your physical YAML scenes using a service call. 

Unlike the native `scene.create` service (which only stores scenes in memory until the next reboot), this integration directly updates the states and attributes of the entities inside your YAML files and reloads the scene integration, making your changes permanent.

## What's New in Version 3.0.0
* **UI Configuration (Config Flow):** Installation is now fully managed via the Home Assistant UI. No more editing `configuration.yaml` to set up the integration.
* **Dropdown Scene Selector:** The service call now uses a native entity selector (`scene_entity`) instead of requiring you to manually type the text name of the scene.
* **Atomic File Writing:** Writes to a temporary file first, seamlessly swapping it only upon success. This prevents file corruption in the event of a power outage or system crash.
* **Smart Attribute Preservation:** Safely updates core state and standard attributes (brightness, color, temperature, etc.) while preserving any custom, non-standard attributes you manually added to your YAML file in the past.

## Installation

### Via HACS (Recommended)
1. Open Home Assistant and navigate to **HACS**.
2. Search for "Scene Updater" in the Integrations tab. *(If not yet available in the default store, add this repository URL as a Custom Repository first).*
3. Click **Download**.
4. Restart Home Assistant.
5. Navigate to **Settings > Devices & Services**.
6. Click **Add Integration** in the bottom right corner.
7. Search for **Scene Updater** and click it to instantly enable the integration.

### Manual Installation
1. Download the `custom_components/scene_updater` folder from this repository.
2. Copy it into your Home Assistant `<config>/custom_components/` directory.
3. Restart Home Assistant.
4. Follow steps 5-7 above to enable it via the UI.

## Usage

This integration creates a new service: `scene_updater.save_scene`. 

You can call this service from Developer Tools, Automations, or Dashboard Buttons.

### Parameters

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `scene_entity` | Yes | The entity ID of the scene you want to update (e.g., `scene.living_room_relax`). |
| `file_path` | No | The path to the YAML file where the scene lives. Defaults to `scenes.yaml`. Useful if you use split configuration files. |

### Example Dashboard Button
```yaml
type: button
name: Save Living Room Scene
icon: mdi:content-save-cog
tap_action:
  action: scene_updater.save_scene
  data:
    scene_entity: scene.living_room_relax
    file_path: "scenes.yaml" # Optional
