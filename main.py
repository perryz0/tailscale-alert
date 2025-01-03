from typing import Final

import discord
from discord.ext import commands, tasks
import os, logging
from dotenv import load_dotenv
from api.TailscaleAPI import TailscaleAPI
from settings.bot_context import BotContext
import asyncio

# Load .env variables
load_dotenv()
DISCORD_TOKEN: Final[str] = os.getenv('DISCORD_BOT_TOKEN')

# API and BOT setup
TAILSCALE_TOKEN: Final[str] = os.getenv('TAILSCALE_API_TOKEN')
ts = TailscaleAPI(api_token=TAILSCALE_TOKEN)
intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)
logging.basicConfig(level=logging.INFO)

context: BotContext = BotContext()

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user}")
    logging.info("Connected guilds:")
    for guild in client.guilds:
        logging.info(f"- {guild.name} (ID: {guild.id})")
    # Start background tasks
    monitor_tailnet_changes.start()


@client.command(name="ping", help="Check if the bot is running")
async def ping(ctx):
    await ctx.send("Pong! The bot is running.")

# Command: List Devices
@client.command(name="list_devices", help="List all devices on the Tailscale network")
async def list_devices(ctx):
    try:
        devices = ts.list_devices(context.tailnet)
        if not devices:
            await ctx.send("No devices found on the Tailscale network.")
            return
        
        device_list = "\n".join([f"- {device['hostname']} ({device['ip']})" for device in devices])
        await ctx.send(f"Devices on Tailscale:\n{device_list}")
    except Exception as e:
        logging.error(f"Error listing devices: {e}")
        await ctx.send("Failed to retrieve device list.")

# Background Task: Monitor Tailnet Changes
@tasks.loop(minutes=1)
async def monitor_tailnet_changes():
    """
    Periodically check for changes in the Tailscale network and send alerts to a Discord channel.
    """
    try:
        devices = ts.list_devices(context.tailnet)
        # Logic for detecting changes (e.g., new devices, disconnected devices)
        # Example:
        logging.info("Monitoring Tailnet for changes...")
    except Exception as e:
        logging.error(f"Error monitoring Tailnet: {e}")

# Error Handling: Command Errors
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Use `!help` to see available commands.")
    else:
        logging.error(f"Error occurred: {error}")
        await ctx.send("An unexpected error occurred. Please check the logs.")

# Run the bot
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
