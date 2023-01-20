import requests

class RaiderIO:

    def __init__(self):
        self.rio_headers = { 
            "accept": "application/json"
            }

    def get_mythics_done(self, realm, name, week):
        week_url = 'mythic_plus_previous_weekly_highest_level_runs' if week == 'last' else 'mythic_plus_weekly_highest_level_runs'

        result = requests.get('https://raider.io/api/v1/characters/profile?region=eu&realm=%s&name=%s&fields=%s' % (realm, name, week_url), headers=self.rio_headers)
        mythics_done = result.json()

        return mythics_done, week_url