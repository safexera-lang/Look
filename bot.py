import discord
import aiohttp
import re
import os
import asyncio
import json
from discord.ext import commands
from datetime import datetime, timezone
import pytz
import time
import io
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup with correct intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# API Configuration
API_URL = "https://lostingness.site/osintx/mobile/api.php?key=c365a7d9-1c91-43c9-933d-da0ac38827ad&number={number}"

# Developer Information
DEVELOPER_INFO = {
    'discord': 'https://discord.com/users/1355605971858100249',
    'instagram': 'https://instagram.com/lostingness/',
    'developer': '@Lostingness'
}

class PremiumStyles:
    # Premium Colors
    PRIMARY = 0x5865F2
    SUCCESS = 0x57F287
    ERROR = 0xED4245
    WARNING = 0xFEE75C
    INFO = 0x3498DB
    PREMIUM = 0x9B59B6

# Global variables for stats
bot.start_time = datetime.now(timezone.utc)
search_count = 0

def get_indian_time():
    """Get current Indian time"""
    try:
        ist = pytz.timezone('Asia/Kolkata')
        return datetime.now(ist).strftime("%d %b %Y • %I:%M %p IST")
    except Exception:
        return datetime.now(timezone.utc).strftime("%d %b %Y • %I:%M %p UTC")

def get_uptime():
    """Calculate bot uptime"""
    try:
        delta = datetime.now(timezone.utc) - bot.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        else:
            return f"{hours}h {minutes}m {seconds}s"
    except Exception:
        return "Unknown"

def clean_text(text):
    """Advanced text cleaning"""
    if not text or str(text).strip() in ["", "null", "None", "N/A", "NA"]:
        return "🚫 Not Available"

    try:
        text = str(text).strip()
        text = re.sub(r'[!@#$%^&*()_+=`~\[\]{}|\\:;"<>?]', ' ', text)
        text = re.sub(r'[.!]+$', '', text)
        text = re.sub(r'\s+', ' ', text)

        if '@' not in text:
            words = text.split()
            cleaned_words = []
            for word in words:
                if word.upper() in ['II', 'III', 'IV', 'VI', 'VII', 'VIII']:
                    cleaned_words.append(word.upper())
                elif len(word) > 1:
                    cleaned_words.append(word[0].upper() + word[1:].lower())
                else:
                    cleaned_words.append(word.upper())
            text = ' '.join(cleaned_words)

        return text
    except Exception:
        return "🚫 Not Available"

@bot.event
async def on_ready():
    logger.info("🚀 Premium Mobile Search Bot Online!")
    logger.info("💎 Developed By @Lostingness")

    try:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Mobile Numbers | !help"
        )
        await bot.change_presence(activity=activity)
    except Exception as e:
        logger.error(f"Error setting presence: {e}")

@bot.command()
async def search(ctx, *, number: str = None):
    """Premium mobile number search"""
    global search_count

    if not number:
        embed = discord.Embed(
            title="ℹ️ Mobile Search",
            description="**Usage:** `!search 7405453929`",
            color=0x3498DB
        )
        await ctx.send(embed=embed)
        return

    # Extract numbers from input
    numbers = re.findall(r'\d{10}', number)
    if not numbers:
        embed = discord.Embed(
            title="❌ Invalid Input",
            description="Please provide a valid 10-digit mobile number.",
            color=0xED4245
        )
        await ctx.send(embed=embed)
        return

    number = numbers[0]
    search_count += 1

    # Show searching embed
    search_embed = discord.Embed(
        title="🚀 Searching...",
        description=f"Searching for: `{number}`",
        color=0x5865F2
    )
    search_msg = await ctx.send(embed=search_embed)

    try:
        # API Request
        url = API_URL.format(number=number)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    raise Exception(f"API returned status {response.status}")

        # Process response
        if isinstance(data, dict) and data.get("error"):
            error_embed = discord.Embed(
                title="❌ Search Failed",
                description=f"Error: {data.get('error', 'Unknown error')}",
                color=0xED4245
            )
            await search_msg.edit(embed=error_embed)
            return

        if not data or (isinstance(data, list) and len(data) == 0):
            no_data_embed = discord.Embed(
                title="⚠️ No Records Found",
                description=f"No records found for: `{number}`",
                color=0xFEE75C
            )
            await search_msg.edit(embed=no_data_embed)
            return

        # Successful search
        await search_msg.delete()

        records = data if isinstance(data, list) else [data]

        for index, record in enumerate(records, 1):
            embed = discord.Embed(
                title=f"📱 Search Result {index}",
                color=0x57F287
            )

            name = clean_text(record.get('name', 'N/A'))
            mobile = record.get('mobile', number)

            embed.add_field(name="📱 Mobile", value=f"`{mobile}`", inline=True)
            embed.add_field(name="👤 Name", value=f"`{name}`", inline=True)

            embed.set_footer(text=f"Developer: @Lostingness • {get_indian_time()}")

            await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Search error: {e}")
        error_embed = discord.Embed(
            title="❌ Search Error",
            description="An error occurred while searching.",
            color=0xED4245
        )
        await search_msg.edit(embed=error_embed)

@bot.command()
async def help(ctx):
    """Help command"""
    embed = discord.Embed(
        title="🆘 Bot Help",
        description="Mobile Number Search Bot Commands",
        color=0x3498DB
    )

    embed.add_field(
        name="🔍 Search Commands",
        value="`!search 7405453929` - Search mobile number",
        inline=False
    )

    embed.add_field(
        name="📊 Info Commands",
        value="`!help` - This help\n`!ping` - Check latency",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Latency: `{latency}ms`",
        color=0x57F287
    )

    await ctx.send(embed=embed)

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")

    if not token:
        logger.error("❌ No DISCORD_BOT_TOKEN environment variable found!")
        exit(1)

    logger.info("🚀 Starting bot...")

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token!")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
