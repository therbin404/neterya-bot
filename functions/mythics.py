import api
import discord

class Mythics:

    def __init__(self, week, min_level, show_all_chests):
        self.week = week
        self.min_level = min_level
        show_all_chests = True if show_all_chests == 'yes' else False
        self.mythics_done = self.format_mythics_done(week, min_level, show_all_chests)

    def get_mythics_done(self):
        """Get all mythics done informations from wowaudit and raider.io"""
        wowaudit = api.wowaudit.WowAudit()
        raiderio = api.raiderio.RaiderIO()
        roster = wowaudit.get_roster()

        roster_mythics_done = {}

        for character in roster:
            name = character['name']
            realm = character['realm']
            mythics_done, week_parameter = raiderio.get_mythics_done(realm, name, self.week)

            # associate 'player name' key to 'level of mythics done' value for datas returned by the api
            roster_mythics_done[character['name']] = [mythic_done['mythic_level'] for mythic_done in mythics_done[week_parameter]]

        return roster_mythics_done

    def is_too_long(self, string):
        """Embed fields on discord accept up to 1024 chars, so we gonna take a safety margin"""
        return True if len(string) > 824 else False

    def handle_discord_strings(self, character, string_to_apply, string_list, string_list_overflow):
        final_character_string = f"\n> **{character}**\n> *({string_to_apply})*"
        if self.is_too_long("".join(string_list)):
            string_list_overflow.append(final_character_string)
        else:
            string_list.append(final_character_string)


    def format_mythics_done(self, week, min_lvl, show_all_chests):
        """Handle and format datas"""
        raw_mythics_done = self.get_mythics_done()
        res = discord.Embed(
            title=f"Mythics done",
            description=f"{week.capitalize()} week \>= {str(min_lvl)}",
            color=discord.Colour.blurple(),
        )
        string_players_done = []
        string_players_done_overflow = []
        string_players_done_wrong = []
        string_players_done_wrong_overflow = []
        string_players_not_done = []
        string_players_not_done_overflow = []
        for character, levels_done in raw_mythics_done.items():
            number_done = len(levels_done)
            string_to_apply = "No mythics done"
            if levels_done:
                string_to_apply = f"Bonus 1: {str(levels_done[0])}"
                if number_done > 3:
                    string_to_apply += f", Bonus 4: {str(levels_done[3])}"
                    if number_done > 7 and show_all_chests:
                        string_to_apply += f", Bonus 8: {str(levels_done[7])}"
                    if levels_done[3] >= int(min_lvl):
                        self.handle_discord_strings(character, string_to_apply, string_players_done, string_players_done_overflow)
                else:
                    self.handle_discord_strings(character, string_to_apply, string_players_done_wrong, string_players_done_wrong_overflow)
            else:
                self.handle_discord_strings(character, string_to_apply, string_players_not_done, string_players_not_done_overflow)

        fields_to_return = [
            ("✅", string_players_done, string_players_done_overflow),
            ("⚠️", string_players_done_wrong, string_players_done_wrong_overflow),
            ("❌", string_players_not_done, string_players_not_done_overflow),
        ]

        for icon, string_value, string_overflow in fields_to_return:
            if string_value:
                value_to_return = "".join(string_value)
                res.add_field(name=icon, value=value_to_return, inline=True)
            if string_overflow:
                value_to_return = "".join(string_overflow)
                res.add_field(name=icon, value=value_to_return, inline=True)

        return res
