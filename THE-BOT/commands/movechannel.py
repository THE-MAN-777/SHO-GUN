import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Move Channel",
    "category": "Channel",
    "help": "This command allows users to reorder channels within the server using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Fetch all text channels and their positions
    text_channels = [channel for channel in interaction.guild.text_channels]

    if not text_channels:
        await interaction.response.send_message("No text channels available to reorder.", ephemeral=True)
        return

    # Create a dropdown menu to select a channel to move
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

        # Create a dropdown menu to select the new position for the channel
        position_options = [
            discord.SelectOption(label=f"Move to position {i + 1}", value=str(i))
            for i in range(len(text_channels))
        ]

        async def select_position_callback(position_interaction):
            selected_position = int(position_interaction.data['values'][0])

            if selected_position == selected_channel.position:
                await position_interaction.response.send_message("The channel is already in the selected position.", ephemeral=True)
                return

            # Reorder the channel
            try:
                # Update the channel's position
                await selected_channel.edit(position=selected_position)
                await position_interaction.response.send_message(f"Channel '{selected_channel.name}' has been moved to position {selected_position + 1}.", ephemeral=True)
            except discord.Forbidden:
                await position_interaction.response.send_message("I do not have permission to move this channel.", ephemeral=True)

        # Add the callback to the position selection dropdown
        position_select = Select(
            placeholder="Select a position to move the channel to",
            options=position_options
        )
        position_select.callback = select_position_callback

        # Add the position dropdown to a view and send the message
        view = View()
        view.add_item(position_select)

        # Optionally, add a cancel button to the dropdown
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Channel reordering cancelled.", ephemeral=True)

        cancel_button.callback = cancel_button_callback
        view.add_item(cancel_button)

        await position_interaction.response.send_message(f"Please select a new position for the channel '{selected_channel.name}'.", view=view)

    # Add the callback to the channel selection dropdown
    channel_select = Select(
        placeholder="Select a channel to move",
        options=channel_options
    )
    channel_select.callback = select_channel_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel reordering cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a channel to reorder.", view=view)

# Help command for the movechannel command
async def help_command(interaction):
    help_message = f"**Move Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a channel and reorder it by moving it to a different position within the server.\n\n" \
                   "Steps:\n1. Select a channel to move.\n" \
                   "2. Select a new position for the channel to be placed in.\n" \
                   "3. The bot will move the channel to the selected position."
    await interaction.response.send_message(help_message)
