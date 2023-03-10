import api
import re
import datetime

class Lineup:

    def find_backups(self, text, roster):
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

    def get_lineup(self, date = False):
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