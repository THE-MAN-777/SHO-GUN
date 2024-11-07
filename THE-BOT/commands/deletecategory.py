import discord
from discord.ui import Select, View, Button
from discord.ext import commands
import asyncio

metadata = {
    "name": "Delete Category",
    "category": "Category",
    "help": "This command allows users to delete a category and all channels inside it."
}

# Define the command
async def execute_command(interaction):
    # Fetch all categories in the server
    categories = interaction.guild.categories
    category_options = [
        discord.SelectOption(label=category.name, value=str(category.id)) 
        for category in categories
    ]
    
    if not category_options:
        await interaction.response.send_message("No categories available to delete.", ephemeral=True)
        return

    category_select = Select(
        placeholder="Select the category to delete",
        options=category_options
    )

    # Create a callback for when a category is selected
    async def select_category_callback(select_interaction):
        selected_category_id = select_interaction.data['values'][0]
        selected_category = interaction.guild.get_channel(int(selected_category_id))

        if not selected_category or not isinstance(selected_category, discord.CategoryChannel):
            await select_interaction.response.send_message("Category not found.", ephemeral=True)
            return

        # Confirm the deletion
        confirm_button = Button(label="Confirm", style=discord.ButtonStyle.red)
        cancel_button = Button(label="Cancel", style=discord.ButtonStyle.green)

        async def confirm_button_callback(interaction):
            try:
                # Delete all channels within the category
                for channel in selected_category.channels:
                    await channel.delete()

                # Delete the category
                await selected_category.delete()

                await interaction.response.send_message(f"Category '{selected_category.name}' and all its channels have been deleted.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("I do not have permission to delete this category or its channels.", ephemeral=True)

        async def cancel_button_callback(interaction):
            await interaction.response.send_message("Category deletion cancelled.", ephemeral=True)

        confirm_button.callback = confirm_button_callback
        cancel_button.callback = cancel_button_callback

        # Add the buttons to a view
        view = View()
        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await select_interaction.response.send_message(f"Are you sure you want to delete the category '{selected_category.name}' and all its channels?", view=view, ephemeral=True)

    # Add the callback to the category selection dropdown
    category_select.callback = select_category_callback

    # Add the dropdown to a view and send the message
    view = View()
    view.add_item(category_select)

    # Optionally, add a cancel button to the initial dropdown
    cancel_button = Button(label="Cancel", style=discord.ButtonStyle.red)

    async def cancel_button_callback(interaction):
        await interaction.response.send_message("Category deletion cancelled.", ephemeral=True)

    cancel_button.callback = cancel_button_callback
    view.add_item(cancel_button)

    await interaction.response.send_message("Please select the category to delete.", view=view)

# Help command for the deletecategory command
async def help_command(interaction):
    help_message = f"**Delete Category Command**\n\n{metadata['help']}\n\n" \
                   "This command allows you to select a category and delete it along with all channels inside it.\n\n" \
                   "Steps:\n1. Select the category you want to delete.\n" \
                   "2. Confirm the deletion.\n" \
                   "3. All channels within the selected category will be deleted along with the category itself."
    await interaction.response.send_message(help_message)
