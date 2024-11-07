import discord
from discord.ui import Select, View, Button, TextInput
from discord.ext import commands
import asyncio

metadata = {
    "name": "Create Role",
    "category": "Role",
    "help": "This command allows users to create new roles in the server with additional configuration options."
}

# Define the command
async def execute_command(interaction):
    # Define options for role permissions (default options: none, and basic role)
    permissions_options = [
        discord.SelectOption(label="No Permissions", value="none"),
        discord.SelectOption(label="Basic Permissions", value="basic"),
        discord.SelectOption(label="Administrator", value="admin")
    ]
    
    permissions_select = Select(
        placeholder="Select the permissions for the new role",
        options=permissions_options
    )

    # Create a callback for when a permission type is selected
    async def select_permissions_callback(select_interaction):
        selected_permission_type = select_interaction.data['values'][0]

        # Ask for the role name
        await select_interaction.response.send_message("Please enter the name for the new role:", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            # Wait for the role name input
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
            role_name = msg.content.strip()

            if not role_name:
                await select_interaction.followup.send("No role name provided. Role creation cancelled.", ephemeral=True)
                return

            # Additional options for role creation
            create_color_input = TextInput(
                label="Role Color (Optional, Hex Code or Name)",
                style=discord.TextStyle.short,
                required=False
            )

            # Create a view for the text input and a cancel button
            view = View()
            view.add_item(create_color_input)

            # Button to cancel the creation
            cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

            async def cancel_button_callback(interaction):
                await interaction.response.send_message("Role creation cancelled.", ephemeral=True)

            cancel_button.callback = cancel_button_callback
            view.add_item(cancel_button)

            await select_interaction.followup.send(
                "Please provide an optional color for the role (can be a hex code or color name). You can skip it if you don't want a color.",
                view=view,
                ephemeral=True
            )

            # Wait for the optional role color input
            try:
                color_msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
                role_color = color_msg.content.strip()
            except asyncio.TimeoutError:
                role_color = None

            # Convert role color (if provided) to a valid color
            if role_color:
                try:
                    if role_color.startswith("#"):  # Hex code format
                        role_color = int(role_color.lstrip('#'), 16)
                    else:  # Name format
                        role_color = discord.Color(role_color)
                except Exception:
                    await select_interaction.followup.send("Invalid color format. Skipping color.", ephemeral=True)
                    role_color = None

            # Create role with the specified permissions
            permissions = discord.Permissions()

            if selected_permission_type == "none":
                permissions = discord.Permissions.none()
            elif selected_permission_type == "basic":
                permissions = discord.Permissions(send_messages=True, read_messages=True)
            elif selected_permission_type == "admin":
                permissions = discord.Permissions.administrator()

            # Create the role
            await interaction.guild.create_role(
                name=role_name,
                permissions=permissions,
                color=role_color or discord.Color.default()
            )
            await select_interaction.followup.send(f"Role '{role_name}' created successfully!", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to reply. Role creation cancelled.", ephemeral=True)

    # Add the callback to the permission selection dropdown
    permissions_select.callback = select_permissions_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(permissions_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Role creation cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select the permissions for the new role.", view=view)

# Help command for the createrole command
async def help_command(interaction):
    help_message = f"**Create Role Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to create a new role in the server by selecting the permissions, providing a name, and optionally adding a color.\n\n" \
                   "Steps:\n1. Select the permissions for the new role (e.g., No Permissions, Basic Permissions, Administrator).\n" \
                   "2. Provide a name for the new role.\n" \
                   "3. Optionally, provide a color for the role.\n" \
                   "4. The role will be created with the specified settings."
    await interaction.response.send_message(help_message)
