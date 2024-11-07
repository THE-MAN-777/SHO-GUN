import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "Unlock Channel",
    "category": "Channel",
    "help": "This command allows users to unlock a channel by selecting it from an auto-fetch dropdown."
}

# Define the command
async def execute_command(interaction):
    # Fetch all the text channels in the server
    channels = interaction.guild.text_channels
    channel_options = [
        discord.SelectOption(label=channel.name, value=str(channel.id))
        for channel in channels
        if not channel.permissions_for(interaction.guild.default_role).send_messages  # Only locked channels
    ]

    if not channel_options:
        await interaction.response.send_message("No locked channels available to unlock.", ephemeral=True)
        return

    # Create a dropdown menu for channel selection
    channel_select = Select(
        placeholder="Select a channel to unlock",
        options=channel_options
    )

    # Function to handle channel selection
    async def channel_select_callback(select_interaction):
        selected_channel_id = select_interaction.data['values'][0]
        selected_channel = interaction.guild.get_channel(int(selected_channel_id))

        if not selected_channel:
            await select_interaction.response.send_message("Channel not found.", ephemeral=True)
            return

        # Check if the channel is locked
        if selected_channel.permissions_for(interaction.guild.default_role).send_messages:
            await select_interaction.response.send_message(f"Channel '{selected_channel.name}' is already unlocked.", ephemeral=True)
            return

        # Unlock the channel
        try:
            # Grant send_messages permission for the default role (everyone)
            await selected_channel.set_permissions(interaction.guild.default_role, send_messages=True)
            await select_interaction.response.send_message(f"Channel '{selected_channel.name}' has been unlocked.", ephemeral=True)
        except discord.Forbidden:
            await select_interaction.response.send_message("I do not have permission to unlock this channel.", ephemeral=True)

    # Add the callback function to the dropdown
    channel_select.callback = channel_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)
    await interaction.response.send_message("Please select a channel to unlock.", view=view)

# Help command for the unlockchannel command
async def help_command(interaction):
    help_message = f"**Unlock Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to unlock a channel by selecting it from a dropdown menu.\n\n" \
                   "Steps:\n1. Select a channel from the dropdown.\n" \
                   "2. The bot will unlock the channel if it is locked."
    await interaction.response.send_message(help_message)
