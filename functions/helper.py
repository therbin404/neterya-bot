import discord

class Helper:

    helper = ""
    section = False

    def __init__(self, section):
        self.section = section
        self.helper = self.set_helper_message()

    def set_helper_message(self):
        if self.section == "commands":
            res = discord.Embed(
                title="Commands",
                description="Commands of Neterya Bot on Discord",
                color=discord.Colour.blurple(),
            )

            commands = {
                '/lineup': {
                    'description': 'Print the formated lineup with ping to all players in it',
                    'parameters': {
                        'date': 'Desired raid date. Must be at YYY-MM-DD format. Not required. Default to the today raid if command executed before 18h, else take the next raid.',
                    }
                },
                '/mythics': {
                    'description': 'Print the two first vault chests for mythics plus for each players in the roster',
                    'parameters': {
                        'week': 'Select if you want to see the current or the past week. Required.',
                        'level': 'The minimum level asked to the players. Not required. Default to 10.',
                        'show_third_chest': 'Choose if you want to see the third chest of each player. Not required.',
                    }
                },
                '/help': {
                    'description': 'Display help sections on how to run Neterya Bot',
                    'parameters': {
                        'section': 'Select which section you look help for. Required.',
                    }
                },
            }

            for command, subcommands in commands.items():
                # add margins
                res.add_field(name="\u200b", value="\u200b", inline=False)
                field_name = command
                field_value = "\n"
                for description, parameters in subcommands.items():
                    if isinstance(parameters, str):
                        field_name += f" : {parameters}"
                    if isinstance(parameters, dict):
                        field_value += f"Parameters :"
                        for param, param_description in parameters.items():
                            field_value += f"\n> **{param}** - *{param_description}*"
                res.add_field(name=field_name, value=field_value, inline=False)
            return res

        elif self.section == "wowaudit":
            res = discord.Embed(
                title="Wowaudit",
                description="Wowaudit settings required to run Neterya Bot",
                color=discord.Colour.blurple(),
            )

            sub_sections = {
                "Roster": "> -Each players must have only their discord ID in their note. To find the discord ID, right click on discord name, and copy user ID",
                "Calendar": "".join([
                    "\n> -Each player that is on Selected section is considered to be in the lineup.",
                    "\n> -Backups have to be in Queued section, and written in the Strategy / Notes section with the following format : **Backups : backup1, backup2**. This string will be removed from the rest of the note when printed on discord."
                    "\n> -You can set All encounters, or only some encounters (and associated notes), the discord print will adapt accordingly."
                ]) 
            }

            for sub_section, description in sub_sections.items():
                # add margins
                res.add_field(name="\u200b", value="\u200b", inline=False)
                res.add_field(name=sub_section, value=description, inline=False)
            return res