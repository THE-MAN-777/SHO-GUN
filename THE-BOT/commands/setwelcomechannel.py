import discord
from discord.ui import View, TextInput
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Welcome Channel",
    "category": "Server",
    "help": "This command allows users to set a welcome channel, a welcome message, and optionally an image or GIF."
}

# Define the command
async def execute_command(interaction):
    # Ask the user to mention the welcome channel
    await interaction.response.send_message(
        "Please mention the channel where you want to set the welcome message.",
        ephemeral=True
    )

    # Function to check the channel mention
    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel and msg.content.startswith('<#') and msg.content.endswith('>')

    try:
        # Wait for the user to mention the channel
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

        # Extract the channel ID from the mention
        welcome_channel_id = int(msg.content[2:-1])  # Removes <# and >
        welcome_channel = interaction.guild.get_channel(welcome_channel_id)

        if not welcome_channel or not isinstance(welcome_channel, discord.TextChannel):
            await interaction.followup.send("Invalid channel mentioned. Please try again.", ephemeral=True)
            return

        # Ask the user to provide the welcome message
        await interaction.followup.send("Please provide the welcome message to be sent to new members.", ephemeral=True)

        # Wait for the welcome message input
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
        welcome_message = msg.content

        # Ask the user if they want to add an optional image or GIF
        await interaction.followup.send("Do you want to add an image or GIF? (Reply with 'yes' or 'no')", ephemeral=True)

        def check_response(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.content.lower() in ['yes', 'no']

        msg = await interaction.client.wait_for('message', check=check_response, timeout=60.0)

        image_url = None
        if msg.content.lower() == 'yes':
            await interaction.followup.send("Please upload the image or GIF.", ephemeral=True)

            # Function to check if a file was uploaded
            def check_file(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel and len(msg.attachments) > 0

            msg = await interaction.client.wait_for('message', check=check_file, timeout=60.0)
            attachment = msg.attachments[0]

            # Check if the file is an image or GIF
            file_extension = attachment.filename.split('.')[-1].lower()
            if file_extension not in ['png', 'jpg', 'jpeg', 'gif']:
                await interaction.followup.send("Invalid file type. Please upload an image or GIF.", ephemeral=True)
                return

            image_url = attachment.url  # Save the URL of the image/GIF

        # Save the welcome channel and message to the guild's data (can use a database or in-memory storage)
        # Here, we store it in the bot's memory as an example
        guild_id = interaction.guild.id
        if not hasattr(interaction.client, "welcome_settings"):
            interaction.client.welcome_settings = {}

        interaction.client.welcome_settings[guild_id] = {
            "channel_id": welcome_channel.id,
            "welcome_message": welcome_message,
            "image_url": image_url
        }

        # Confirmation message
        confirmation_msg = f"Welcome channel set to {welcome_channel.mention}.\nWelcome message: {welcome_message}"
        if image_url:
            confirmation_msg += f"\nImage/GIF: {image_url}"

        await interaction.followup.send(confirmation_msg, ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to respond. The process has been cancelled.", ephemeral=True)

# Help command for the setwelcomechannel command
async def help_command(interaction):
    help_message = f"**Set Welcome Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to set the welcome channel, the welcome message, and optionally an image or GIF.\n\n" \
                   "Steps:\n1. Mention the channel to set as the welcome channel.\n" \
                   "2. Provide the welcome message.\n" \
                   "3. Optionally, upload an image or GIF to include in the welcome message."
    await interaction.response.send_message(help_message)
