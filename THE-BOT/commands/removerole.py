import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Remove Role",
    "category": "Role",
    "help": "This command allows users to remove a role from multiple users using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Fetch all roles in the guild
    roles = [role for role in interaction.guild.roles if role.name != "@everyone" and not role.managed]

    if not roles:
        await interaction.response.send_message("No roles available to remove.", ephemeral=True)
        return

    # Create a dropdown menu to select a role
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id)) 
        for role in roles
    ]

    # Create a callback for when a role is selected
    async def select_role_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Prompt user to tag multiple people to remove the role from
        await select_interaction.response.send_message("Please mention the users you want to remove the role from.", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
            tagged_users = [user for user in msg.mentions]

            if not tagged_users:
                await select_interaction.followup.send("No users mentioned. Role removal cancelled.", ephemeral=True)
                return

            # Remove the role from mentioned users
            for user in tagged_users:
                try:
                    await user.remove_roles(selected_role)
                    await select_interaction.followup.send(f"Role '{selected_role.name}' removed from {user.mention}.", ephemeral=True)
                except discord.Forbidden:
                    await select_interaction.followup.send(f"Could not remove role from {user.mention} due to permission restrictions.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to reply. Role removal cancelled.", ephemeral=True)

    # Add the callback to the role selection dropdown
    role_select = Select(
        placeholder="Select a role to remove",
        options=role_options
    )
    role_select.callback = select_role_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    # Optionally, add a cancel button to the dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Role removal cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a role to remove and then mention users.", view=view)

# Help command for the removerole command
async def help_command(interaction):
    help_message = f"**Remove Role Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a role from a dropdown and remove it from multiple users by mentioning them.\n\n" \
                   "Steps:\n1. Select a role to remove.\n" \
                   "2. Mention users to remove the selected role from.\n" \
                   "3. The bot will remove the role from the mentioned users."
    await interaction.response.send_message(help_message)
