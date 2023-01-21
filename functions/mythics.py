import api

class Mythics:

    def get_mythics_done(self, week):
        wowaudit = api.wowaudit.WowAudit()
        raiderio = api.raiderio.RaiderIO()
        roster = wowaudit.get_roster()

        roster_mythics_done = {}

        for number, character in enumerate(roster):
            name = character['name']
            realm = character['realm'].replace('Marecage de Zangar', 'Marécage de Zangar').replace(' ', '-')
            # returns (mythics_done, week_url)
            mythics_done = raiderio.get_mythics_done(realm, name, week)

            mythic_datas = []

            # we only want weekly mythics done
            for mythic_done in mythics_done[0][mythics_done[1]]:
                mythic_datas.append(mythic_done['mythic_level'])

            roster_mythics_done[character['name']] = mythic_datas

        return roster_mythics_done

    def format_mythics_done(self, roster_mythics_done, min_lvl):
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