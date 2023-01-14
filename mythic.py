import requests
import os
import discord
import typing
import re
import datetime
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild_obj = discord.Object(id=int(os.getenv('DISCORD_ID')))
audit_headers = { 
    "accept": "application/json", 
    "Authorization": os.getenv('WOW_AUDIT_BEARER')
    }
bnet_headers = { 
    "accept": "application/json"
    }

    
def get_roster(for_lineup = False):
    result = requests.get("https://wowaudit.com/v1/characters", headers=audit_headers)
    roster = result.json()

    return roster



###### MYTHIC PLUS ########

def get_mythics_done(week):
    roster = get_roster()

    roster_mythics_done = {}

    week_url = 'mythic_plus_previous_weekly_highest_level_runs' if week == 'last' else 'mythic_plus_weekly_highest_level_runs'

    for number, character in enumerate(roster):
        name = character['name']
        realm = character['realm'].replace('Marecage de Zangar', 'Marécage de Zangar').replace(' ', '-')
        result = requests.get('https://raider.io/api/v1/characters/profile?region=eu&realm=%s&name=%s&fields=%s' % (realm, name, week_url), headers=bnet_headers)
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

###############################




###### RAID ########

def find_backups(text, roster):
    backup_string = re.findall(r"^Backups:(.*)", text)
    backups = []
    discord_string = text
    if backup_string:
        discord_string += 'Backups : \n'
        backups = backup_string[0].strip().split(',')
        for index, backup in enumerate(backups):
            if index > 0:
                discord_string += '\n'
            note = list(filter(lambda c: c['name'] == backup.strip(), roster))[0]['note']
            discord_string += '<@%s>' % note
        discord_string = re.sub(r"^Backups:(.*)", '', discord_string)

    return discord_string


def get_lineup(date):
    roster = get_roster()
    include_past = 'false'
    if date:
        include_past = 'true'

    result = requests.get('https://wowaudit.com/v1/raids?include_past=%s' % include_past, headers=audit_headers).json()

    choosen_ones = []

    string_to_return = ''

    if result:
        if len(result['raids']) > 0:
            raid_id = str(result['raids'][0]['id'])
            if date:
                raid = list(filter(lambda r: r['date'] == date, result['raids']))
                if raid:
                    raid_id = str(raid[0]['id'])

            next_raid = requests.get('https://wowaudit.com/v1/raids/%s' % raid_id, headers=audit_headers).json()

            next_raid_date = datetime.datetime.strptime(next_raid['date'], '%Y-%m-%d')
            next_raid_date = next_raid_date.strftime('%d/%m')
            string_to_return += '\u200b \n** Raid du %s **\n\n' % next_raid_date

            encounters = filter(lambda a: a['enabled'], next_raid['encounters'])
            characters_selected = {}
            encounters_name = []
            general_note = ''
                
            # set a list of char_id, roles and wich encounters they'll do
            # characters_selected[id] = {
            #    'role': role,
            #    'encounters': encouters_name
            #}
            if len(list(encounters)) == 0:
                for character in list(filter(lambda c: c['selected'], next_raid['signups'])):
                    if character['character']['id'] not in characters_selected:
                        characters_selected[character['character']['id']] = {'role': character['character']['role'], 'encounters': []}
                html_free = re.sub(r"<[^<]+?>", "", next_raid['notes'])
                html_free = find_backups(html_free, roster)
                general_note += '\n\n%s' % html_free
            else:
                for encounter in encounters:
                    if encounter['notes']:
                        html_free = re.sub(r"<[^<]+?>", "", encounter['notes'])
                        html_free = find_backups(html_free, roster)
                        general_note += '\n\n%s' % html_free
                    encounters_name.append(encounter['name'])
                    encounter_roster = encounter['selections']
                    for character in encounter_roster:
                        if character['character_id'] not in characters_selected:
                            characters_selected[character['character_id']] = {'role': character['role'], 'encounters': []}
                        if not (encounter['name'] in characters_selected[character['character_id']]) and character['selected']:
                            characters_selected[character['character_id']]['encounters'].append(encounter['name'])

            # show lineup, with comment if they participate on less bosses than all encounters
            string_tank = ''
            string_melee = ''
            string_ranged = ''
            string_heal = ''
            note_encounters = ''
            for character in characters_selected:
                current_char = characters_selected[character]
                note = list(filter(lambda c: c['id'] == character, roster))[0]['note']
                if len(current_char['encounters']) > 0:
                    if len(current_char['encounters']) < len(encounters_name):
                        note_encounters = 'seulement pour '
                        for index, encounter in enumerate(current_char['encounters']):
                            if index > 0:
                                note_encounters += ', '
                            note_encounters += encounter

                if current_char['role'] == 'Tank':
                    string_tank += '\n<@%s> %s' % (note, note_encounters)
                elif current_char['role'] == 'Melee':
                    string_melee += '\n<@%s> %s' % (note, note_encounters)
                elif current_char['role'] == 'Ranged':
                    string_ranged += '\n<@%s> %s' % (note, note_encounters)
                elif current_char['role'] == 'Heal':
                    string_heal += '\n<@%s> %s' % (note, note_encounters)

            if len(string_tank) > 0:
                string_to_return += '**Tanks**%s\n\n' % string_tank 
            if len(string_heal) > 0:
                string_to_return += '**Heals**%s\n\n' % string_heal
            if len(string_melee) > 0:
                string_to_return += '**Melee**%s\n\n' % string_melee
            if len(string_ranged) > 0:
                string_to_return += '**Ranged**%s\n\n' % string_ranged

            string_to_return += general_note
        
    return string_to_return
                



###############################





###### COMMANDS ########

@tree.command(name="mythics", description="Show chests based on mythics plus done", guild=guild_obj)
@app_commands.choices(semaine=[
    app_commands.Choice(name="Actuelle", value="current"),
    app_commands.Choice(name="Dernière", value="last"),
    ])
async def mythics(interaction, semaine: typing.Optional[app_commands.Choice[str]], niveau: typing.Optional[int] = 0):
    semaine = 'current' if semaine == None else semaine.value
    await interaction.response.send_message('Commande lancée...')
    response = format_mythics_done(get_mythics_done(semaine), niveau)
    await interaction.edit_original_response(content=response)

@tree.command(name="lineup", description="Publish lineup for next raid", guild=guild_obj)
async def lineup(interaction, date: typing.Optional[str] = ''):
    await interaction.response.send_message(get_lineup(date))
    
    #await interaction.response.send_message('<@%s>' % str(222844821264531456))

###############################

@client.event
async def on_ready():
    await tree.sync(guild=guild_obj)
    print("Ready!")

client.run(os.getenv('DISCORD_BOT_KEY'))