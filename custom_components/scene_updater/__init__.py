import os
import yaml
import logging
from homeassistant.util import slugify
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SAFE_ATTRIBUTES = {
    "brightness", "color_temp", "rgb_color", "rgbw_color", "rgbww_color",
    "xy_color", "hs_color", "effect", "temperature", "target_temp_high",
    "target_temp_low", "hvac_mode", "preset_mode", "swing_mode", "fan_mode",
    "percentage", "current_position", "tilt_position"
}

def sanitize_for_yaml(data):
    """Recursively convert tuples to lists to prevent YAML serialization errors."""
    if isinstance(data, tuple):
        return list(sanitize_for_yaml(item) for item in data)
    elif isinstance(data, list):
        return [sanitize_for_yaml(item) for item in data]
    elif isinstance(data, dict):
        return {k: sanitize_for_yaml(v) for k, v in data.items()}
    return data

async def async_setup(hass, config):
    """Fallback setup method."""
    return True

async def async_setup_entry(hass, entry):
    """Set up Scene Updater from a UI config entry."""

    async def handle_save_scene(call):
        """Handle the service call to update the scene file."""
        scene_entity = call.data.get("scene_entity")
        file_path = call.data.get("file_path", "scenes.yaml")
        
        target_slug = scene_entity.split(".")[1] if "." in scene_entity else scene_entity

        config_dir = hass.config.config_dir
        target_path = os.path.abspath(os.path.join(config_dir, file_path))
        
        if not target_path.startswith(config_dir):
            _LOGGER.error("Security violation: Attempted to access file outside config directory: %s", file_path)
            return

        if not os.path.exists(target_path):
            _LOGGER.error("Scene file not found at %s", target_path)
            return

        def update_yaml_file():
            try:
                with open(target_path, "r", encoding="utf8") as file:
                    scenes = yaml.safe_load(file) or []
            except Exception as exc:
                _LOGGER.error("File Read Error on %s: %s", target_path, exc)
                return None

            target_scene_found = False
            updated_entity_ids = []

            for scene in scenes:
                yaml_name = scene.get("name")
                if yaml_name and slugify(yaml_name) == target_slug:
                    target_scene_found = True
                    if "entities" not in scene:
                        _LOGGER.error("Scene '%s' has no entities defined.", yaml_name)
                        return None

                    # Capture the exact entities attached to this scene
                    updated_entity_ids = list(scene["entities"].keys())

                    for entity_id in scene["entities"]:
                        state = hass.states.get(entity_id)
                        if state:
                            existing_data = scene["entities"].get(entity_id, {})
                            if not isinstance(existing_data, dict):
                                existing_data = {}
                                
                            entity_data = dict(existing_data)
                            entity_data["state"] = state.state
                            
                            for attr in SAFE_ATTRIBUTES:
                                if attr in state.attributes:
                                    entity_data[attr] = sanitize_for_yaml(state.attributes[attr])
                                    
                            scene["entities"][entity_id] = entity_data
                        else:
                            _LOGGER.warning("Entity %s not found. Keeping existing YAML values.", entity_id)
                    break

            if not target_scene_found:
                _LOGGER.error("Scene linked to entity '%s' not found in %s.", scene_entity, target_path)
                return None

            temp_file = f"{target_path}.tmp"
            try:
                with open(temp_file, "w", encoding="utf8") as file:
                    yaml.dump(scenes, file, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                os.replace(temp_file, target_path)
                return updated_entity_ids  # Return the list of entities instead of a boolean
            except Exception as exc:
                _LOGGER.error("Error writing to %s: %s", target_path, exc)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return None

        # Execute file I/O safely and retrieve the list of entities that were just processed
        entities_to_snapshot = await hass.async_add_executor_job(update_yaml_file)

        # V3.1.0 MEMORY LEAK FIX: If file write succeeded, update active memory instantly via scene.create
        if entities_to_snapshot is not None:
            _LOGGER.info("Successfully updated physical file for '%s'. Updating active memory.", scene_entity)
            await hass.services.async_call(
                "scene", "create",
                {
                    "scene_id": target_slug,
                    "snapshot_entities": entities_to_snapshot
                }
            )

    hass.services.async_register(DOMAIN, "save_scene", handle_save_scene)
    return True

async def async_unload_entry(hass, entry):
    """Unload the config entry and clean up the service."""
    hass.services.async_remove(DOMAIN, "save_scene")
    return True
