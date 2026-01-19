import os
import discord
from discord.ext import commands
import json

VALUES_FILE = 'values.json'

#function to store values from json
def load_values():
    with open(VALUES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# function to nromalize user input
def norm(s: str) -> str:
    return s.strip().lower()

# function to store items and quantity from user input
def parse_item_token(token: str) -> tuple[str, int]:
    token = token.strip()
    if not token:
        return ("", 0)
    
    parts = token.split()
    if parts[0].isdigit() and len(parts) >= 2:
        qty = int(parts[0])
        name = " ".join(parts[1:])
        return (norm(name), qty)
    
    return (norm(token), 1)

# function to format item and quantity for embed
def format_item_lines(items):
    lines = []
    for name, qty in items:
        if qty == 1:
            lines.append(f"• {name.title()}")
        else:
            lines.append(f"• {qty} {name.title()}")
    return "\n".join(lines) if lines else "—"

# intents (needed so the bot can read messages)
intents = discord.Intents.default()
intents.message_content = True

# set the prefix
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# ping command to test if the bot works
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

# main trade command
@bot.command(name="trade", aliases=['t'])
async def trade(ctx, *, arg: str = None):
    
    # make sure there is input
    if not arg:
        await ctx.send("Invalid format. Use `!trade <item1>, <item2> for <item3>, <item4>`")
        return
      
    ###
    # Example:
    # !trade dragon, golden sword for phoenix
    ###
    values = load_values()

    if " for " not in arg.lower():
        await ctx.send("Invalid format. Use `!trade <item1>, <item2> for <item3>, <item4>`")
        return
    
    left, right = arg.split(" for ", 1)  # split once
    left = left.strip()
    right = right.strip()

    if not left or not right:
        await ctx.send("Invalid format. Use `!trade <item1>, <item2> for <item3>, <item4>`")
        return

    
    my_items = [parse_item_token(x) for x in left.split(",") if x.strip()]
    their_items = [parse_item_token(x) for x in right.split(",") if x.strip()]

    # calculate totals
    def total(items):
        t = 0
        missing = []
        for name, qty in items:
            if name in values:
                t += int(values[name]) * qty
            else:
                missing.append(name)
        return t, missing
    
    my_total, my_missing = total(my_items)
    their_total, their_missing = total(their_items)

    # calculate difference , percentage, color, result, and sign
    diff = their_total - my_total
    percent_diff = (diff / my_total * 100) if my_total > 0 else 0

    if diff > 0:
        color = discord.Color.green()
        result_line = "You are winning!"
    elif diff == 0:
        color = discord.Color.gold()
        result_line = "Trade is fair."
    else:
        color = discord.Color.red()
        result_line = "You are losing!"

    sign = "+" if percent_diff > 0 else ""

    # make the embed
    embed = discord.Embed(
        title="Trade Assessment",
        color=color
    )

    # add fields for respective items and totals
    embed.add_field(
        name="🦥 Your Items",
        value=format_item_lines(my_items),
        inline=True
    )

    embed.add_field(
        name="🎁 Their Trade",
        value=format_item_lines(their_items),
        inline=True
    )

    # add spacer so formatting looks good
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="Your Total", value=f"{my_total}", inline=True)
    embed.add_field(name="Their Total", value=f"{their_total}", inline=True)

    # add field for differenfce
    embed.add_field(
        name="⚖️ Difference",
        value=f"{diff} ({sign}{percent_diff:.2f}%)",
        inline=False
    )

    # add field for missing values
    missing = sorted(set(my_missing + their_missing))
    if missing:
        embed.add_field(
            name="⚠️ Missing Values",
            value="\n".join([f"• {item.title()}" for item in missing]),
            inline=False
        )
    
    # add field for result
    embed.add_field(
        name="Result",
        value=result_line,
        inline=False
    )

    #send msg
    await ctx.send(embed=embed)

# near command
@bot.command(name="near", aliases=['n'])
async def near(ctx, *, arg:str = None):
    
    # make sure there is input
    if not arg:
        await ctx.send("Invalid format. Use `!near <item>, <range>`")
        return
    
    # make the list of values sorted by value
    values = load_values()
    order = sorted(
        ((name, value) for name, value in values.items() if isinstance(value, int)),
        key=lambda x: x[1]
    )
    
    # parse input for item and range
    parts = arg.split(",")
    if len(parts) > 2:
        await ctx.send("Invalid format. Use `!near <item>, <range>`")
        return
    
    item = norm(parts[0])
    range_str = norm(parts[1]) if len(parts) > 1 else "3"
    if not range_str.isdigit():
        await ctx.send("Range must be a number.")
        return
    range_of_items = int(range_str)
    

    # validate item
    if item not in values:
        await ctx.send(
        f"Missing value for: `{item}`\n"
        "Usage: `!near <item>, <range>`"
        )
        return
    
    # index of the item
    idx = next(i for i, (name, _) in enumerate(order) if name == item)

    # make list of items near the target item
    line = []
    for offset in range(-range_of_items, range_of_items + 1):
        target = idx + offset
        if 0 <= target < len(order):
            name, value = order[target]
            if offset == 0:
                prefix = "➡️ "
            else:
                prefix = "• "
            line.append(f"{prefix}{name.title()} - {value}")

    # make embed
    embed = discord.Embed(
        title = f"Items near '{item.title()}'",
        color = discord.Color.from_rgb(135, 206, 235)

    )

    embed.add_field(
        name="",
        value="\n\n".join(line),
        inline=False
    )

    await ctx.send(embed=embed)



# read the token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN environment variable not set")

bot.run(TOKEN)