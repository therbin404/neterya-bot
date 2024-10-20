import discord

class Helper:

    helper = ""
    section = False

    def __init__(self, section):
        self.section = section
        self.helper = self.set_helper_message()

    def set_helper_message(self):
        if self.section == "commandes":
            res = discord.Embed(
                title="Commandes",
                description="Commandes du bot discord Neterya",
                color=discord.Colour.blurple(),
            )

            commands = {
                '/lineup': {
                    'description': 'Affiche la lineup avec un ping à chaque joueur présent.',
                    'paramètres': {
                        'date': 'Date de raid demandée. Doit être au format YYYY-MM-DD. Facultatif. Si la commande est executée avant 18h un jour de raid, ce raid est pris par défaut, sinon le prochain raid prévu est selectionné.',
                    }
                },
                '/mythics': {
                    'description': 'Affiche les coffres mythique + de la grand chambre forte pour chaque joueur présent dans le roster.',
                    'paramètres': {
                        'semaine': 'Période de recherche pour les coffres (semaine actuelle ou semaine passée). Requis.',
                        'niveau': 'Le niveau minimum demandé aux joueurs. Facultatif. Par défaut 10.',
                        'troisieme_coffre': 'Affichage du troisième coffres de la grande chambre forte. Facultatif.',
                    }
                },
                '/help': {
                    'description': 'Affiche des aides sur la manière dont faire fonctionner le bot discord Neterya.',
                    'paramètres': {
                        'section': 'Précision de la catégorie sur laquelle l\'aide est demandée. Requis.',
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
                        field_value += f"Paramètres :"
                        for param, param_description in parameters.items():
                            field_value += f"\n> **{param}** - *{param_description}*"
                res.add_field(name=field_name, value=field_value, inline=False)
            return res

        elif self.section == "wowaudit":
            res = discord.Embed(
                title="Wowaudit",
                description="Configurations Wowaudit requises pour faire fonctionner le bot discord Neterya",
                color=discord.Colour.blurple(),
            )

            sub_sections = {
                "Roster": "> -Chaque joueur doit avoir sa note renseignée uniquement avec l'ID discord. Pour trouver l'ID discord d'un joueur, clique droit sur son protrait, et *Copier l'identifiant utilisateur*.",
                "Calendrier": "".join([
                    "\n> -Chaque joueur dans la section __Selected__ est considéré comme faisant partie de la lineup.",
                    "\n> -Les backups doivent être dans la section __Queued__, et leur pseudonymes écrits dans la section __Strategy / Notes__ avec le format strict suivant: **Backups : backup1, backup2**. Cette chaîne de caractères sera retirée du reste de la note quand affichée sur discord."
                    "\n> -Vous pouvez selectionner une, plusieurs, ou toutes les rencontres (ainsi que leur notes respectives), le bot discord Neterya s'adaptera en conséquence."
                ]) 
            }

            for sub_section, description in sub_sections.items():
                # add margins
                res.add_field(name="\u200b", value="\u200b", inline=False)
                res.add_field(name=sub_section, value=description, inline=False)
            return res