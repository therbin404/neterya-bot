import api
import discord
import re
import unicodedata
from datetime import datetime
from datetime import timedelta
from itertools import groupby

def sanitize_string(string):
    """Remove all accents and lower string"""
    nfkd_form = unicodedata.normalize('NFKD', string)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    decoded = only_ascii.decode("utf-8")
    return decoded.lower()

def set_role_icons(role):
    """Set symbols and text formatting based on role"""
    if role == "Tank":
        role = f"🛡️  **{role}**"
    if role == "Heal":
        role = f"🩹  **{role}**"
    if role == "Melee":
        role = f"⚔️  **{role}**"
    if role == "Ranged":
        role = f"🏹  **{role}**"
    if role == "Backups":
        role = f"🔄  **{role}**"
    return role

def format_notes(notes):
    """Remove html tags from notes"""
    html_free_notes = re.sub(r"<[^<]+?>", "", notes)
    return html_free_notes

class Lineup:

    mapped_char_discord = []
    roster = []
    include_past = False

    def __init__(self, date):
        self.date = date
        self.include_past = True if (self.date and self.date < datetime.now().strftime('%Y-%m-%d')) else False
        self.wowaudit = api.wowaudit.WowAudit()

        self.roster = self.wowaudit.get_roster()
        # we gonna sanitize player names to avoid differences in capital letters or accents later
        for player in self.roster:
            player['name'] = sanitize_string(player['name'])

        self.mapped_char_discord = self.map_char_discord()
        self.lineup = self.get_lineup()

    def get_next_raid(self):
        """Get the next raid based on date"""
        raids = self.wowaudit.get_raids(self.include_past)

        now = datetime.now()

        # if we have a date, we want the raid with that date
        if self.date:
            next_raid = list(filter(lambda raid: raid['date'] == self.date, raids['raids']))
            if not next_raid:
                raise Exception(f"There is no raid at {self.date}")
            next_raid_id = next_raid[0]['id'] if next_raid else False
        # otherwise, we want the next raid (today if command sent before 18h, next one (can be in X days) if sent after)
        # sent before 18h a day of raid : select first upcoming raid
        # sent after 18h a day of raid : select second upcoming raid
        # sent some days before the next raid : select first upcoming raid
        else:
            now = datetime.now()
            raid_tonight = raids['raids'][0]['date'] == now.strftime('%Y-%m-%d') if raids['raids'] else False
            # also check if there are multiple upcoming raids upcoming raids
            days = 1 if (now.hour > 18 and raid_tonight) and not len(raids['raids']) == 1 else 0
            next_raid_id = raids['raids'][days]['id'] if raids['raids'] else False

        if next_raid_id:
            # set self.date to print it in discord message
            result = self.wowaudit.get_raid(next_raid_id)
            self.date = self.date if self.date else result['date']
            return result
        raise Exception("There is no upcoming raid")


    def get_selected_players(self, selections, all_raid=False):
        """Returns a dict that contains all discord ids selected grouped by role
        
        e.g: {'Ulgrax': {'Ranged': [39057542431234]}, 'The Bloodbound Horror': {'Ranged': [390575423443, 51919515234234], 'Melee': [51203698123213]}}"""
        encounter_selections = {}
        # we sort the dict by role, as groupby only group consecutive items together
        sorted_selections = sorted(selections, key=lambda selection: selection['role'])

        roles_grouped = groupby(sorted_selections, lambda x: x['role'])
        
        for role, players in roles_grouped:
            encounter_selections[role] = [player.get('character').get('id') for player in players if player.get('selected')] if all_raid else [player.get('character_id') for player in players if player.get('selected')]

            for index, character_id in enumerate(encounter_selections[role]):
                encounter_selections[role][index] = self.find_discord_id(character_id)

        return encounter_selections

    def find_discord_ids_by_name(self, names):
        """Find discord id with names as a list"""
        discord_ids = []
        for name in names:
            discord_id = self.find_discord_id(name=name)
            if discord_id:
                discord_ids.append(discord_id)
        return discord_ids

    def find_discord_id(self, character_id=False, name=False):
        """Find the discord id based on character id or name"""
        if name:
            # we sanitize the player to avoid differences in capital letters or accents
            name = sanitize_string(name)
            # TODO : Add exception if name not found
            character_id = [item.get('id') for item in self.roster if item.get('name') == name]
            if not character_id:
                raise Exception(f"The ID of the player {name} was not found")
            character_id = character_id[0] if character_id else False

        return ''.join([item.get(character_id) for item in self.mapped_char_discord if item.get(character_id)])


    def map_char_discord(self):
        """Init an array of dict that map discord id and character id"""
        return [{char.get('id'): char.get('note')} for char in self.roster]


    def get_lineup(self):
        """Main method to get and format lineup"""
        next_raid = self.get_next_raid()

        if next_raid:

            # now we gonna handle the selections of each encounters (or all encounters if none is enabled)
            all_selected = {}
            activated_encounters = [encounter for encounter in next_raid['encounters'] if encounter['enabled']]
            for activated_encounter in activated_encounters:
                selections = activated_encounter.get('selections')
                all_selected[activated_encounter.get('name')] = {
                        'lineup': self.get_selected_players(selections),
                        'note': activated_encounter['notes'] if activated_encounter['notes'] else ""
                    }

            if not activated_encounters:
                all_selected['All raid'] = {
                    'lineup': self.get_selected_players(next_raid['signups'], all_raid=True),
                    'note': next_raid['notes'] if next_raid['notes'] else ""
                    }

            for encounter, selection in all_selected.items():
                selection = self.find_backups(selection)
                
            result = self.format_lineup(all_selected)
            return result

    def format_lineup(self, all_selected):
        """Create the embed that will be shown on discord"""
        nb_encounters = len(all_selected)
        res = discord.Embed(
            title=f"Lineup du {self.date}",
            color=discord.Colour.blurple(),
        )

        for encounter_name, encounter in all_selected.items():
            if nb_encounters > 1:
                string_total = string_roles = ""
                for role, players in encounter['lineup'].items():
                    string_roles += f"\n> \n> {set_role_icons(role)} :"
                    for player in players:
                        string_roles += f"\n> <@{player}>"
                string_total += f"\n{string_roles}\n> \n> ℹ️  **Note**\n"
                # Note can be empty on screen and have some line breaks, due to backups string remove
                if encounter['note'] and not all(char == "\n" for char in encounter['note']):
                    string_total += f"> {encounter['note']}"
                res.add_field(name=encounter_name, value=string_total, inline=True)
            else:
                for role, players in encounter['lineup'].items():
                    string_players = ""
                    for player in players:
                        string_players += f"\n> <@{player}>"
                    res.add_field(name=set_role_icons(role), value=string_players, inline=True)

                res.add_field(name="ℹ️  **Note**", value=encounter['note'], inline=True)

        return res

    def find_backups(self, selection):
        """Return discord ids from backups found on the note"""
        note = format_notes(selection['note'])
        backup_string = re.search(r"Backups\s*:\s*(.+)", note)
        selection['lineup']['Backups'] = []
        if backup_string:
            backup_players = backup_string.group(1).split(", ")
            selection['lineup']['Backups'] = self.find_discord_ids_by_name(names=backup_players)
            # now we have backups registered, remove the backups part of the note
        selection['note'] = re.sub(r"Backups\s*:\s*(.+)", "", note)
        return selection