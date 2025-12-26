import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime

# ======================
# ENV (Render Dashboard)
# ======================
TOKEN = os.environ.get("TOKEN")
FF_API_KEY = os.environ.get("FF_API_KEY")
FF_USER_UID = os.environ.get("FF_USER_UID")
FF_REGION = os.environ.get("FF_REGION", "bd")

if not TOKEN:
    raise RuntimeError("TOKEN not set")

# ======================
# BOT SETUP (MINIMAL)
# ======================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

session = None

FF_API_URL = "https://proapis.hlgamingofficial.com/main/games/freefire/account/api"

# ======================
# HELPERS
# ======================
def ts(v):
    try:
        return datetime.utcfromtimestamp(int(v)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Not found"

# ======================
# EVENTS
# ======================
@bot.event
async def on_ready():
    global session
    if session is None:
        session = aiohttp.ClientSession()
    print(f"✅ Logged in as {bot.user}")

# ======================
# COMMAND (SAFE)
# ======================
@bot.command(name="info")
@commands.cooldown(1, 10, commands.BucketType.user)
async def info(ctx, uid: str):

    if not uid.isdigit():
        return await ctx.send("❌ UID must be numeric")

    if session is None:
        return await ctx.send("⚠️ Bot is starting, try again")

    params = {
        "sectionName": "AllData",
        "PlayerUid": uid,
        "region": FF_REGION,
        "useruid": FF_USER_UID,
        "api": FF_API_KEY
    }

    async with session.get(FF_API_URL, params=params) as resp:
        if resp.status != 200:
            return await ctx.send("⚠️ Free Fire service unavailable")

        data = await resp.json()

    r = data.get("result", {})
    acc = r.get("AccountInfo", {})
    guild = r.get("GuildInfo", {})
    credit = r.get("creditScoreInfo", {})
    social = r.get("socialinfo", {})
    leader = r.get("captainBasicInfo", {})

    text = (
        "**Player Information**\n\n"
        "**┌ ACCOUNT BASIC INFO**\n"
        f"├─ Name: {acc.get('AccountName','N/A')}\n"
        f"├─ UID: {uid}\n"
        f"├─ Level: {acc.get('AccountLevel','?')}\n"
        f"├─ Region: 🇧🇩 Bangladesh\n"
        f"├─ Likes: {acc.get('AccountLikes','?')}\n"
        f"├─ Honor Score: {credit.get('creditScore','?')}\n"
        f"└─ Signature: {social.get('AccountSignature','None')}\n\n"

        "**┌ GUILD INFO**\n"
        f"├─ Guild Name: {guild.get('GuildName','None')}\n"
        f"└─ Members: {guild.get('GuildMember','?')}/{guild.get('GuildCapacity','?')}\n\n"

        "**┌ LEADER INFO**\n"
        f"├─ Name: {leader.get('nickname','N/A')}\n"
        f"├─ UID: {leader.get('accountId','N/A')}\n"
        f"└─ Level: {leader.get('level','?')}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "💎 **Buy Instant FF Likes**\n"
        "🔗 https://uniquetopup.com/\n"
        "📞 +880 1716-720487\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    embed = discord.Embed(
        description=text,
        color=discord.Color.gold()
    )
    embed.set_footer(text="UniqueTopup")

    await ctx.send(embed=embed)

# ======================
# RUN (SAFE)
# ======================
bot.run(TOKEN)
