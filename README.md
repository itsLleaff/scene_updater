# Scene Updater for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom integration for Home Assistant that allows you to dynamically overwrite your physical YAML scenes using a service call. 

Unlike the native `scene.create` service (which only stores scenes in memory until the next reboot), this integration directly updates the states and attributes of the entities inside your YAML files and reloads the scene integration, making your changes permanent.

## Version 2.1 Features
* **Atomic File Writing:** Writes to a temporary file first, seamlessly swapping it only upon success. This prevents file corruption in the event of a power outage or system crash during the save process.
* **Smart Attribute Preservation:** Safely updates core state and standard attributes (brightness, color, temperature, etc.) while preserving any custom, non-standard attributes you manually added to your YAML file in the past.
* **Path Traversal Security:** Strictly validates file paths to ensure writes are contained exclusively within your Home Assistant configuration directory.

## Installation via HACS (Custom Repository)
1. Open Home Assistant and navigate to **HACS**.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add the URL of this repository (`https://github.com/itsLleaff/scene_updater`) and select **Integration** as the category.
4. Click **Add**, then close the modal. 
5. Search for "Scene Updater" in HACS, click it, and click **Download**.
6. Restart Home Assistant.

## Usage

This integration creates a new service: `scene_updater.save_scene`. 

### Parameters

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `scene_name` | Yes | The friendly name of the scene exactly as it appears in your YAML file (e.g., `Living Room Relax`). |
| `file_path` | No | The path to the YAML file where the scene lives. Defaults to `scenes.yaml`. Useful if you use split configuration files. |

### Example Dashboard Button
```yaml
type: button
name: Save Living Room Scene
icon: mdi:content-save
tap_action:
  action: scene_updater.save_scene
  data:
    scene_name: "Living Room Relax"
    file_path: "scenes.yaml" # Optional
