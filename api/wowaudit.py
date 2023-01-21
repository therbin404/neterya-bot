import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WowAudit:   

    def __init__(self):
        self.audit_headers = { 
            "accept": "application/json", 
            "Authorization": os.getenv('WOW_AUDIT_BEARER')
            }

    def get_roster(self):
        result = requests.get("https://wowaudit.com/v1/characters", headers=self.audit_headers)
        roster = result.json()

        return roster

    def get_raids(self, include_past):
        result = requests.get('https://wowaudit.com/v1/raids?include_past=%s' % include_past, headers=self.audit_headers)
        raids = result.json()

        return raids

    def get_raid(self, raid_id):
        result = requests.get('https://wowaudit.com/v1/raids/%s' % raid_id, headers=self.audit_headers)
        raid = result.json()

        return raid