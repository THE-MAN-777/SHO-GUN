import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "List Roles",
    "category": "Information",
    "help": "This command allows users to view all roles, their colors, the number of members assigned to each role, and other important information."
}

# Define the command
async def execute_command(interaction):
    # Fetch all roles in the server
    roles = sorted(interaction.guild.roles, key=lambda role: role.position, reverse=True)  # Sort roles by position
    
    if not roles:
        await interaction.response.send_message("No roles available to display.", ephemeral=True)
        return

    # Create a dropdown menu to select a role
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id)) 
        for role in roles if role.name != "@everyone"  # Exclude @everyone role
    ]

    # Create a callback for when a role is selected
    async def select_role_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Get the members assigned to the selected role
        role_members = [member for member in interaction.guild.members if selected_role in member.roles]
        member_count = len(role_members)

        # Prepare the role information message
        role_info_message = f"**Role: {selected_role.name}**\n"
        role_info_message += f"Color: {selected_role.color}\n"
        role_info_message += f"Position: {selected_role.position}\n"
        role_info_message += f"Members: {member_count} member(s)\n"
        
        if selected_role.hoist:
            role_info_message += "This role is displayed separately in the member list.\n"
        else:
            role_info_message += "This role is not displayed separately in the member list.\n"

        if selected_role.managed:
            role_info_message += "This role is managed by an external service (e.g., bot).\n"
        else:
            role_info_message += "This role is not managed by an external service.\n"

        # Display all members with the role
        if member_count > 0:
            role_info_message += "\n**Members with this role:**\n"
            for member in role_members:
                role_info_message += f" - {member.name}#{member.discriminator}\n"
        else:
            role_info_message += "\nNo members have this role."

        await select_interaction.response.send_message(role_info_message, ephemeral=True)

    # Add the callback to the role selection dropdown
    role_select = Select(
        placeholder="Select a role to view its information",
        options=role_options
    )
    role_select.callback = select_role_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Role listing cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a role to view its information.", view=view)

# Help command for the listroles command
async def help_command(interaction):
    help_message = f"**List Roles Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a role and view detailed information about it, including:\n" \
                   "- The color of the role\n" \
                   "- The number of members assigned to the role\n" \
                   "- Role position and other important details\n\n" \
                   "Steps:\n1. Select a role to view its information.\n" \
                   "2. The bot will display the role's color, number of members, and additional information."
    await interaction.response.send_message(help_message)
