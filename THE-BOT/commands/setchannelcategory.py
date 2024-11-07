import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Channel Category",
    "category": "Channel",
    "help": "This command allows users to move multiple channels to a selected category using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Fetch all text and voice channels in the guild
    channels = [channel for channel in interaction.guild.channels if isinstance(channel, (discord.TextChannel, discord.VoiceChannel))]

    if not channels:
        await interaction.response.send_message("No channels available to move.", ephemeral=True)
        return

    # Create a dropdown menu to select categories
    categories = [category for category in interaction.guild.categories]

    if not categories:
        await interaction.response.send_message("No categories available to move channels to.", ephemeral=True)
        return

    category_options = [
        discord.SelectOption(label=category.name, value=str(category.id)) 
        for category in categories
    ]

    # Create a callback for when a category is selected
    async def select_category_callback(select_interaction):
        selected_category_id = select_interaction.data['values'][0]
        selected_category = interaction.guild.get_category(int(selected_category_id))

        if not selected_category:
            await select_interaction.response.send_message("Category not found.", ephemeral=True)
            return

        # Prompt user to mention multiple channels to move
        await select_interaction.response.send_message("Please mention the channels you want to move to the selected category.", ephemeral=True)

        def check(msg):
            return msg.author == interaction.user and msg.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
            mentioned_channels = [channel for channel in msg.content.split() if channel.startswith("#")]

            # Ensure the mentioned channels exist
            mentioned_channels_objects = []
            for channel_mention in mentioned_channels:
                channel_name = channel_mention[1:]  # Remove the "#" symbol
                channel = discord.utils.get(interaction.guild.channels, name=channel_name)
                if channel:
                    mentioned_channels_objects.append(channel)

            if not mentioned_channels_objects:
                await select_interaction.followup.send("No valid channels mentioned. Operation cancelled.", ephemeral=True)
                return

            # Move the mentioned channels to the selected category
            for channel in mentioned_channels_objects:
                try:
                    await channel.edit(category=selected_category)
                    await select_interaction.followup.send(f"Channel #{channel.name} has been moved to {selected_category.name}.", ephemeral=True)
                except discord.Forbidden:
                    await select_interaction.followup.send(f"Could not move channel #{channel.name} due to permission restrictions.", ephemeral=True)

        except asyncio.TimeoutError:
            await select_interaction.followup.send("You took too long to reply. Channel move operation cancelled.", ephemeral=True)

    # Add the callback to the category selection dropdown
    category_select = Select(
        placeholder="Select a category to move the channels to",
        options=category_options
    )
    category_select.callback = select_category_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(category_select)

    # Optionally, add a cancel button to the dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Channel move operation cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select a category to move channels to and then mention the channels (in #channel format).", view=view)

# Help command for the setchannelcategory command
async def help_command(interaction):
    help_message = f"**Set Channel Category Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a category and then move multiple channels to that category by mentioning them in the message.\n\n" \
                   "Steps:\n1. Select a category to move the channels to.\n" \
                   "2. Mention the channels in the format '#channel' that you want to move.\n" \
                   "3. The bot will move the selected channels to the chosen category."
    await interaction.response.send_message(help_message)
