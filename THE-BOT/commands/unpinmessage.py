import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "Unpin Message",
    "category": "channel",
    "help": "This command allows users to unpin a message from a channel using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Fetch the pinned messages in the current channel
    pinned_messages = await interaction.channel.pins()
    if not pinned_messages:
        await interaction.response.send_message("No pinned messages in this channel.", ephemeral=True)
        return

    # Create a dropdown menu to select a pinned message
    message_options = [
        discord.SelectOption(label=f"Message by {msg.author}", value=str(msg.id))
        for msg in pinned_messages
    ]

    # Create a dropdown for selecting a pinned message to unpin
    message_select = Select(
        placeholder="Select a pinned message to unpin",
        options=message_options
    )

    # Function to handle message selection
    async def message_select_callback(select_interaction):
        selected_message_id = select_interaction.data['values'][0]
        selected_message = await interaction.channel.fetch_message(int(selected_message_id))

        if not selected_message:
            await select_interaction.response.send_message("Message not found.", ephemeral=True)
            return

        # Unpin the message
        try:
            await selected_message.unpin()
            await select_interaction.response.send_message(f"Message by {selected_message.author} has been unpinned.", ephemeral=True)
        except discord.Forbidden:
            await select_interaction.response.send_message("I do not have permission to unpin this message.", ephemeral=True)

    # Add the callback function to the dropdown
    message_select.callback = message_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(message_select)
    await interaction.response.send_message("Please select a pinned message to unpin.", view=view)

# Help command for the unpinmsg command
async def help_command(interaction):
    help_message = f"**Unpin Message Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to unpin a pinned message from a channel using a dropdown menu.\n\n" \
                   "Steps:\n1. Select a pinned message from the dropdown.\n" \
                   "2. The bot will unpin the selected message."
    await interaction.response.send_message(help_message)
