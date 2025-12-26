import discord
from discord.ext import commands
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask

# ======================
# LOAD ENV
# ======================
load_dotenv()

TOKEN = os.getenv("TOKEN")
PORT = int(os.getenv("PORT", 5000))

# ⚠️ Move sensitive values to .env before public release
FF_API_KEY = os.getenv("FF_API_KEY", "LFy6c48ZmjfKpWoswLka86gZSGCDoB")
FF_USER_UID = os.getenv("FF_USER_UID", "0UQuFDoZiFVfw8OXB2iSiS1GYNz2")
FF_REGION = os.getenv("FF_REGION", "bd")

if not TOKEN:
    raise ValueError("TOKEN missing in .env")

# ======================
# FLASK (OPTIONAL – FOR HOSTING)
# ======================
app = Flask(__name__)

@app.route("/")
def home():
    return "UniqueTopup Bot is running"

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

# ======================
# DISCORD BOT
# ======================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

session = None

# ======================
# FREE FIRE API
# ======================
FF_API_URL = "https://proapis.hlgamingofficial.com/main/games/freefire/account/api"

# ======================
# HELPERS
# ======================
def ts(t):
    try:
        return datetime.utcfromtimestamp(int(t)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "Not found"

# ======================
# BOT EVENTS
# ======================
@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_disconnect():
    if session:
        await session.close()

# ======================
# INFO COMMAND
# ======================
@bot.command(name="info")
async def info(ctx, uid: str):
    if not uid.isdigit():
        return await ctx.send("❌ UID must be numeric")

    if session is None:
        return await ctx.send("⚠️ Bot is starting, please try again in a moment.")

    params = {
        "sectionName": "AllData",
        "PlayerUid": uid,
        "region": FF_REGION,
        "useruid": FF_USER_UID,
        "api": FF_API_KEY
    }

    async with ctx.typing():
        async with session.get(FF_API_URL, params=params) as resp:
            if resp.status != 200:
                return await ctx.send("⚠️ Free Fire service unavailable")
            data = await resp.json()

    r = data.get("result", {})
    acc = r.get("AccountInfo", {})
    prof = r.get("AccountProfileInfo", {})
    guild = r.get("GuildInfo", {})
    pet = r.get("petInfo", {})
    credit = r.get("creditScoreInfo", {})
    social = r.get("socialinfo", {})
    leader = r.get("captainBasicInfo", {})

    text = (
        "**Player Information**\n\n"
        "**┌ ACCOUNT BASIC INFO**\n"
        f"├─ Name: {acc.get('AccountName','Not found')}\n"
        f"├─ UID: {uid}\n"
        f"├─ Level: {acc.get('AccountLevel','?')} (Exp: {acc.get('AccountEXP','?')})\n"
        f"├─ Region: 🇧🇩 Bangladesh\n"
        f"├─ Likes: {acc.get('AccountLikes','?')}\n"
        f"├─ Honor Score: {credit.get('creditScore','?')}\n"
        f"└─ Signature: {social.get('AccountSignature','None')}\n\n"

        "**┌ ACCOUNT ACTIVITY**\n"
        f"├─ Most Recent OB: {acc.get('ReleaseVersion','?')}\n"
        f"├─ Current BP Badges: {acc.get('AccountBPBadges','?')}\n"
        f"├─ BR Rank: {acc.get('BrRankPoint','?')}\n"
        f"├─ CS Rank: {acc.get('CsRankPoint','?')}\n"
        f"├─ Created At: {ts(acc.get('AccountCreateTime'))}\n"
        f"└─ Last Login: {ts(acc.get('AccountLastLogin'))}\n\n"

        "**┌ ACCOUNT OVERVIEW**\n"
        f"├─ Avatar ID: {acc.get('AccountAvatarId','Not found')}\n"
        f"├─ Banner ID: {acc.get('AccountBannerId','Not found')}\n"
        f"├─ Pin ID: {acc.get('AccountBPID','Not found')}\n"
        f"└─ Equipped Skills: {prof.get('EquippedSkills','[]')}\n\n"

        "**┌ PET DETAILS**\n"
        f"├─ Equipped?: {'Yes' if pet.get('isSelected') else 'No'}\n"
        f"├─ Pet Name: {pet.get('name','Not found')}\n"
        f"├─ Pet Exp: {pet.get('exp','Not found')}\n"
        f"└─ Pet Level: {pet.get('level','Not found')}\n\n"

        "**┌ GUILD INFO**\n"
        f"├─ Guild Name: {guild.get('GuildName','Not found')}\n"
        f"├─ Guild ID: {guild.get('GuildID','Not found')}\n"
        f"├─ Guild Level: {guild.get('GuildLevel','Not found')}\n"
        f"├─ Live Members: {guild.get('GuildMember','?')}/{guild.get('GuildCapacity','?')}\n"
        f"└─ Leader Info:\n"
        f"    ├─ Leader Name: {leader.get('nickname','Not found')}\n"
        f"    ├─ Leader UID: {leader.get('accountId','Not found')}\n"
        f"    ├─ Leader Level: {leader.get('level','?')} (Exp: {leader.get('exp','?')})\n"
        f"    ├─ Last Login: {ts(leader.get('lastLoginAt'))}\n"
        f"    ├─ Title: {leader.get('title','Not found')}\n"
        f"    ├─ BP Badges: {leader.get('badgeCnt','?')}\n"
        f"    ├─ BR Rank: {leader.get('rankingPoints','?')}\n"
        f"    └─ CS Rank: {leader.get('csRankingPoints','?')}"
        +
        "\n\n━━━━━━━━━━━━━━━━━━\n"
        "💎 **Boost Your Free Fire Balance Instantly!**\n\n"
        "✨ **Buy Instant FF Likes**\n"
        "🔗 https://uniquetopup.com/\n\n"
        "💠 **Need Diamonds? Contact Us**\n"
        "📞 +880 1716-720487\n\n"
        "🚀 Fast • Safe • Trusted by Players\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    embed = discord.Embed(description=text, color=discord.Color.gold())
    embed.set_footer(text="UniqueTopup")
    await ctx.send(embed=embed)

# ======================
# RUN BOT
# ======================
bot.run(TOKEN)
