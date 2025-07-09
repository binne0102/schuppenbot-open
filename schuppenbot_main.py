import discord
from discord.ext import commands
import datetime
import traceback
import atexit

# ==== KONFIGURATION ====
TOKEN = 'DEIN_BOT_TOKEN_HIER'  # <- Hier deinen Bot-Token einfügen
LOG_CHANNEL_ID = 123456789012345678  # <- Hier die ID deines Log-Channels einfügen

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# ==== HILFSFUNKTION: Eingebettete Logs ====
def create_embed(title, description, color, emoji=None):
    embed = discord.Embed(title=f"{emoji + ' ' if emoji else ''}{title}",
                          description=description,
                          color=color)
    embed.timestamp = datetime.datetime.utcnow()
    return embed

# ==== EVENT: Bot startklar ====
@bot.event
async def on_ready():
    print(f'Bot ist online als {bot.user.name}')
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = create_embed("Bot Online", f"✅ Bot ist jetzt online – {datetime.datetime.now().strftime('%H:%M:%S')}", 0x2ecc71, "🟢")
        await channel.send(embed=embed)

# ==== BOT OFFLINE MESSAGE ====
def on_exit():
    try:
        loop = bot.loop
        if loop.is_closed():
            return
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            coro = channel.send(embed=create_embed("Bot Offline", f"⛔ Bot wurde gestoppt oder ist offline gegangen – {datetime.datetime.now().strftime('%H:%M:%S')}", 0xe74c3c, "🔻"))
            future = discord.utils.ensure_future(coro, loop=loop)
            loop.run_until_complete(future)
    except Exception as e:
        print("Fehler beim Senden der Offline-Nachricht:")
        traceback.print_exc()

atexit.register(on_exit)

# ==== EVENT: Voice Logger ====
@bot.event
async def on_voice_state_update(member, before, after):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    if before.channel is None and after.channel is not None:
        embed = create_embed("Voice Join", f"**{member.display_name}** ist **'{after.channel.name}'** beigetreten.", 0x3498db, "🟩")
        await channel.send(embed=embed)
    elif before.channel is not None and after.channel is None:
        embed = create_embed("Voice Leave", f"**{member.display_name}** hat **'{before.channel.name}'** verlassen.", 0xe74c3c, "🟥")
        await channel.send(embed=embed)
    elif before.channel != after.channel:
        embed = create_embed("Voice Wechsel", f"**{member.display_name}** wechselte von **'{before.channel.name}'** zu **'{after.channel.name}'**.", 0xf1c40f, "🔁")
        await channel.send(embed=embed)

# ==== EVENT: Rollen Logger ====
@bot.event
async def on_member_update(before, after):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return

    added_roles = [role for role in after.roles if role not in before.roles]
    removed_roles = [role for role in before.roles if role not in after.roles]

    for role in added_roles:
        embed = create_embed("Rolle Hinzugefügt", f"**{after.display_name}** hat die Rolle **{role.name}** erhalten.", 0x2ecc71, "✅")
        await channel.send(embed=embed)

    for role in removed_roles:
        embed = create_embed("Rolle Entfernt", f"**{after.display_name}** wurde die Rolle **{role.name}** entfernt.", 0xe74c3c, "❌")
        await channel.send(embed=embed)

# ==== EVENT: Join / Leave Logger ====
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = create_embed("Neues Mitglied", f"**{member.display_name}** ist dem Server beigetreten.", 0x1abc9c, "➕")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = create_embed("Mitglied Verlassen", f"**{member.display_name}** hat den Server verlassen.", 0xe67e22, "➖")
        await channel.send(embed=embed)

# ==== EVENT: Nachrichten-Logger ====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel:
        embed = create_embed("Nachricht", f"**{message.author.display_name}** in **#{message.channel}**:
{message.content}", 0x95a5a6, "💬")
        await channel.send(embed=embed)

# ==== START ====
try:
    bot.run(TOKEN)
except Exception as e:
    print("Fehler beim Starten des Bots:")
    traceback.print_exc()
    on_exit()
