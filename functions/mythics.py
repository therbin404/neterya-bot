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

    def format_mythics_done(self, week, min_lvl, show_all_chests):
        """Handle and format datas"""
        raw_mythics_done = self.get_mythics_done()
        res = discord.Embed(
            title=f"Mythics done",
            description=f"{week.capitalize()} week \>= {str(min_lvl)}",
            color=discord.Colour.blurple(),
        )
        string_players_done = string_players_done_wrong = string_players_not_done = ""
        for character, levels_done in raw_mythics_done.items():
            number_done = len(levels_done)
            if levels_done:
                string_to_apply = f"Bonus 1: {str(levels_done[0])}"
                if number_done > 3:
                    string_to_apply += f", Bonus 4: {str(levels_done[3])}"
                    if number_done > 7 and show_all_chests:
                        string_to_apply += f", Bonus 8: {str(levels_done[7])}"
                    if levels_done[3] >= int(min_lvl):
                        string_players_done += f"\n> **{character}**\n> *({string_to_apply})*"
                    else:
                        string_players_done_wrong += f"\n> **{character}**\n> *({string_to_apply})*"
            else:
                string_players_not_done += f"\n> **{character}**\n> *(No mythics done)*"

        res.add_field(name="✅", value=string_players_done, inline=True)
        res.add_field(name="⚠️", value=string_players_done_wrong, inline=True)
        res.add_field(name="❌", value=string_players_not_done, inline=True)
        return res
