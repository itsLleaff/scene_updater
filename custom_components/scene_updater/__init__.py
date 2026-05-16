import os
import yaml
import logging

DOMAIN = "scene_updater"
_LOGGER = logging.getLogger(__name__)

SAFE_ATTRIBUTES = {
    "brightness", "color_temp", "rgb_color", "rgbw_color", "rgbww_color",
    "xy_color", "hs_color", "effect", "temperature", "target_temp_high",
    "target_temp_low", "hvac_mode", "preset_mode", "swing_mode", "fan_mode",
    "percentage", "current_position", "tilt_position"
}

async def async_setup(hass, config):
    """Set up the Scene Updater component."""

    async def handle_save_scene(call):
        """Handle the service call to update the scene file."""
        scene_name = call.data.get("scene_name")
        file_path = call.data.get("file_path", "scenes.yaml")
        
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
            except yaml.YAMLError as exc:
                _LOGGER.error("YAML Syntax Error parsing %s: %s", target_path, exc)
                return False
            except Exception as exc:
                _LOGGER.error("File Read Error on %s: %s", target_path, exc)
                return False

            target_scene_found = False

            for scene in scenes:
                if scene.get("name") == scene_name:
                    target_scene_found = True
                    if "entities" not in scene:
                        _LOGGER.error("Scene '%s' has no entities defined.", scene_name)
                        return False

                    for entity_id in scene["entities"]:
                        state = hass.states.get(entity_id)
                        if state:
                            # V2.1 PRESERVATION LOGIC
                            # Fetch existing YAML data to preserve unknown attributes
                            existing_data = scene["entities"].get(entity_id, {})
                            
                            # Ensure we are working with a dictionary
                            if not isinstance(existing_data, dict):
                                existing_data = {}
                                
                            entity_data = dict(existing_data)
                            
                            # Always update the core state
                            entity_data["state"] = state.state
                            
                            # Update safe attributes from current state machine
                            for attr in SAFE_ATTRIBUTES:
                                if attr in state.attributes:
                                    entity_data[attr] = state.attributes[attr]
                                    
                            scene["entities"][entity_id] = entity_data
                        else:
                            _LOGGER.warning("Entity %s not found in state machine. Keeping existing YAML values.", entity_id)
                    break

            if not target_scene_found:
                _LOGGER.error("Scene '%s' not found in %s.", scene_name, target_path)
                return False

            temp_file = f"{target_path}.tmp"
            try:
                with open(temp_file, "w", encoding="utf8") as file:
                    yaml.dump(scenes, file, default_flow_style=False, sort_keys=False, allow_unicode=True)
                
                os.replace(temp_file, target_path)
                return True
            except Exception as exc:
                _LOGGER.error("Error writing to %s: %s", target_path, exc)
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return False

        success = await hass.async_add_executor_job(update_yaml_file)

        if success:
            _LOGGER.info("Successfully updated scene '%s' in %s.", scene_name, file_path)
            await hass.services.async_call("scene", "reload")

    hass.services.async_register(DOMAIN, "save_scene", handle_save_scene)
    return True
