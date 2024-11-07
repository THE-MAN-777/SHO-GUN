import discord
from discord.ui import View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Set Channel Topic",
    "category": "Channel",
    "help": "This command allows users to set the topic of a specific channel by mentioning it."
}

# Define the command
async def execute_command(interaction):
    # Prompt the user to mention the channel they want to change the topic for
    await interaction.response.send_message("Please mention the channel you want to set the topic for (e.g. #channel).", ephemeral=True)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        # Wait for the user to mention the channel
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

        # Extract the mentioned channel from the message
        mentioned_channel = discord.utils.get(interaction.guild.channels, mention=msg.content.split()[0])

        if not mentioned_channel:
            await interaction.followup.send("Invalid channel mentioned. Please try again.", ephemeral=True)
            return

        # Prompt the user to enter a new topic for the channel
        await interaction.followup.send(f"Please enter the new topic for the channel {mentioned_channel.mention}:", ephemeral=True)

        # Wait for the user to provide the new topic
        topic_msg = await interaction.client.wait_for('message', check=check, timeout=60.0)

        new_topic = topic_msg.content

        # Set the new topic for the mentioned channel
        try:
            await mentioned_channel.edit(topic=new_topic)
            await interaction.followup.send(f"Topic for {mentioned_channel.mention} has been set to: {new_topic}", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"Could not set the topic for {mentioned_channel.mention} due to permission restrictions.", ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to reply. Operation cancelled.", ephemeral=True)

# Help command for the setchanneltopic command
async def help_command(interaction):
    help_message = f"**Set Channel Topic Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to set the topic for a specific channel by mentioning it.\n\n" \
                   "Steps:\n1. Mention the channel you want to set the topic for.\n" \
                   "2. Enter the new topic for the channel.\n" \
                   "3. The bot will update the channel topic accordingly."
    await interaction.response.send_message(help_message)
