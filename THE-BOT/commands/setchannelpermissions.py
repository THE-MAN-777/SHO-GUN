import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Channel Permissions",
    "category": "Permissions",
    "help": "This command allows users to set permissions for a specific channel by toggling permissions via dropdowns."
}

# Define the command
async def execute_command(interaction):
    # Prompt user to mention the channel they want to change permissions for
    await interaction.response.send_message("Please mention the channel you want to change permissions for (e.g. #channel).", ephemeral=True)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        # Wait for the user to mention a channel
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

        # Extract the mentioned channel from the message
        mentioned_channel = discord.utils.get(interaction.guild.channels, mention=msg.content.split()[0])

        if not mentioned_channel:
            await interaction.followup.send("Invalid channel mentioned. Please try again.", ephemeral=True)
            return

        # Fetch the permissions for the mentioned channel
        channel_permissions = mentioned_channel.overwrites

        # Create a list of permission options
        permission_options = [
            discord.SelectOption(label=perm[0], value=perm[0], description=f"Currently: {'Granted' if perm[1] else 'Denied'}") 
            for perm in channel_permissions.items()
        ]

        if not permission_options:
            await interaction.followup.send("This channel has no custom permissions set. Please add permissions first.", ephemeral=True)
            return

        # Create a dropdown to allow the user to select permissions to toggle
        permission_select = Select(
            placeholder="Select a permission to toggle",
            options=permission_options
        )

        async def permission_toggle_callback(select_interaction):
            permission_name = select_interaction.data['values'][0]
            perm_value = channel_permissions.get(permission_name)

            # Toggle the permission (True/False)
            new_perm_value = not perm_value

            # Update the permission
            try:
                await mentioned_channel.set_permissions(interaction.user, **{permission_name: new_perm_value})
                await select_interaction.response.send_message(f"Permission `{permission_name}` has been {'granted' if new_perm_value else 'denied'} for {interaction.user.mention}.", ephemeral=True)
            except discord.Forbidden:
                await select_interaction.response.send_message(f"Could not modify permissions for {mentioned_channel.mention}.", ephemeral=True)

        # Add the callback function to the dropdown
        permission_select.callback = permission_toggle_callback

        # Add the dropdown to a view and send the message
        view = View()
        view.add_item(permission_select)

        # Optionally, add a cancel button
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Permission modification operation cancelled.", ephemeral=True)

        cancel_button.callback = cancel_button_callback
        view.add_item(cancel_button)

        await interaction.followup.send(f"Please select a permission to toggle for {mentioned_channel.mention}.", view=view)

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to reply. Operation cancelled.", ephemeral=True)

# Help command for the setchannelperms command
async def help_command(interaction):
    help_message = f"**Set Channel Permissions Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a channel and toggle its permissions for the selected role or user.\n\n" \
                   "Steps:\n1. Mention the channel you want to modify permissions for.\n" \
                   "2. Select the permission you want to toggle.\n" \
                   "3. The bot will change the permission to the opposite of the current value.\n" \
                   "Note: If the permission is currently granted, it will be denied, and vice versa."
    await interaction.response.send_message(help_message)
