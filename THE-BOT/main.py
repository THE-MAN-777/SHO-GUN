import discord
from discord.ext import commands
import os
import importlib
import logging

# Setup logging to catch issues
logging.basicConfig(level=logging.INFO)

# Bot setup with Message Content Intent
intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

# Function to load commands from files
def load_commands():
    commands_data = {}
    command_files = [f for f in os.listdir('./commands') if f.endswith('.py') and f != '__init__.py']
    
    for file in command_files:
        try:
            module_name = f'commands.{file[:-3]}'
            module = importlib.import_module(module_name)
            
            # Check for metadata
            if hasattr(module, 'metadata'):
                metadata = module.metadata
                if 'category' not in metadata or 'name' not in metadata:
                    raise ValueError(f"Missing category or name in metadata for {file}")
                
                if metadata["category"] not in commands_data:
                    commands_data[metadata["category"]] = []
                
                commands_data[metadata["category"]].append(metadata)
            else:
                logging.warning(f"Skipping {file}: No metadata found.")
        except Exception as e:
            logging.error(f"Error loading command from {file}: {str(e)}")
    
    return commands_data

@bot.command()
async def menu(ctx):
    commands_data = load_commands()
    
    # Create a new view for each category
    current_view = discord.ui.View()

    # Add category buttons
    for category, commands in commands_data.items():
        if len(current_view.children) >= 25:  # Max limit for buttons per view
            current_view = discord.ui.View()  # Create a new view if the limit is reached
        
        # Add a button for the category
        category_button = discord.ui.Button(
            label=category,
            style=discord.ButtonStyle.primary,
            custom_id=category
        )

        # Function that will handle the button click (open commands within category)
        async def category_button_callback(interaction, cat_name=category):
            await show_category_commands(interaction, cat_name)

        category_button.callback = category_button_callback
        current_view.add_item(category_button)

    # Send the categories menu with one view at a time
    await ctx.send("Here are the command categories:", view=current_view)
    
    # If you have multiple views to send (like if there were too many buttons):
    for view in views:
        await ctx.send("Here are the command categories:", view=view)

# Show commands within a selected category
async def show_category_commands(interaction, category):
    commands_data = load_commands()
    
    # Check if the category exists
    if category not in commands_data:
        await interaction.response.send_message(f"No commands found for category: {category}", ephemeral=True)
        return

    # Create a new view for commands within the selected category
    current_view = discord.ui.View()
    for command in commands_data[category]:
        # Add each command as a button
        command_button = discord.ui.Button(
            label=command["name"],
            style=discord.ButtonStyle.primary,
            custom_id=command["name"]
        )

        # Define the callback for executing the command
        async def command_button_callback(interaction, cmd_name=command["name"]):
            await execute_command(interaction, cmd_name)

        command_button.callback = command_button_callback
        current_view.add_item(command_button)

    # Add a back button to return to the categories menu
    back_button = discord.ui.Button(label="Back", style=discord.ButtonStyle.secondary)

    async def back_button_callback(interaction):
        await menu(interaction)

    back_button.callback = back_button_callback
    current_view.add_item(back_button)

    # Send the commands under the selected category
    await interaction.response.send_message(f"Commands in category: {category}", view=current_view)

    # Help button
    help_button = discord.ui.Button(label="Help", style=discord.ButtonStyle.secondary)
    
    # Help dropdown logic
    async def help_callback(interaction):
        help_select = discord.ui.Select(
            placeholder="Select a command to get help...",
            options=[discord.SelectOption(label=cmd["name"], value=cmd["name"]) for cmds in commands_data.values() for cmd in cmds]
        )

        async def select_callback(select_interaction):
            command_name = select_interaction.data['values'][0]
            await show_help(select_interaction, command_name)

        help_select.callback = select_callback
        
        await interaction.response.send_message(content="Select a command to get help:", ephemeral=True, view=discord.ui.View(help_select))

    help_button.callback = help_callback
    current_view.add_item(help_button)

    # Send multiple views if needed
    for view in views:
        await ctx.send("Here is the command menu:", view=view)

# Execute command
async def execute_command(interaction, command_name):
    # Normalize command_name for file matching
    normalized_command_name = command_name.lower().replace(" ", "").replace("_", "")  # Normalize spaces and underscores
    module_name = f'commands.{normalized_command_name}'
    
    try:
        # Attempt to load the module with the normalized name
        module = importlib.import_module(module_name)
        
        # Call the command execution function directly
        if hasattr(module, 'execute_command'):
            await module.execute_command(interaction)
        else:
            await interaction.response.send_message(f"Command '{command_name}' not found.")
    except ModuleNotFoundError as e:
        # Error if module is not found
        await interaction.response.send_message(f"Module for command '{command_name}' could not be found: {str(e)}")
    except Exception as e:
        # General error handling
        await interaction.response.send_message(f"Error executing command '{command_name}': {str(e)}")

# Help command execution
async def show_help(interaction, command_name):
    module_name = f'commands.{command_name.lower().replace(" ", "_")}'
    try:
        module = importlib.import_module(module_name)
        
        if hasattr(module, 'help_command'):
            await module.help_command(interaction)
        else:
            await interaction.response.send_message(f"No help available for '{command_name}'.")
    except Exception as e:
        await interaction.response.send_message(f"Error loading help for '{command_name}': {str(e)}")

# Reload commands with !bonk
@bot.command()
async def bonk(ctx):
    """Reloads all command modules."""
    try:
        # Reload all modules in the commands directory
        command_files = [f for f in os.listdir('./commands') if f.endswith('.py') and f != '__init__.py']
        
        for file in command_files:
            try:
                module_name = f'commands.{file[:-3]}'
                # Reload the module
                importlib.reload(importlib.import_module(module_name))
                logging.info(f"Reloaded command module: {file}")
            except Exception as e:
                logging.error(f"Error reloading {file}: {e}")
        
        await ctx.send("Command modules have been reloaded!")
    except Exception as e:
        await ctx.send(f"Failed to reload commands: {str(e)}")

# Safe token handling: Load token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')  # Ensure the token is stored in an environment variable

if not TOKEN:
    raise ValueError("Bot token is missing. Please set it in the environment variables.")

bot.run(TOKEN)
