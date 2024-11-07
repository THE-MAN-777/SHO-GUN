import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Lock Channel",
    "category": "Channel",
    "help": "This command allows users to lock a channel by selecting it from a dropdown menu. Locking a channel prevents users from sending messages."
}

# Define the command
async def execute_command(interaction):
    # Fetch all text channels in the server
    text_channels = [channel for channel in interaction.guild.text_channels]

    if not text_channels:
        await interaction.response.send_message("No text channels available to lock.", ephemeral=True)
        return

    # Create a dropdown menu to select a channel to lock
    channel_options = [
        discord.SelectOption(label=channel.name, value=str(channel.id)) 
        for channel in text_channels
    ]

    # Create a callback for when a channel is selected
    async def select_channel_callback(select_interaction):
        selected_channel_id = select_interaction.data['values'][0]
        selected_channel = interaction.guild.get_channel(int(selected_channel_id))

        if not selected_channel or not isinstance(selected_channel, discord.TextChannel):
            await select_interaction.response.send_message("Channel not found or is not a text channel.", ephemeral=True)
            return

        # Lock the channel by setting the 'send_messages' permission for @everyone to False
        try:
            await selected_channel.set_permissions(interaction.guild.default_role, send_messages=False)
            await select_interaction.response.send_message(f"Channel '{selected_channel.name}' has been locked.", ephemeral=True)
        except discord.Forbidden:
            await select_interaction.response.send_message("I do not have permission to lock this channel.", ephemeral=True)

    # Add the callback to the channel selection dropdown
    channel_select = Select(
        placeholder="Select a channel to lock",
        options=channel_options
    )
    channel_select.callback = select_channel_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel locking cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a channel to lock.", view=view)

# Help command for the lockchannel command
async def help_command(interaction):
    help_message = f"**Lock Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a text channel from a dropdown menu and lock it, preventing users from sending messages.\n\n" \
                   "Steps:\n1. Select a channel to lock.\n" \
                   "2. The bot will lock the channel and prevent users from sending messages."
    await interaction.response.send_message(help_message)
