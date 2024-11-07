import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "List Channels",
    "category": "Information",
    "help": "This command allows users to view all channels, their categories, and the roles that have access to them."
}

# Define the command
async def execute_command(interaction):
    # Fetch all categories and channels
    categories = interaction.guild.categories
    channels = interaction.guild.channels

    # Prepare category and channel options
    category_channels = {}
    for category in categories:
        category_channels[category] = [channel for channel in category.channels if isinstance(channel, (discord.TextChannel, discord.VoiceChannel))]

    if not categories:
        await interaction.response.send_message("No categories available to display.", ephemeral=True)
        return
    
    # Create a dropdown menu to select a category
    category_options = [
        discord.SelectOption(label=category.name, value=str(category.id)) 
        for category in categories
    ]

    # Create a callback for when a category is selected
    async def select_category_callback(select_interaction):
        selected_category_id = select_interaction.data['values'][0]
        selected_category = interaction.guild.get_channel(int(selected_category_id))

        if not selected_category or not isinstance(selected_category, discord.CategoryChannel):
            await select_interaction.response.send_message("Category not found.", ephemeral=True)
            return

        # Collect channels in the selected category
        category_channels_list = category_channels[selected_category]
        
        if not category_channels_list:
            await select_interaction.response.send_message(f"No channels found in the category '{selected_category.name}'.", ephemeral=True)
            return

        # Create a beautiful message with channel names and roles that have access
        channel_info_message = f"**Category: {selected_category.name}**\n\n"
        for channel in category_channels_list:
            channel_info_message += f"**Channel: {channel.name}**\n"

            # Collect roles that have access to the channel
            allowed_roles = []
            for overwrite in channel.overwrites.values():
                if isinstance(overwrite, discord.PermissionOverwrite) and overwrite.read_messages:
                    allowed_roles.extend([role.name for role in interaction.guild.roles if role.id == overwrite.id])

            if allowed_roles:
                channel_info_message += f"  - Accessible by: {', '.join(allowed_roles)}\n"
            else:
                channel_info_message += "  - No specific roles have access.\n"

        await select_interaction.response.send_message(channel_info_message, ephemeral=True)

    # Add the callback to the category selection dropdown
    category_select = Select(
        placeholder="Select a category to view channels",
        options=category_options
    )
    category_select.callback = select_category_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(category_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel listing cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a category to view its channels and role access.", view=view)

# Help command for the listchannels command
async def help_command(interaction):
    help_message = f"**List Channels Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a category and view all channels in it, along with the roles that have access to each channel.\n\n" \
                   "Steps:\n1. Select a category to view its channels.\n" \
                   "2. The bot will display all channels in the selected category along with the roles that have access to each one."
    await interaction.response.send_message(help_message)
