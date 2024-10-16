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

    def format_mythics_done(self, week, min_lvl, show_all_chests):
        """Handle and format datas"""
        raw_mythics_done = self.get_mythics_done()
        res = discord.Embed(
            title=f"Mythics done",
            description=f"{week.capitalize()} week \>= {str(min_lvl)}",
            color=discord.Colour.blurple(),
        )
        string_players_done = string_players_done_2 = string_players_done_wrong = string_players_done_wrong_2 = string_players_not_done = string_players_not_done_2 = ""
        for character, levels_done in raw_mythics_done.items():
            number_done = len(levels_done)
            if levels_done:
                string_to_apply = f"Bonus 1: {str(levels_done[0])}"
                if number_done > 3:
                    string_to_apply += f", Bonus 4: {str(levels_done[3])}"
                    if number_done > 7 and show_all_chests:
                        string_to_apply += f", Bonus 8: {str(levels_done[7])}"
                    if levels_done[3] >= int(min_lvl):
                        if self.is_too_long(string_players_done):
                            string_players_done_2 += f"\n> **{character}**\n> *({string_to_apply})*"
                        else:
                            string_players_done += f"\n> **{character}**\n> *({string_to_apply})*"
                    else:
                        if self.is_too_long(string_players_done_wrong):
                            string_players_done_wrong_2 += f"\n> **{character}**\n> *({string_to_apply})*"
                        else:
                            string_players_done_wrong += f"\n> **{character}**\n> *({string_to_apply})*"
            else:
                if self.is_too_long(string_players_not_done):
                    string_players_not_done_2 += f"\n> **{character}**\n> *(No mythics done)*"
                else:
                    string_players_not_done += f"\n> **{character}**\n> *(No mythics done)*"


        if string_players_done:
            res.add_field(name="✅", value=string_players_done, inline=True)
        if string_players_done_2:
            res.add_field(name="✅ (2)", value=string_players_done_2, inline=True)

        if string_players_done_wrong:
            res.add_field(name="⚠️", value=string_players_done_wrong, inline=True)
        if string_players_done_wrong_2:
            res.add_field(name="⚠️ (2)", value=string_players_done_wrong_2, inline=True)

        if string_players_not_done:
            res.add_field(name="❌", value=string_players_not_done, inline=True)
        if string_players_not_done_2:
            res.add_field(name="❌ (2)", value=string_players_not_done_2, inline=True)
        return res
