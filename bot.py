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

# Bot setup with correct intents (NO VOICE)
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
    PRIMARY = 0x5865F2
    SUCCESS = 0x57F287
    ERROR = 0xED4245
    WARNING = 0xFEE75C
    INFO = 0x3498DB
    PREMIUM = 0x9B59B6

# Global variables
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

def format_address(address):
    """Premium address formatting"""
    if not address or str(address).strip() in ["", "null", "None", "N/A"]:
        return "🚫 Address Not Available"

    try:
        address = str(address)
        address = re.sub(r'[.!*#-]+', ', ', address)
        address = re.sub(r'\s*,\s*', ', ', address)
        address = re.sub(r'\s+', ' ', address)
        address = address.strip().strip(',')

        parts = [part.strip() for part in address.split(',') if part.strip()]
        formatted_parts = []

        for part in parts:
            if part.upper() in ['DELHI', 'MUMBAI', 'KOLKATA', 'CHENNAI', 'BANGALORE', 'HYDERABAD']:
                formatted_parts.append(part.upper())
            else:
                formatted_parts.append(part.title())

        return ', '.join(formatted_parts)
    except Exception:
        return "🚫 Address Not Available"

@bot.event
async def on_ready():
    logger.info("🚀 Premium Mobile Search Bot Online!")
    logger.info("💎 Developed By @Lostingness")
    logger.info(f"📊 Connected to {len(bot.guilds)} servers")

    try:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Mobile Numbers | !help"
        )
        await bot.change_presence(activity=activity)
        logger.info("✅ Presence set successfully")
    except Exception as e:
        logger.error(f"Error setting presence: {e}")

@bot.event
async def on_guild_join(guild):
    """Welcome message on server join"""
    try:
        if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
            channel = guild.system_channel
        else:
            channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)

        if channel:
            embed = discord.Embed(
                title="👋 Thanks for adding Mobile Search Bot!",
                description="**Advanced mobile number lookup**",
                color=0x5865F2
            )
            embed.add_field(
                name="🚀 Quick Start",
                value="• Use `!search 7405453929`\n• Type any 10-digit number\n• Use `!help` for commands",
                inline=False
            )
            await channel.send(embed=embed)
            logger.info(f"✅ Welcome message sent to {guild.name}")
    except Exception as e:
        logger.error(f"Welcome message error: {e}")

class PremiumSearchView(discord.ui.View):
    """Interactive buttons"""
    def __init__(self, ctx, records, number):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.records = records
        self.number = number

    @discord.ui.button(label='📋 JSON Export', style=discord.ButtonStyle.primary)
    async def copy_json(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)

            copy_data = {
                "search_number": self.number,
                "timestamp": get_indian_time(),
                "total_records": len(self.records),
                "records": self.records
            }

            json_str = json.dumps(copy_data, indent=2, ensure_ascii=False)

            if len(json_str) > 2000:
                file_buffer = io.BytesIO(json_str.encode('utf-8'))
                file = discord.File(fp=file_buffer, filename=f"search_{self.number}.json")
                await interaction.followup.send("✅ JSON export:", file=file, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="📋 JSON Data",
                    description=f"```json\n{json_str}\n```",
                    color=0x9B59B6
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"JSON export error: {e}")
            await interaction.followup.send("❌ Export failed", ephemeral=True)

    @discord.ui.button(label='📱 Text Export', style=discord.ButtonStyle.secondary)
    async def export_text(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)

            text_content = f"🔍 MOBILE SEARCH RESULTS\n{'='*30}\n\n"
            text_content += f"📱 Number: {self.number}\n"
            text_content += f"📅 Time: {get_indian_time()}\n"
            text_content += f"📊 Records: {len(self.records)}\n\n"

            for i, record in enumerate(self.records, 1):
                text_content += f"{'─'*30}\nRECORD {i}\n{'─'*30}\n"
                text_content += f"📱 Mobile: {record.get('mobile', 'N/A')}\n"
                text_content += f"👤 Name: {clean_text(record.get('name', 'N/A'))}\n"
                text_content += f"👨‍👦 Father: {clean_text(record.get('father_name', 'N/A'))}\n"
                text_content += f"🏠 Address: {format_address(record.get('address', 'N/A'))}\n\n"

            file_buffer = io.BytesIO(text_content.encode('utf-8'))
            file = discord.File(fp=file_buffer, filename=f"search_{self.number}.txt")

            await interaction.followup.send("📥 Text export:", file=file, ephemeral=True)
        except Exception as e:
            logger.error(f"Text export error: {e}")
            await interaction.followup.send("❌ Export failed", ephemeral=True)

@bot.command()
async def search(ctx, *, number: str = None):
    """Search mobile number"""
    global search_count

    if not number:
        embed = discord.Embed(
            title="ℹ️ Mobile Search",
            description="**Usage:** `!search 7405453929`",
            color=0x3498DB
        )
        await ctx.send(embed=embed)
        return

    numbers = re.findall(r'\d{10}', number)
    if not numbers:
        embed = discord.Embed(
            title="❌ Invalid Input",
            description="Provide a valid 10-digit number.",
            color=0xED4245
        )
        await ctx.send(embed=embed)
        return

    number = numbers[0]
    search_count += 1

    search_embed = discord.Embed(
        title="🚀 Searching...",
        description=f"Target: `{number}`",
        color=0x5865F2
    )
    search_msg = await ctx.send(embed=search_embed)

    try:
        url = API_URL.format(number=number)
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                else:
                    raise Exception(f"API status {response.status}")

        if isinstance(data, dict) and data.get("error"):
            error_embed = discord.Embed(
                title="❌ Search Failed",
                description=f"Error: {data.get('error')}",
                color=0xED4245
            )
            await search_msg.edit(embed=error_embed)
            return

        if not data or (isinstance(data, list) and len(data) == 0):
            no_data_embed = discord.Embed(
                title="⚠️ No Records",
                description=f"No records for: `{number}`",
                color=0xFEE75C
            )
            await search_msg.edit(embed=no_data_embed)
            return

        await search_msg.delete()

        records = data if isinstance(data, list) else [data]
        total_records = len(records)

        summary_embed = discord.Embed(
            title="🎉 SEARCH SUCCESSFUL!",
            description=f"**Found {total_records} Record(s)**",
            color=0x57F287,
            timestamp=datetime.now(timezone.utc)
        )

        summary_embed.add_field(
            name="ℹ️ Summary",
            value=f"**Number:** `{number}`\n**Records:** {total_records}",
            inline=False
        )

        view = PremiumSearchView(ctx, records, number)
        await ctx.send(embed=summary_embed, view=view)

        for index, record in enumerate(records, 1):
            embed = discord.Embed(
                title=f"👤 RECORD {index}/{total_records}",
                color=0x5865F2,
                timestamp=datetime.now(timezone.utc)
            )

            name = clean_text(record.get('name', 'N/A'))
            fathers_name = clean_text(record.get('father_name', record.get('fathersname', 'N/A')))
            address = format_address(record.get('address', 'N/A'))
            mobile = record.get('mobile', number)

            embed.add_field(name="📱 Mobile", value=f"```{mobile}```", inline=True)
            embed.add_field(name="👤 Name", value=f"```{name}```", inline=True)

            if fathers_name != "🚫 Not Available":
                embed.add_field(name="👨‍👦 Father", value=f"```{fathers_name}```", inline=True)

            if address != "🚫 Address Not Available":
                embed.add_field(name="🏠 Address", value=f"```{address}```", inline=False)

            embed.set_footer(text=f"Record {index}/{total_records} • {DEVELOPER_INFO['developer']}")

            await ctx.send(embed=embed)
            await asyncio.sleep(0.3)

    except Exception as e:
        logger.error(f"Search error: {e}")
        error_embed = discord.Embed(
            title="❌ Error",
            description="Search failed. Try again.",
            color=0xED4245
        )
        await search_msg.edit(embed=error_embed)

@bot.event
async def on_message(message):
    """Auto-detect numbers"""
    if message.author == bot.user:
        return

    numbers = re.findall(r'\b\d{10}\b', message.content)
    if numbers:
        for number in numbers[:1]:  # Only first number
            embed = discord.Embed(
                title="🔍 Auto-Detected",
                description=f"Found: `{number}`",
                color=0x3498DB
            )
            await message.channel.send(embed=embed)

            # Trigger search
            ctx = await bot.get_context(message)
            await search(ctx, number=number)
            break

    await bot.process_commands(message)

@bot.command()
async def help(ctx):
    """Help command"""
    embed = discord.Embed(
        title="⭐ BOT HELP",
        description="Mobile Number Search Bot",
        color=0x3498DB
    )

    embed.add_field(
        name="🔍 Search",
        value="`!search 7405453929`\nAuto-detect: Type 10-digit number",
        inline=False
    )

    embed.add_field(
        name="📊 Commands",
        value="`!help` - This help\n`!ping` - Check latency\n`!stats` - Bot stats",
        inline=False
    )

    embed.add_field(
        name="🔗 Developer",
        value=f"[Discord]({DEVELOPER_INFO['discord']}) • [Instagram]({DEVELOPER_INFO['instagram']})",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Check latency"""
    latency = round(bot.latency * 1000)

    if latency < 50:
        status = "⚡ FAST"
        color = 0x57F287
    elif latency < 100:
        status = "✅ GOOD"
        color = 0x3498DB
    else:
        status = "⚠️ SLOW"
        color = 0xFEE75C

    embed = discord.Embed(
        title="🏓 Pong!",
        color=color
    )

    embed.add_field(name="📡 Latency", value=f"```{latency}ms```", inline=True)
    embed.add_field(name="🟢 Status", value=f"```{status}```", inline=True)

    await ctx.send(embed=embed)

@bot.command()
async def stats(ctx):
    """Bot statistics"""
    latency = round(bot.latency * 1000)
    uptime = get_uptime()
    servers = len(bot.guilds)
    users = sum(g.member_count for g in bot.guilds if g.member_count)

    embed = discord.Embed(
        title="📊 BOT STATS",
        color=0x5865F2,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="⚡ Performance",
        value=f"**Latency:** `{latency}ms`\n**Uptime:** `{uptime}`",
        inline=False
    )

    embed.add_field(
        name="🔍 Usage",
        value=f"**Searches:** `{search_count}`\n**Servers:** `{servers}`\n**Users:** `{users}`",
        inline=False
    )

    embed.set_footer(text=f"{get_indian_time()}")

    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    logger.error(f"Command error: {error}")

# Run bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")

    if not token:
        logger.error("❌ No DISCORD_BOT_TOKEN found!")
        exit(1)

    logger.info("🚀 Starting bot...")

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token!")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
