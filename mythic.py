import requests
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)
load_dotenv()
    
def get_roster(last_msg):
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

def get_mythics_done(last_msg):
    roster = get_roster(last_msg)
    headers = { 
        "accept": "application/json", 
        }

    roster_mythics_done = {}

    for number, character in enumerate(roster):
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
        
    


@bot.command()
async def mythics_done(ctx, *arg):
    last_msg = await ctx.send('Commande lancée...')
    minimal_level = 0
    if len(arg) == 1:
        if arg[0].isdigit():
            minimal_level = int(arg[0])
    await ctx.send(format_mythics_done(get_mythics_done(last_msg), minimal_level))

bot.run(os.getenv('DISCORD_BOT_KEY'))