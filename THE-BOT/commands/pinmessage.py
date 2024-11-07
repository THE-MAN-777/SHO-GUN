import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Pin Message",
    "category": "channel",
    "help": "This command allows users to pin a message from a dropdown menu in a channel."
}

# Define the command
async def execute_command(interaction):
    # Fetch all text channels in the guild
    text_channels = [channel for channel in interaction.guild.text_channels]

    if not text_channels:
        await interaction.response.send_message("No text channels available to pin messages from.", ephemeral=True)
        return

    # Create a dropdown menu to select the channel
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

        # Fetch the recent messages in the selected channel
        messages = await selected_channel.history(limit=20).flatten()

        if not messages:
            await select_interaction.response.send_message("No messages found in this channel.", ephemeral=True)
            return

        # Create a dropdown menu to select a message to pin
        message_options = [
            discord.SelectOption(label=f"Message from {msg.author} - {msg.content[:50]}", value=str(msg.id)) 
            for msg in messages
        ]

        # Create a callback for when a message is selected
        async def select_message_callback(message_interaction):
            selected_message_id = message_interaction.data['values'][0]
            selected_message = await selected_channel.fetch_message(int(selected_message_id))

            if not selected_message:
                await message_interaction.response.send_message("Message not found.", ephemeral=True)
                return

            # Pin the selected message
            try:
                await selected_message.pin()
                await message_interaction.response.send_message(f"Message from {selected_message.author} has been pinned.", ephemeral=True)
            except discord.Forbidden:
                await message_interaction.response.send_message("I do not have permission to pin this message.", ephemeral=True)

        # Add the callback to the message selection dropdown
        message_select = Select(
            placeholder="Select a message to pin",
            options=message_options
        )
        message_select.callback = select_message_callback

        # Add the message dropdown to a view and send the message
        view = View()
        view.add_item(message_select)

        # Optionally, add a cancel button to the dropdown
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Pinning cancelled.", ephemeral=True)

        cancel_button.callback = cancel_button_callback
        view.add_item(cancel_button)

        await message_interaction.response.send_message(f"Please select a message from {selected_channel.name} to pin.", view=view)

    # Add the callback to the channel selection dropdown
    channel_select = Select(
        placeholder="Select a channel to pin messages from",
        options=channel_options
    )
    channel_select.callback = select_channel_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Pinning cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a channel to pin a message from.", view=view)

# Help command for the pinmessage command
async def help_command(interaction):
    help_message = f"**Pin Message Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a channel and pin a message from that channel.\n\n" \
                   "Steps:\n1. Select a channel to choose a message from.\n" \
                   "2. Select a message from the recent messages list.\n" \
                   "3. The bot will pin the selected message in the channel."
    await interaction.response.send_message(help_message)
