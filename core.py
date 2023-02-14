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

admin_id = 222844821264531456

@tree.command(name="mythics", description="Show chests based on mythics plus done", guild=guild_obj)
@discord.app_commands.choices(semaine=[
    app_commands.Choice(name="Actuelle", value="current"),
    app_commands.Choice(name="Dernière", value="last"),
    ])
async def mythics(interaction, semaine: typing.Optional[app_commands.Choice[str]], niveau: typing.Optional[int] = 0):
    await interaction.response.defer()
    admin = await client.fetch_user(admin_id)
    await admin.send('%s a utilisé la commande /%s (avec les arguments: %s - %s)' % (interaction.user, interaction.command.name, semaine, niveau))

    Mythics = functions.mythics.Mythics()
    semaine = 'current' if semaine == None else semaine.value
    response = Mythics.format_mythics_done(Mythics.get_mythics_done(semaine), niveau)
    await interaction.edit_original_response(content=response)

@tree.command(name="lineup", description="Publish lineup for next raid", guild=guild_obj)
async def lineup(interaction, date: typing.Optional[str] = ''):
    # defer is here to quick respond to discord, to avoid timeout of application
    await interaction.response.defer()

    admin = await client.fetch_user(admin_id)
    await admin.send('%s a utilisé la commande /%s (avec les arguments: %s)' %(interaction.user, interaction.command.name, date))

    Lineup = functions.lineup.Lineup()
    # return [(bool), errors or string]
    # first argument if there's any errors
    # second is errors, or expected response if there's no errors
    response = Lineup.get_lineup(date)
    
    if response[0]:
        await interaction.delete_original_response()
        await interaction.user.send(content=response[1])
    elif not response[0]:
        await interaction.edit_original_response(content=response[1])

@client.event
async def on_ready():
    await tree.sync(guild=guild_obj)
    print("Ready!")

client.run(os.getenv('DISCORD_BOT_KEY'))
        