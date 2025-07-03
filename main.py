import discord as ds
from discord.ext import commands
import tokens
from functools import wraps
from steamsales import *
from steamgamesids import *
from datetime import datetime

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

def check_admin_func(interaction: ds.Interaction):
    return interaction.user.id in [839429032343765002, 114880864772423682]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name} - {bot.user.id}")

@bot.tree.command(name="send_here", description="Envoyer les prix ici")
@check_admin
async def send_here(interaction: ds.Interaction):
    await interaction.response.defer()
    desc = f"```\n{"Jeu".ljust(34)} | {"Prix".ljust(5)} | Reduc | {"%".ljust(5)}\n"
    for name, id in SteamGamesIDs.data.items():
        price = steamapi.search(id)
        print(f"Searched for {name}")
        desc += f"{name.ljust(34)} | {str(price.current_price).ljust(5)} | {str(price.original_price).ljust(5) if price.is_reduction else "/".ljust(5)} | {str(price.reduction_percentage) if price.is_reduction else "/"}\n"
        # await asyncio.sleep(.1)
    for name, id in SteamGamesIDsSponso.data.items():
        price = steamapi.search(id)
        print(f"Searched for {name}")
        desc += f"{name.ljust(34)} | {str(price.current_price).ljust(5)} | {str(price.original_price).ljust(5) if price.is_reduction else "/".ljust(5)} | {str(price.reduction_percentage) if price.is_reduction else "/"}\n"

    desc += "```\n" + datetime.now().strftime("Mis a jour le %d/%m/%Y à %H:%M")
    await interaction.followup.send(desc)

bot.run(tokens.TOKEN)