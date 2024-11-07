import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Role Colour",
    "category": "Role",
    "help": "This command allows users to set the color of a role using a hex color code by selecting a role from a dropdown menu."
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
        placeholder="Select a role to change its color",
        options=role_options
    )

    # Function to handle role selection and color input
    async def role_select_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Ask the user to input a hex color code
        await select_interaction.response.send_message(f"Please enter a new hex color code for role `{selected_role.name}` (e.g., #ff5733):", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            # Wait for the user to enter the color
            color_msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

            hex_color = color_msg.content.strip()

            # Validate the hex color format
            if not hex_color.startswith('#') or len(hex_color) != 7:
                await select_interaction.followup.send("Invalid hex color format. Please make sure the color is in the form #RRGGBB.", ephemeral=True)
                return

            # Try to set the role color
            try:
                await selected_role.edit(color=discord.Color(int(hex_color[1:], 16)))
                await select_interaction.followup.send(f"Color of the role `{selected_role.name}` has been updated to {hex_color}.", ephemeral=True)
            except discord.Forbidden:
                await select_interaction.followup.send(f"Could not update the color for `{selected_role.name}` due to permission restrictions.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to respond. Operation cancelled.", ephemeral=True)

    # Add the callback function to the dropdown
    role_select.callback = role_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    await interaction.response.send_message("Please select a role to change its color.", view=view)

# Help command for the setrolecolour command
async def help_command(interaction):
    help_message = f"**Set Role Colour Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to set the color for a selected role in the server using a hex color code.\n\n" \
                   "Steps:\n1. Select a role you want to change the color of.\n" \
                   "2. Enter a valid hex color code in the format #RRGGBB.\n" \
                   "3. The bot will update the color of the selected role."
    await interaction.response.send_message(help_message)
