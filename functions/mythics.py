import api

class Mythics:

    def __init__(self, week, min_level):
        self.week = week
        self.min_level = min_level
        self.mythics_done = self.format_mythics_done(week, min_level)

    def get_mythics_done(self):
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

    def format_mythics_done(self, week, min_lvl):
        # we set this block as diff code because we want to color it red, gray, or green
        string_to_return = f"**{week} week \>= {str(min_lvl)}**\n```diff\n"
        raw_mythics_done = self.get_mythics_done()

        for character, levels_done in raw_mythics_done.items():
            string_to_apply = character + ': '
            mark = '-'
            number_done = len(levels_done)
            if levels_done:
                string_to_apply += f"Bonus 1: {str(levels_done[0])}"
                if number_done > 3:
                    string_to_apply += f", Bonus 4: {str(levels_done[3])}"
                    if levels_done[3] >= 10:
                        mark = '+'
            string_to_return += f"{mark} {(str(number_done))} {string_to_apply}\n"

        string_to_return += '\n```'
        return string_to_return
