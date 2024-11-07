import discord
from discord.ui import Select, View
from discord.ext import commands
import asyncio

metadata = {
    "name": "View Permissions",
    "category": "Permissions",
    "help": "This command allows users to view the permissions of roles, channels, or users."
}

# Define the command
async def execute_command(interaction):
    # Ask the user to specify if they want to view permissions for a role, channel, or user
    options = [
        discord.SelectOption(label="Role", value="role"),
        discord.SelectOption(label="Channel", value="channel"),
        discord.SelectOption(label="User", value="user")
    ]

    # Create a dropdown to select the type (role, channel, or user)
    type_select = Select(
        placeholder="Select the type of entity to view permissions",
        options=options
    )

    # Function to handle selection of the type
    async def type_select_callback(select_interaction):
        selected_type = select_interaction.data['values'][0]

        if selected_type == "role":
            # Fetch all roles in the guild for the dropdown
            roles = interaction.guild.roles
            role_options = [
                discord.SelectOption(label=role.name, value=str(role.id))
                for role in roles if role != interaction.guild.default_role  # Exclude @everyone
            ]

            if not role_options:
                await select_interaction.response.send_message("No roles available to display.", ephemeral=True)
                return

            # Create dropdown to select a role
            role_select = Select(
                placeholder="Select a role to view permissions",
                options=role_options
            )

            # Function to handle role selection
            async def role_select_callback(role_interaction):
                selected_role_id = role_interaction.data['values'][0]
                selected_role = interaction.guild.get_role(int(selected_role_id))

                if not selected_role:
                    await role_interaction.response.send_message("Role not found.", ephemeral=True)
                    return

                # Fetch and display the role permissions
                permissions = selected_role.permissions
                perms_list = [f"**{perm.name}**: {'✅' if permissions[perm] else '❌'}" for perm in permissions]

                perms_message = f"Permissions for role **{selected_role.name}**:\n\n" + "\n".join(perms_list)
                await role_interaction.response.send_message(perms_message, ephemeral=True)

            # Add callback for role dropdown
            role_select.callback = role_select_callback

            # Add dropdown to a view and send the message
            view = View()
            view.add_item(role_select)
            await select_interaction.response.send_message("Please select a role to view its permissions.", view=view)

        elif selected_type == "channel":
            # Fetch all text channels in the guild for the dropdown
            channels = interaction.guild.text_channels
            channel_options = [
                discord.SelectOption(label=channel.name, value=str(channel.id))
                for channel in channels
            ]

            if not channel_options:
                await select_interaction.response.send_message("No channels available to display.", ephemeral=True)
                return

            # Create dropdown to select a channel
            channel_select = Select(
                placeholder="Select a channel to view permissions",
                options=channel_options
            )

            # Function to handle channel selection
            async def channel_select_callback(channel_interaction):
                selected_channel_id = channel_interaction.data['values'][0]
                selected_channel = interaction.guild.get_channel(int(selected_channel_id))

                if not selected_channel:
                    await channel_interaction.response.send_message("Channel not found.", ephemeral=True)
                    return

                # Fetch and display the channel permissions
                permissions = selected_channel.permissions_for(interaction.guild.default_role)
                perms_list = [f"**{perm}**: {'✅' if getattr(permissions, perm) else '❌'}" for perm in permissions]

                perms_message = f"Permissions for channel **{selected_channel.name}**:\n\n" + "\n".join(perms_list)
                await channel_interaction.response.send_message(perms_message, ephemeral=True)

            # Add callback for channel dropdown
            channel_select.callback = channel_select_callback

            # Add dropdown to a view and send the message
            view = View()
            view.add_item(channel_select)
            await select_interaction.response.send_message("Please select a channel to view its permissions.", view=view)

        elif selected_type == "user":
            # Ask user to tag a user to view their permissions
            await select_interaction.response.send_message("Please mention a user to view their permissions.", ephemeral=True)

            # Check if the user has tagged someone
            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel and len(msg.mentions) == 1

            try:
                msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
                mentioned_user = msg.mentions[0]

                # Fetch and display the user permissions for each channel
                perms_message = f"Permissions for user **{mentioned_user.name}**:\n\n"
                for channel in interaction.guild.text_channels:
                    permissions = channel.permissions_for(mentioned_user)
                    perms_list = [f"**{perm}**: {'✅' if getattr(permissions, perm) else '❌'}" for perm in permissions]
                    perms_message += f"**{channel.name}**:\n" + "\n".join(perms_list) + "\n\n"

                await msg.reply(perms_message)

            except asyncio.TimeoutError:
                await select_interaction.followup.send("You took too long to mention a user. Permissions viewing cancelled.", ephemeral=True)

    # Add the callback function to the type selection dropdown
    type_select.callback = type_select_callback

    # Add dropdown to a view and send the message
    view = View()
    view.add_item(type_select)
    await interaction.response.send_message("Please select the type of entity to view permissions (Role, Channel, or User).", view=view)

# Help command for the viewperms command
async def help_command(interaction):
    help_message = f"**View Permissions Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to view the permissions of roles, channels, or users.\n\n" \
                   "Steps:\n1. Select whether you want to view permissions for a role, channel, or user.\n" \
                   "2. For roles and channels, select from the dropdown. For users, mention the user in the chat.\n" \
                   "3. The bot will show the permissions and their current status (True/False)."
    await interaction.response.send_message(help_message)
