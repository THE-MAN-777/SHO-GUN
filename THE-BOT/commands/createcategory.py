import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Create Category",
    "category": "category",
    "help": "This command allows users to create new categories in the server using a dropdown menu."
}

# Define the command
async def execute_command(interaction):
    # Create a prompt for the category name
    await interaction.response.send_message("Please enter the name for the new category:", ephemeral=True)

    def check(msg):
        return msg.author == interaction.user and msg.channel == interaction.channel

    try:
        # Wait for the category name input
        msg = await interaction.client.wait_for('message', check=check, timeout=60.0)
        category_name = msg.content

        if not category_name:
            await interaction.followup.send("No category name provided. Category creation cancelled.", ephemeral=True)
            return

        # Create the category without specifying channel type
        category = await interaction.guild.create_category(category_name)

        await interaction.followup.send(f"Category '{category_name}' created successfully!", ephemeral=True)

    except asyncio.TimeoutError:
        await interaction.followup.send("You took too long to reply. Category creation cancelled.", ephemeral=True)

# Help command for the createcategory command
async def help_command(interaction):
    help_message = f"**Create Category Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to create a new category in the server by providing a name.\n\n" \
                   "Steps:\n1. Enter the name of the category you want to create.\n" \
                   "2. The category will be created in the server."
    await interaction.response.send_message(help_message)
