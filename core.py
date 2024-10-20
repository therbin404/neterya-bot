import discord
import os
from dotenv import load_dotenv
import functions

load_dotenv()


bot = discord.Bot()

file = discord.File("./borderlands-claptrap.gif", filename="borderlands-claptrap.gif")
embed_error = discord.Embed(
            title=f"Erreur !",
            )
embed_error.set_image(url="attachment://borderlands-claptrap.gif")

@bot.slash_command(name="help")
async def help(
    ctx: discord.ApplicationContext, 
    section: discord.Option(input_type=str, choices=['commandes', 'wowaudit'], required=True, description='Sujet nécessitant une aide.'), 
    ):
    """Affiche des aides sur la manière dont faire fonctionner le bot discord Neterya"""
    await ctx.defer()
    try:
        Helper = functions.helper.Helper(section)
        await ctx.followup.send(embed=Helper.helper)
    except Exception as e:
        embed_error.description=str(e)
        await ctx.followup.send(file=file, embed=embed_error)

@bot.slash_command(name="lineup")
async def lineup(
    ctx: discord.ApplicationContext, 
    date: discord.Option(input_type=str, required=False, description='Date, au format YYYY-MM-DD')
    ):
    """Affiche la lineup avec un ping à chaque joueur présent"""
    await ctx.defer()
    try:
        Lineup = functions.lineup.Lineup(date)
        await ctx.followup.send(embed=Lineup.lineup)
    except Exception as e:
        embed_error.description=str(e)
        await ctx.followup.send(file=file, embed=embed_error)

@bot.slash_command(name="mythics")
async def mythics_command(
    ctx: discord.ApplicationContext, 
    semaine: discord.Option(input_type=str, choices=['actuelle', 'passée'], required=True, description='Période de recherche'), 
    niveau: discord.Option(input_type=int, required=False, description='Niveau minimum demandé'), 
    troisieme_coffre: discord.Option(input_type=str, choices=['oui', 'non'], required=False, description='Afficher le troisième coffre')
    ):
    """Affiche les coffres mythique + de la grand chambre forte pour chaque joueur présent dans le roster
    """
    # ctx.defer is here to replace default timeout that is too quick
    # with this, it waits for the first thing it can send (here followup.send)
    await ctx.defer()
    try:
        Mythics = functions.mythics.Mythics(semaine, niveau, troisieme_coffre)
        await ctx.followup.send(embed=Mythics.mythics_done)
    except Exception as e:
        embed_error.description=str(e)
        await ctx.followup.send(file=file, embed=embed_error)

@bot.event
async def on_ready():
    print("Bot is ready to kick some asses!")

bot.run(os.getenv('DISCORD_BOT_KEY'))