import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "Toggle Mentionable Role",
    "category": "Role",
    "help": "This command allows users to toggle the mentionable permission of a role using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Fetch all the roles in the server
    roles = interaction.guild.roles
    role_options = [
        discord.SelectOption(label=role.name, value=str(role.id))
        for role in roles if role != interaction.guild.default_role  # Exclude @everyone
    ]

    if not role_options:
        await interaction.response.send_message("No roles available to modify.", ephemeral=True)
        return

    # Create a dropdown menu for roles
    role_select = Select(
        placeholder="Select a role to toggle mentionable permission",
        options=role_options
    )

    # Function to handle role selection
    async def role_select_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Show current mentionable status of the selected role
        mentionable_status = "mentionable" if selected_role.mentionable else "not mentionable"
        await select_interaction.response.send_message(
            f"Role '{selected_role.name}' is currently {mentionable_status}. Would you like to toggle it?",
            ephemeral=True
        )

        # Ask for confirmation to toggle mentionable status
        await select_interaction.followup.send("React with ✅ to toggle or ❌ to cancel.", ephemeral=True)

        # Wait for the user to react
        def check(reaction, user):
            return user == interaction.user and reaction.message.author == interaction.user and reaction.emoji in ['✅', '❌']

        try:
            # Wait for the reaction (confirmation)
            reaction, user = await interaction.client.wait_for('reaction_add', check=check, timeout=60.0)

            if reaction.emoji == '✅':
                # Toggle the mentionable status
                new_mentionable_status = not selected_role.mentionable
                await selected_role.edit(mentionable=new_mentionable_status)
                new_status = "mentionable" if new_mentionable_status else "not mentionable"
                await select_interaction.followup.send(
                    f"The mentionable status of '{selected_role.name}' has been changed to {new_status}.", ephemeral=True
                )
            else:
                await select_interaction.followup.send("Operation canceled. No changes were made.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to respond. The operation has been canceled.", ephemeral=True)

    # Add the callback function to the dropdown
    role_select.callback = role_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)
    await interaction.response.send_message("Please select a role to modify its mentionable status.", view=view)

# Help command for the togglementionable command
async def help_command(interaction):
    help_message = f"**Toggle Mentionable Role Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to toggle the mentionable status of a role using a dropdown menu.\n\n" \
                   "Steps:\n1. Select a role from the dropdown.\n" \
                   "2. The bot will show you the current mentionable status.\n" \
                   "3. React with ✅ to toggle the status or ❌ to cancel."
    await interaction.response.send_message(help_message)
