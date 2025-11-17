import logging

import discord
from discord import app_commands
from discord.ext import commands

import settings
from utils import get_message

from .ui.views import TicketView

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True  
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=settings.ALLOWED_GUILD))
    logging.info(f"Logged in as {bot.user}")

    channel = bot.get_channel(int(settings.CREATE_TICKET_CHANNEL))
    if not channel:
        logging.error("CREATE_TICKET_CHANNEL not found or invalid ID.")
        return
    
    try:
        await channel.purge(limit=50) 
    except Exception as e:
        logging.error(f"Could not purge channel: {e}")

    color = getattr(discord.Color, get_message("messages.embeds.ticket_reason_select.color"))()
    embed = discord.Embed(
        title=get_message("messages.embeds.ticket_reason_select.title"),
        description=get_message("messages.embeds.ticket_reason_select.description"),
        color=color,
    )
    await channel.send(embed=embed, view=TicketView())
    
    logging.info(f"Channel #{channel.name} cleared, new message was send")


def run_bot():
    bot.run(settings.BOT_TOKEN)
