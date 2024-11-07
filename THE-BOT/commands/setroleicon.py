import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio
import io

metadata = {
    "name": "Set Role Icon",
    "category": "Role",
    "help": "This command allows users to set the icon of a role by selecting the role from a dropdown menu and then sending an image file to be used as the role icon."
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
        placeholder="Select a role to change its icon",
        options=role_options
    )

    # Function to handle role selection and image input
    async def role_select_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Ask the user to upload an image for the role icon
        await select_interaction.response.send_message(f"Please upload an image to set as the icon for role `{selected_role.name}`.", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel and msg.attachments

        try:
            # Wait for the user to upload an image
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

            # Get the first attachment from the message
            attachment = msg.attachments[0]

            # Ensure the file is an image
            if not attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                await select_interaction.followup.send("The file must be an image (PNG, JPG, JPEG, or GIF). Please try again.", ephemeral=True)
                return

            # Get the image content
            image_bytes = await attachment.read()

            # Try to set the role icon
            try:
                await selected_role.edit(icon=discord.File(io.BytesIO(image_bytes), filename=attachment.filename))
                await select_interaction.followup.send(f"Icon for the role `{selected_role.name}` has been updated.", ephemeral=True)
            except discord.Forbidden:
                await select_interaction.followup.send(f"Could not update the icon for `{selected_role.name}` due to permission restrictions.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to respond. Operation cancelled.", ephemeral=True)

    # Add the callback function to the dropdown
    role_select.callback = role_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    await interaction.response.send_message("Please select a role to change its icon.", view=view)

# Help command for the setroleicon command
async def help_command(interaction):
    help_message = f"**Set Role Icon Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to set the icon for a selected role by uploading an image.\n\n" \
                   "Steps:\n1. Select a role you want to change the icon of.\n" \
                   "2. Upload an image to be used as the role icon.\n" \
                   "3. The bot will update the role's icon accordingly."
    await interaction.response.send_message(help_message)
