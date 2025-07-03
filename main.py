import json
import discord as ds
from discord.ext import commands
import tokens
from functools import wraps
from steamsales import *
from steamgamesids import *
from datetime import datetime, timedelta
import asyncio

def check_admin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if check_admin_func(args[0]):
            return await func(*args, **kwargs)
        else:
            return await args[0].response.send_message("Tu n'as pas la permission pour exécuter cette commande !", ephemeral=True)
    return wrapper


bot = commands.Bot(command_prefix="!", intents=ds.Intents.all())
steamapi = SteamSales()
desc = None
with open("messages.json", "r") as f:
    messages: dict[str, str] = json.load(f)

def update_messages():
    with open("messages.json", "w") as f:
        json.dump(messages, f, indent=4)

def add_message_id(channel_id: str, message_id: str):
    if not message_id in messages:
        messages[channel_id] = message_id
        update_messages()

def remove_message_id(channel_id: str):
    if channel_id in messages:
        del messages[channel_id]
        update_messages()

def check_admin_func(interaction: ds.Interaction):
                                   # CodeurIII ID      # Synedh ID
    return interaction.user.id in [839429032343765002, 114880864772423682]

def get_datetime():
    return datetime.now().strftime("Mis a jour le %d/%m/%Y à %H:%M")

def get_games():
    result = {}
    for name, id in SteamGamesIDs.data.items():
        result[name] = steamapi.search(id).to_dict()
        print(f"Searched for {name}")
    for name, id in SteamGamesIDsSponso.data.items():
        result[name] = steamapi.search(id).to_dict()
        print(f"Searched for {name}")
    
    return result

def get_desc(result: dict[str, dict[str, str | float]]):
    desc = f"```\n{'Jeu'.ljust(34)} | {'Prix'.ljust(5)} | Reduc | %\n"
    for name, price_dict in result.items():
        price = Price.from_dict(price_dict)
        desc += f"{name.ljust(34)} | {str(price.current_price).ljust(5)} | {str(price.original_price).ljust(5) if price.is_reduction else '/'.ljust(5)} | {str(price.reduction_percentage) if price.is_reduction else '/'}\n"
    desc += "```\n" + get_datetime()
    return desc

def update_desc():
    global desc
    desc = get_desc(get_games())

async def update_discord_messages():
    update_desc()
    for channel_id, message_id in messages.items():
        channel = await bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.edit(content=desc)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await update_discord_messages()
    bot.loop.create_task(hourly_update_desc())
    print(f"Logged in as {bot.user.name} - {bot.user.id}")

@bot.event
async def on_message_delete(message: ds.Message):
    if message.channel.id in messages:
        remove_message_id(message.channel.id)
        print(f"Message supprimé retiré de la liste : {message.id}")

@bot.tree.command(name="send_here", description="Envoyer les prix ici")
@check_admin
async def send_here(interaction: ds.Interaction):
    await interaction.response.send_message(desc)
    msg = await interaction.original_response()
    add_message_id(interaction.channel.id, msg.id)


async def hourly_update_desc():
    while True:
        now = datetime.now()
        next_hour = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        wait_seconds = (next_hour - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        await update_discord_messages()
        print(f"Description mise à jour à {datetime.now().strftime('%H:%M')}")


bot.run(tokens.TOKEN)