import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Role Permissions",
    "category": "Permissions",
    "help": "This command allows users to view and modify role permissions by selecting a role and toggling its permissions."
}

# Define the command
async def execute_command(interaction):
    # Fetch all available roles in the guild
    roles = interaction.guild.roles
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id))
        for role in roles if not role.managed and role.name != "@everyone"
    ]

    if not role_options:
        await interaction.response.send_message("No roles available to modify.", ephemeral=True)
        return

    # Create a dropdown to select a role
    role_select = Select(
        placeholder="Select a role to modify its permissions",
        options=role_options
    )

    # Function to handle role selection and permissions modification
    async def role_select_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Get the permissions of the selected role
        permissions = selected_role.permissions
        perms_options = [
            discord.SelectOption(label=perm, value=perm, description="Enabled" if getattr(permissions, perm) else "Disabled")
            for perm in dir(permissions)
            if not perm.startswith('_') and isinstance(getattr(permissions, perm), bool)
        ]

        # Create a dropdown to select a permission to toggle
        if not perms_options:
            await select_interaction.response.send_message(f"The role `{selected_role.name}` has no configurable permissions.", ephemeral=True)
            return

        perms_select = Select(
            placeholder="Select a permission to toggle",
            options=perms_options
        )

        # Function to handle toggling of permission
        async def perms_select_callback(select_interaction):
            perm_name = select_interaction.data['values'][0]
            current_status = getattr(permissions, perm_name)

            # Toggle the permission
            new_status = not current_status

            # Update the role's permissions
            try:
                perms_dict = {perm: new_status if perm == perm_name else getattr(permissions, perm) for perm in dir(permissions) if not perm.startswith('_') and isinstance(getattr(permissions, perm), bool)}
                updated_permissions = discord.Permissions(**perms_dict)

                await selected_role.edit(permissions=updated_permissions)
                status = "enabled" if new_status else "disabled"
                await select_interaction.response.send_message(f"The permission `{perm_name}` has been {status} for the role `{selected_role.name}`.", ephemeral=True)
            except discord.Forbidden:
                await select_interaction.response.send_message(f"Could not update the permissions for `{selected_role.name}` due to permission restrictions.", ephemeral=True)

        # Add the callback function to the dropdown
        perms_select.callback = perms_select_callback

        # Add the dropdown to a view and send the message
        view = View()
        view.add_item(perms_select)

        await select_interaction.response.send_message(
            f"Current permissions for role `{selected_role.name}`:\n"
            + "\n".join([f"{perm}: {'Enabled' if getattr(permissions, perm) else 'Disabled'}" for perm in dir(permissions) if not perm.startswith('_') and isinstance(getattr(permissions, perm), bool)]),
            view=view
        )

    # Add the callback function to the role selection dropdown
    role_select.callback = role_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    await interaction.response.send_message("Please select a role to modify its permissions.", view=view)

# Help command for the setroleperms command
async def help_command(interaction):
    help_message = f"**Set Role Permissions Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to view and toggle permissions for a selected role.\n\n" \
                   "Steps:\n1. Select a role you want to modify.\n" \
                   "2. View the current permissions of the role (enabled/disabled).\n" \
                   "3. Toggle any permission (enabled/disabled)."
    await interaction.response.send_message(help_message)
