import discord
import os
from dotenv import load_dotenv
import functions

load_dotenv()


bot = discord.Bot()

error_msg = f"Ni !\n\n **Use the force, Harry**\n *-Gandalf* \n\n"

@bot.slash_command(name="lineup")
async def lineup(
    ctx: discord.ApplicationContext, 
    date: discord.Option(input_type=str, required=False, description='Date, at YYYY-MM-DD format')
    ):
    await ctx.defer()
    try:
        Lineup = functions.lineup.Lineup(date)
        await ctx.followup.send(embed=Lineup.lineup)
    except Exception as e:
        await ctx.followup.send(f"{error_msg}({e})")

@bot.slash_command(name="mythics")
async def mythics_command(
    ctx: discord.ApplicationContext, 
    week: discord.Option(input_type=str, choices=['current', 'last'], required=True, description='Watching period'), 
    level: discord.Option(input_type=int, required=False, description='Minimum level asked'), 
    show_all_chests: discord.Option(input_type=str, choices=['yes', 'no'], required=False, description='Display all chests')
    ):
    """Returns the mythics done by the roster, formatted to highlight min level parameter
    """
    # ctx.defer is here to replace default timeout that is too quick
    # with this, it waits for the first thing it can send (here followup.send)
    await ctx.defer()
    try:
        Mythics = functions.mythics.Mythics(week, level, show_all_chests)
        await ctx.followup.send(embed=Mythics.mythics_done)
    except Exception as e:
        await ctx.followup.send(f"{error_msg}({e})")

@bot.event
async def on_ready():
    print("Bot is ready to kick some asses!")

bot.run(os.getenv('DISCORD_BOT_KEY'))