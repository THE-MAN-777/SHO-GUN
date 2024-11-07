import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Delete Channel",
    "category": "Channel",
    "help": "This command allows users to delete a specific channel in the server."
}

# Define the command
async def execute_command(interaction):
    # Fetch all channels in the server
    channels = interaction.guild.channels
    channel_options = [
        discord.SelectOption(label=channel.name, value=str(channel.id)) 
        for channel in channels if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.VoiceChannel)
    ]
    
    if not channel_options:
        await interaction.response.send_message("No channels available to delete.", ephemeral=True)
        return

    channel_select = Select(
        placeholder="Select the channel to delete",
        options=channel_options
    )

    # Create a callback for when a channel is selected
    async def select_channel_callback(select_interaction):
        selected_channel_id = select_interaction.data['values'][0]
        selected_channel = interaction.guild.get_channel(int(selected_channel_id))

        if not selected_channel:
            await select_interaction.response.send_message("Channel not found.", ephemeral=True)
            return

        # Confirm the deletion
        confirm_button = Button(label="Confirm", style=discord.ButtonStyle.red)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.green)

        async def confirm_button_callback(interaction):
            try:
                # Delete the selected channel
                await selected_channel.delete()
                await interaction.response.send_message(f"Channel '{selected_channel.name}' has been deleted.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I do not have permission to delete this channel.", ephemeral=True)
            except discord.HTTPException as e:
                await interaction.response.send_message(f"Failed to delete the channel. Error: {str(e)}", ephemeral=True)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Channel deletion cancelled.", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        # Add the buttons to a view
        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await select_interaction.response.send_message(f"Are you sure you want to delete the channel '{selected_channel.name}'?", view=view, ephemeral=True)

    # Add the callback to the channel selection dropdown
    channel_select.callback = select_channel_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel deletion cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select the channel to delete.", view=view)

# Help command for the deletechannel command
async def help_command(interaction):
    help_message = f"**Delete Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a channel and delete it.\n\n" \
                   "Steps:\n1. Select the channel you want to delete.\n" \
                   "2. Confirm the deletion.\n" \
                   "3. The channel will be permanently deleted after confirmation."
    await interaction.response.send_message(help_message)
