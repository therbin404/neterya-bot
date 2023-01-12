import requests
import os
import discord
import typing
from discord import app_commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

load_dotenv()
    
def get_roster():
    headers = { 
        "accept": "application/json", 
        "Authorization": os.getenv('WOW_AUDIT_BEARER')
        }
    result = requests.get("https://wowaudit.com/v1/characters", headers=headers)
    roster = result.json()

    # we only want name and realm
    keys_to_remove = ['id', 'class', 'role', 'rank', 'status', 'note', 'blizzard_id', 'tracking_since']
    for character in roster:
        for key in keys_to_remove:
            character.pop(key)
    return roster

def get_mythics_done(week):
    roster = get_roster()
    headers = { 
        "accept": "application/json", 
        }

    roster_mythics_done = {}

    week_url = 'mythic_plus_previous_weekly_highest_level_runs' if week == 'last' else 'mythic_plus_weekly_highest_level_runs'

    for number, character in enumerate(roster):
        name = character['name']
        realm = character['realm'].replace('Marecage de Zangar', 'Marécage de Zangar').replace(' ', '-')
        result = requests.get('https://raider.io/api/v1/characters/profile?region=eu&realm=%s&name=%s&fields=%s' % (realm, name, week_url), headers=headers)
        mythics_done = result.json()

        mythic_datas = []

        # we only want weekly mythics done
        for mythic_done in mythics_done[week_url]:
            mythic_datas.append(mythic_done['mythic_level'])

        roster_mythics_done[character['name']] = mythic_datas

    return roster_mythics_done

def format_mythics_done(roster_mythics_done, min_lvl):
    # we set this block as diff code because we want to color it red, gray, or green
    string_to_return = '**\>= ' + str(min_lvl) + '**\n```diff'
    for character, mythics_done in roster_mythics_done.items():
        keys_done = len(mythics_done)
        levels_string = ''
        # put a minus on line start to color it red if the player have less than 2 chests
        mark = '-'
        if len(mythics_done) > 0:
            levels_string += 'Bonus 1: ' + str(mythics_done[0])
            if len(mythics_done) >= 4:
                levels_string += ', Bonus 4: ' + str(mythics_done[3])
                mark = ''
                if mythics_done[3] >= min_lvl:
                    mark = '+'

        string_to_return += '\n%s (%d) %s: %s' % (mark, keys_done, character, levels_string)
    string_to_return += '\n```'
    return string_to_return

@tree.command(name="mythics", description="Show chests based on mythics plus done", guild=os.getenv('DISCORD_ID'))
@app_commands.choices(semaine=[
    app_commands.Choice(name="Actuelle", value="current"),
    app_commands.Choice(name="Dernière", value="last"),
    ])
async def mythics(interaction, semaine: typing.Optional[app_commands.Choice[str]], niveau: typing.Optional[int] = 0):
    semaine = 'current' if semaine == None else semaine.value
    await interaction.response.send_message('Commande lancée...')
    response = format_mythics_done(get_mythics_done(semaine), niveau)
    await interaction.edit_original_response(content=response)

@client.event
async def on_ready():
    await tree.sync(guild=os.getenv('DISCORD_ID'))
    print("Ready!")

client.run(os.getenv('DISCORD_BOT_KEY'))