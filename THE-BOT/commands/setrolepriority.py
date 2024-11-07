import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Role Priority",
    "category": "Role",
    "help": "This command allows users to view and modify the priority of a role by selecting a role and adjusting its priority in the role hierarchy."
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
        placeholder="Select a role to modify its priority",
        options=role_options
    )

    # Function to handle role selection and priority modification
    async def role_select_callback(select_interaction):
        selected_role_id = select_interaction.data['values'][0]
        selected_role = interaction.guild.get_role(int(selected_role_id))

        if not selected_role:
            await select_interaction.response.send_message("Role not found.", ephemeral=True)
            return

        # Show the current priority (position) of the role
        current_priority = selected_role.position
        await select_interaction.response.send_message(
            f"Current priority (position) of role `{selected_role.name}`: {current_priority}\n\n"
            "You can now modify the priority by selecting a new position.",
            ephemeral=True
        )

        # Create a dropdown to select the new priority
        priority_options = [
            discord.SelectOption(label=f"Position {i}", value=str(i))
            for i in range(len(roles)-1, -1, -1)  # Reverse the roles so the highest positions are at the top
            if roles[i] != selected_role and roles[i].position != selected_role.position
        ]
        
        # If there are no valid positions to modify, let the user know
        if not priority_options:
            await select_interaction.followup.send(f"Cannot modify the priority of `{selected_role.name}`. It may already be at the highest or lowest position.", ephemeral=True)
            return

        priority_select = Select(
            placeholder="Select a new position for the role",
            options=priority_options
        )

        # Function to handle priority change
        async def priority_select_callback(select_interaction):
            new_position = int(select_interaction.data['values'][0])

            # Move the role to the selected position in the hierarchy
            try:
                await selected_role.edit(position=new_position)
                await select_interaction.response.send_message(
                    f"The priority of the role `{selected_role.name}` has been updated to position {new_position}.", ephemeral=True
                )
            except discord.Forbidden:
                await select_interaction.response.send_message(f"Could not update the priority of `{selected_role.name}` due to permission restrictions.", ephemeral=True)

        # Add the callback function to the priority selection dropdown
        priority_select.callback = priority_select_callback

        # Add the dropdown to a view and send the message
        view = View()
        view.add_item(priority_select)

        await select_interaction.followup.send(
            f"Please select a new position for the role `{selected_role.name}` from the available positions.",
            view=view
        )

    # Add the callback function to the role selection dropdown
    role_select.callback = role_select_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(role_select)

    await interaction.response.send_message("Please select a role to modify its priority.", view=view)

# Help command for the setrolepriority command
async def help_command(interaction):
    help_message = f"**Set Role Priority Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to view and modify the priority (position) of a selected role.\n\n" \
                   "Steps:\n1. Select a role to modify.\n" \
                   "2. View the current priority (position) of the role.\n" \
                   "3. Select a new position (priority) for the role."
    await interaction.response.send_message(help_message)
