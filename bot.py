from ast import arg
import os
import discord
from discord.ext import commands
import json

VALUES_FILE = 'values.json'

def load_values():
    with open(VALUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def norm(s: str) -> str:
    return s.strip().lower()

# intents (needed so the bot can read messages)
intents = discord.Intents.default()
intents.message_content = True

# set the prefix
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

@bot.command()
async def t(ctx, *, arg: str):
    ###
    # Example:
    # !t dragon, golden sword for phoenix
    ###
    values = load_values()

    if " for " not in arg.lower():
        await ctx.send("Invalid format. Use `!t item1, item2 for item3, item4`")
        return
    
    left, right = arg.split(" for ", 1)  # split once
    left = left.strip()
    right = right.strip()

    if not left or not right:
        await ctx.send("Invalid format. Use `!t item1, item2 for item3, item4`")
        return

    
    my_items = [norm(x) for x in left.split(",") if x.strip()]
    their_items = [norm(x) for x in right.split(",") if x.strip()]

    def total(items):
        t = 0
        missing = []
        for it in items:
            if it in values:
                t += int(values[it])
            else:
                missing.append(it)
        return t, missing
    
    my_total, my_missing = total(my_items)
    their_total, their_missing = total(their_items)

    diff = their_total - my_total
    if diff > 0:
        verdict = "✅ Win"
    elif diff == 0:
        verdict = "⚖️ Fair"
    else:
        verdict = "❌ Lose"
    
    msg = (
        f"**Your side:** {my_total}\n"
        f"**Their side:** {their_total}\n"
        f"**Difference:** {diff}\n"
        f"**Result:** {verdict}"
    )

    missing = sorted(set(my_missing + their_missing))
    if missing:
        msg += "\n\n**Missing values for:** " + ", ".join(missing)

    await ctx.send(msg)

# read the token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN environment variable not set")

bot.run(TOKEN)