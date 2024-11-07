import discord
from discord.ext import commands
import io

metadata = {
    "name": "Set Server Icon",
    "category": "Server",
    "help": "This command allows users to set a new server icon by uploading an image file (PNG, JPG, etc.)."
}

# Define the command
async def execute_command(interaction):
    # Ask the user to upload an image file
    await interaction.response.send_message(
        "Please upload an image file (PNG, JPG, or other formats) to set as the new server icon.",
        ephemeral=True
    )

    # Function to check the uploaded image file
    def check(message):
        return message.author == interaction.user and message.channel == interaction.channel and len(message.attachments) > 0

    try:
        # Wait for the user to upload a file
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

        # Get the first attachment (image file)
        attachment = msg.attachments[0]
        file_extension = attachment.filename.split('.')[-1].lower()

        # Validate file type (check for common image formats)
        if file_extension not in ['png', 'jpg', 'jpeg', 'gif']:
            await interaction.followup.send("Invalid file type. Please upload a PNG, JPG, or JPEG image.", ephemeral=True)
            return

        # Download the image data
        image_data = await attachment.read()

        # Set the new server icon
        try:
            await interaction.guild.edit(icon=image_data)
            await interaction.followup.send(f"The server icon has been successfully updated to the new image.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to change the server icon.", ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to upload an image. The request has been cancelled.", ephemeral=True)

# Help command for the setservericon command
async def help_command(interaction):
    help_message = f"**Set Server Icon Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to set a new server icon by uploading an image file (PNG, JPG, etc.).\n\n" \
                   "Steps:\n1. Upload an image file (PNG, JPG, or JPEG).\n" \
                   "2. The bot will set the uploaded image as the new server icon."
    await interaction.response.send_message(help_message)
