import discord
from discord.ui import Select, View, Button, TextInput
from discord.ext import commands
import asyncio

metadata = {
    "name": "Create Channel",
    "category": "Channel",
    "help": "This command allows users to create new text or voice channels in the server with additional configuration options."
}

# Define the command
async def execute_command(interaction):
    # Define options for channel type (text or voice)
    channel_options = [
        discord.SelectOption(label="Text Channel", value="text"),
        discord.SelectOption(label="Voice Channel", value="voice")
    ]

    channel_select = Select(
        placeholder="Select the type of channel to create",
        options=channel_options
    )

    # Create a callback for when a channel type is selected
    async def select_channel_callback(select_interaction):
        selected_channel_type = select_interaction.data['values'][0]

        # Ask for the channel name
        await select_interaction.response.send_message("Please enter the name for the new channel:", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            # Wait for the channel name input
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
            channel_name = msg.content

            if not channel_name:
                await select_interaction.followup.send("No channel name provided. Channel creation cancelled.", ephemeral=True)
                return

            # Additional options for channel creation
            create_text_input = TextInput(
                label="Channel Topic (Optional)",
                style=discord.TextStyle.short,
                required=False
            )

            # Create a view for the text input and a cancel button
            view = View()
            view.add_item(create_text_input)

            # Button to cancel the creation
            cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

            async def cancel_button_callback(interaction):
                await interaction.response.send_message("Channel creation cancelled.", ephemeral=True)

            cancel_button.callback = cancel_button_callback
            view.add_item(cancel_button)

            await select_interaction.followup.send(
                "Please provide an optional topic for the channel or leave it blank to skip.", 
                view=view,
                ephemeral=True
            )

            # Wait for the optional channel topic input
            try:
                topic_msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
                channel_topic = topic_msg.content.strip()
            except asyncio.TimeoutError:
                channel_topic = ""

            # Proceed to create the channel
            if selected_channel_type == "text":
                await interaction.guild.create_text_channel(channel_name, topic=channel_topic)
                await select_interaction.followup.send(f"Text channel '{channel_name}' created successfully!", ephemeral=True)
            elif selected_channel_type == "voice":
                await interaction.guild.create_voice_channel(channel_name, topic=channel_topic)
                await select_interaction.followup.send(f"Voice channel '{channel_name}' created successfully!", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to reply. Channel creation cancelled.", ephemeral=True)

    # Add the callback to the channel selection dropdown
    channel_select.callback = select_channel_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(channel_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel creation cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select the type of channel to create.", view=view)

# Help command for the createchannel command
async def help_command(interaction):
    help_message = f"**Create Channel Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to create a new channel in the server by selecting the type (text or voice), providing a name, and optionally adding a topic.\n\n" \
                   "Steps:\n1. Select the type of channel you want to create (Text or Voice).\n" \
                   "2. Provide a name for the new channel.\n" \
                   "3. Optionally, provide a topic for the channel.\n" \
                   "4. The channel will be created in the server."
    await interaction.response.send_message(help_message)
