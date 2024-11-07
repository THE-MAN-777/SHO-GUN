import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Assign Role",
    "category": "Role",
    "help": "This command allows users to assign roles to multiple people from a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Create a dropdown menu to select roles
    roles = interaction.guild.roles
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id)) 
        for role in roles if not role.managed and role.name != "@everyone"
    ]
    
    if not role_options:
        await interaction.response.send_message("No roles available to assign.", ephemeral=True)
        return
    
    role_select = Select(
        placeholder="Select a role to assign",
        options=role_options
    )
    
    # Create a dropdown to select users to assign the role to
    async def select_role_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Prompt user to tag multiple people
        await select_interaction.response.send_message("Please mention the users you want to assign the role to.", ephemeral=True)
        
        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
            tagged_users = [user for user in msg.mentions]

            if not tagged_users:
                await select_interaction.followup.send("No users mentioned. Role assignment cancelled.", ephemeral=True)
                return

            # Assign the role to mentioned users
            for user in tagged_users:
                try:
                    await user.add_roles(selected_role)
                    await select_interaction.followup.send(f"Role '{selected_role.name}' assigned to {user.mention}.", ephemeral=True)
                except discord.Forbidden:
                    await select_interaction.followup.send(f"Could not assign role to {user.mention} due to permission restrictions.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to reply. Role assignment cancelled.", ephemeral=True)

    # Add the callback function to the dropdown
    role_select.callback = select_role_callback
    
    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    # Optionally, add a cancel button
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Role assignment canceled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a role to assign and then mention users.", view=view)

# Help command for the assignrole command
async def help_command(interaction):
    help_message = f"**Assign Role Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a role from a dropdown and assign it to multiple users by mentioning them.\n\n" \
                   "Steps:\n1. Select a role from the dropdown.\n2. Mention users to assign the selected role.\n" \
                   "3. The role will be assigned to mentioned users."
    await interaction.response.send_message(help_message)
