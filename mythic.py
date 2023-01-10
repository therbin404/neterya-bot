import requests
import os
import discord
from dotenv import load_dotenv

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

def get_mythics_done():
    roster = get_roster()
    headers = { 
        "accept": "application/json", 
        }

    roster_mythics_done = {}

    for character in roster:
        name = character['name']
        realm = character['realm'].replace('Marecage de Zangar', 'Marécage de Zangar').replace(' ', '-')
        result = requests.get('https://raider.io/api/v1/characters/profile?region=eu&realm=%s&name=%s&fields=mythic_plus_weekly_highest_level_runs' % (realm, name), headers=headers)
        mythics_done = result.json()

        mythic_datas = []

        # we only want weekly mythics done
        for mythic_done in mythics_done['mythic_plus_weekly_highest_level_runs']:
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
        
    

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author.id == client.user:
        return

    if message.content.startswith('!mythics_done'):
        minimal_level = 0
        if len(message.content.split()) == 2:
            if message.content.split()[1].isdigit():
                minimal_level = int(message.content.split()[1])
        await message.channel.send(format_mythics_done(get_mythics_done(), minimal_level))

client.run(os.getenv('DISCORD_KEY'))