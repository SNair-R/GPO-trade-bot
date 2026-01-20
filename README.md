# GPO Trade Bot

A Discord bot for assessing Global Piece Online (GPO) trades using custom item values  
based on **Watashi Ruby’s values**.

## Features
- Compare trades with win / fair / lose verdicts
- Supports item quantities (e.g. `2 mera`)
- Shows percentage difference
- Find items near a target item's value

## Commands

### !trade / !t
Compare two trades.

**Format**
!trade item1, item2 for item3, item4

**Examples**
!trade mera, 2 hie for magu
!t 2 suna for pika

### !near / !n
Show items near the value of a target item.

**Format**
!near item, range

**Examples**
!near magu
!near pika, 5

## Setup
1. Install Python 3.12+
2. Install dependencies:
   pip install discord.py
3. Create a values.json file with item values
4. Set DISCORD_BOT_TOKEN as an environment variable
5. Run:
   python bot.py

## Notes
- Item names are case-insensitive
- Values are based on the current values.json list
- 
## Values Source
Item values used by this bot are based on **Watashi Ruby’s GPO values**.
