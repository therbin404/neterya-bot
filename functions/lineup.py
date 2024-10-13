import api
import discord
import re
from datetime import datetime
from datetime import timedelta
from itertools import groupby

class Lineup:

    mapped_char_discord = []
    roster = []

    def __init__(self, date):
        self.date = date
        self.wowaudit = api.wowaudit.WowAudit()
        self.roster = self.wowaudit.get_roster()
        self.mapped_char_discord = self.map_char_discord()
        self.lineup = self.get_lineup()

    def get_next_raid(self):
        """Get the next raid based on date"""
        raids = self.wowaudit.get_raids()

        now = datetime.now()
        # the next raid date is tonight if the command is launch before 18h
        next_raid_date = now if now.hour < 18 else now + timedelta(days=1)
        date = self.date if self.date else next_raid_date.strftime('%Y-%m-%d')

        next_raid = list(filter(lambda raid: raid['date'] == date, raids['raids']))
        next_raid_id = next_raid[0]['id'] if next_raid else 0
        if next_raid_id:
            result = self.wowaudit.get_raid(next_raid_id)
        else:
            result = False

        return result


    def get_selected_players(self, selections, all=False):
        """Returns a dict that contains all discord ids selected grouped by role
        
        e.g: {'Ulgrax': {'Ranged': [39057542431234]}, 'The Bloodbound Horror': {'Ranged': [390575423443, 51919515234234], 'Melee': [51203698123213]}}"""
        encounter_selections = {}
        # we sort the dict by role, as groupby only group consecutive items together
        sorted_selections = sorted(selections, key=lambda selection: selection['role'])

        roles_grouped = groupby(sorted_selections, lambda x: x['role'])
        
        for role, players in roles_grouped:
            encounter_selections[role] = [player.get('character').get('id') for player in players if player.get('selected')] if all else [player.get('character_id') for player in players if player.get('selected')]

            for index, character_id in enumerate(encounter_selections[role]):
                encounter_selections[role][index] = self.find_discord_id(character_id)

        return encounter_selections

    def find_discord_ids_by_name(self, names):
        """Find discord id with names as a list"""
        discord_ids = []
        for name in names:
            discord_ids.append(self.find_discord_id(name=name))
        return discord_ids

    def find_discord_id(self, character_id=False, name=False):
        """Find the discord id based on character id or name"""
        if name:
            # TODO : Add exception if name not found
            character_id = [item.get('id') for item in self.roster if item.get('name') == name]
            character_id = character_id[0] if character_id else False

        return ''.join([item.get(character_id) for item in self.mapped_char_discord if item.get(character_id)])


    def map_char_discord(self):
        """Init an array of dict that map discord id and character id"""
        return [{char.get('id'): char.get('note')} for char in self.roster]


    def get_lineup(self):
        next_raid = self.get_next_raid()

        if next_raid:

            # now we gonna handle the selections of each encounters (or all encounters if none is enabled)
            all_selected = {}
            activated_encounters = [encounter for encounter in next_raid['encounters'] if encounter['enabled']]
            for activated_encounter in activated_encounters:
                selections = activated_encounter.get('selections')
                all_selected[activated_encounter.get('name')] = {
                        'lineup': self.get_selected_players(selections),
                        'note': activated_encounter['notes']
                    }

            if not activated_encounters:
                all_selected['All'] = {
                    'lineup': self.get_selected_players(next_raid['signups'], all=True),
                    'note': next_raid['notes']
                    }

            for encounter, selection in all_selected.items():
                selection = self.find_backups(selection)
                
            result = self.format_lineup(all_selected)
            return result

    def format_lineup(self, all_selected):
        res = discord.Embed(
            title=f"Lineup du {self.date}",
            color=discord.Colour.blurple(),
        )

        string_total = ""
        for encounter_name, encounter in all_selected.items():
            # string_roles = ""
            # for role, players in encounter['lineup'].items():
            #     string_roles += f"\n> {role} :"
            #     for player in players:
            #         string_roles += f"\n> <@{player}>"
            # string_total += f"\n{string_roles}\n\n{encounter['note']}"

            # res.add_field(name=encounter_name, value=string_total, inline=True)
            for role, players in encounter['lineup'].items():
                string_players = ""
                for player in players:
                    string_players += f"\n> <@{player}>"
                if role == "Tank":
                    role = f"🛡️  {role}"
                if role == "Heal":
                    role = f"🩹  {role}"
                if role == "Melee":
                    role = f"⚔️  {role}"
                if role == "Ranged":
                    role = f"🏹  {role}"
                if role == "Backups":
                    role = f"🔄  {role}"
                res.add_field(name=role, value=string_players, inline=True)

            res.add_field(name="ℹ️  Note", value=encounter['note'], inline=True)
        return res


    def format_notes(self, notes):
        html_free_notes = re.sub(r"<[^<]+?>", "", notes)
        return html_free_notes

    def find_backups(self, selection):
        note = self.format_notes(selection['note'])
        backup_string = re.search(r"Backups\s*:\s*(.+)", note)
        if backup_string:
            backup_players = backup_string.group(1).split(", ")
        selection['lineup']['Backups'] = self.find_discord_ids_by_name(names=backup_players)
        # now we h ave backups registered, remove the bakcups part of the note
        selection['note'] = re.sub(r"Backups\s*:\s*(.+)", "", note)
        return selection



    def find_backups_bobby(self, text, roster):
        missing_backup_note = 0
        backup_string = re.findall(r"^Backups:(.*)", text)
        backups = []
        discord_string = text
        if backup_string:
            discord_string += 'Backups : \n'
            backups = backup_string[0].strip().split(',')
            for index, backup in enumerate(backups):
                if index > 0:
                    discord_string += '\n'
                print(backup.strip())
                note = list(filter(lambda c: c['name'] == backup.strip().replace('&nbsp;', ''), roster))[0]['note']
                if not note:
                    missing_backup_note += 1
                discord_string += '<@%s>' % note
            discord_string = re.sub(r"^Backups:(.*)", '', discord_string)

        return missing_backup_note, discord_string

    def get_lineup_bobby(self, date = False):
        errors = []

        wowaudit = api.wowaudit.WowAudit()
        roster = wowaudit.get_roster()

        include_past = 'false'
        if date:
            include_past = 'true'

        result = wowaudit.get_raids(include_past)

        choosen_ones = []

        string_to_return = ''

        if result:
            if len(result['raids']) > 0:
                # we setup the missing characters notes (discord ids), to return it later in the errors array
                missing_notes = 0

                raid_id = str(result['raids'][0]['id'])
                if date:
                    raid = list(filter(lambda r: r['date'] == date, result['raids']))
                    if raid:
                        raid_id = str(raid[0]['id'])

                next_raid = wowaudit.get_raid(raid_id)

                next_raid_datetime = datetime.datetime.strptime(next_raid['date'], '%Y-%m-%d')
                next_raid_date = next_raid_datetime.strftime('%d/%m')
                # we need to compare raid date to yesterday, because the raid date is always set a 00:00. 
                # in the worst case, datetime.now() will be same day, 23:59:59
                # and will be greater than raid date
                if next_raid_datetime < (datetime.datetime.now() + datetime.timedelta(days=-1)):
                    errors.append('La date du prochain raid %s est dans le passé, Marty !' % next_raid_datetime.strftime('%d/%m/%Y'))

                string_to_return += '\u200b \n** Raid du %s **\n\n' % next_raid_date

                encounters = list(filter(lambda a: a['enabled'], next_raid['encounters']))
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
                            characters_selected[character['character']['id']] = {'role': character['character']['role'], 'encounters': ['all']}
                        print(characters_selected)
                    html_free = re.sub(r"<[^<]+?>", "", next_raid['notes'])
                    # returns [number_of_missing_notes, backups_string]
                    html_free = self.find_backups(html_free, roster)
                    missing_notes += html_free[0]
                    general_note += '\n\n%s' % html_free[1]
                else:
                    for encounter in encounters:
                        if encounter['notes']:
                            html_free = re.sub(r"<[^<]+?>", "", encounter['notes'])
                            # returns [number_of_missing_notes, backups_string]
                            html_free = self.find_backups(html_free, roster)
                            missing_notes += html_free[0]
                            general_note += '\n\n%s' % html_free[1]
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
                    if not note:
                        missing_notes += 1
                        continue
                        
                    if len(current_char['encounters']) > 0:
                        if len(current_char['encounters']) < len(encounters_name):
                            note_encounters = 'seulement pour '
                            for index, encounter in enumerate(current_char['encounters']):
                                if index > 0:
                                    note_encounters += ', '
                                note_encounters += encounter

                    if len(current_char['encounters']) > 0:
                        if current_char['role'] == 'Tank':
                            string_tank += '\n<@%s> %s' % (note, note_encounters)
                        elif current_char['role'] == 'Melee':
                            string_melee += '\n<@%s> %s' % (note, note_encounters)
                        elif current_char['role'] == 'Ranged':
                            string_ranged += '\n<@%s> %s' % (note, note_encounters)
                        elif current_char['role'] == 'Heal':
                            string_heal += '\n<@%s> %s' % (note, note_encounters)
                
                if missing_notes > 0:
                    errors.append('%d personnes dans la LU n\'ont pas leur ID discord sur leur note Wow Audit !' % missing_notes)

                if len(string_tank) > 0:
                    string_to_return += '**Tanks**%s\n\n' % string_tank 
                if len(string_heal) > 0:
                    string_to_return += '**Heals**%s\n\n' % string_heal
                if len(string_melee) > 0:
                    string_to_return += '**Melee**%s\n\n' % string_melee
                if len(string_ranged) > 0:
                    string_to_return += '**Ranged**%s\n\n' % string_ranged

                string_to_return += general_note
            
        if errors:
            errors_string = 'Et BIM ! Feignus a encore fait des conneries. A moins que la config soit pas bonne ? J\'te laisse check.'
            for index, error in enumerate(errors):
                errors_string += '\n%d. %s' % (index + 1, error)
            return True, errors_string

        return False, string_to_return