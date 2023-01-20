import api
import functions
import discord
import typing
import os
from discord import app_commands
from dotenv import load_dotenv
import functions

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild_obj = discord.Object(id=int(os.getenv('DISCORD_ID')))

@tree.command(name="mythics", description="Show chests based on mythics plus done", guild=guild_obj)
@discord.app_commands.choices(semaine=[
    app_commands.Choice(name="Actuelle", value="current"),
    app_commands.Choice(name="Dernière", value="last"),
    ])
async def mythics(interaction, semaine: typing.Optional[app_commands.Choice[str]], niveau: typing.Optional[int] = 0):
    semaine = 'current' if semaine == None else semaine.value
    await interaction.response.send_message('Commande lancée...')
    response = functions.mythics.Mythics.format_mythics_done(functions.mythics.Mythics.get_mythics_done(semaine), niveau)
    await interaction.edit_original_response(content=response)

@tree.command(name="lineup", description="Publish lineup for next raid", guild=guild_obj)
async def lineup(interaction, date: typing.Optional[str] = ''):
    await interaction.response.send_message(functions.lineup.Lineup.get_lineup(date))

@client.event
async def on_ready():
    await tree.sync(guild=guild_obj)
    print("Ready!")

client.run(os.getenv('DISCORD_BOT_KEY'))
        