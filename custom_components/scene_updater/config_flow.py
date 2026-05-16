import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN

class SceneUpdaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Scene Updater."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # Prevent users from installing the integration more than once
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            # Create the UI entry. No specific user configuration is needed.
            return self.async_create_entry(title="Scene Updater", data={})

        return self.async_show_form(step_id="user")
