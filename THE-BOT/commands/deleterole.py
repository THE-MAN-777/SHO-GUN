import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Delete Role",
    "category": "Role",
    "help": "This command allows users to delete a specific role in the server."
}

# Define the command
async def execute_command(interaction):
    # Fetch all roles in the server
    roles = interaction.guild.roles
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id)) 
        for role in roles if role.name != "@everyone"
    ]
    
    if not role_options:
        await interaction.response.send_message("No roles available to delete.", ephemeral=True)
        return

    role_select = Select(
        placeholder="Select the role to delete",
        options=role_options
    )

    # Create a callback for when a role is selected
    async def select_role_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Confirm the deletion
        confirm_button = Button(label="Confirm", style=discord.ButtonStyle.red)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.green)

        async def confirm_button_callback(interaction):
            try:
                # Delete the selected role
                await selected_role.delete()
                await interaction.response.send_message(f"Role '{selected_role.name}' has been deleted.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I do not have permission to delete this role.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to delete the role. Error: {str(e)}", ephemeral=True)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Role deletion cancelled.", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        # Add the buttons to a view
        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await select_interaction.response.send_message(f"Are you sure you want to delete the role '{selected_role.name}'?", view=view, ephemeral=True)

    # Add the callback to the role selection dropdown
    role_select.callback = select_role_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Role deletion cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select the role to delete.", view=view)

# Help command for the deleterole command
async def help_command(interaction):
    help_message = f"**Delete Role Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a role and delete it.\n\n" \
                   "Steps:\n1. Select the role you want to delete.\n" \
                   "2. Confirm the deletion.\n" \
                   "3. The role will be permanently deleted after confirmation."
    await interaction.response.send_message(help_message)
