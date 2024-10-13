import discord
# import typing
import os
# from discord import app_commands
from dotenv import load_dotenv
import functions

load_dotenv()

# intents = discord.Intents.default()
# intents.message_content = True
# client = discord.Client(intents=intents)
# tree = app_commands.CommandTree(client)
# guild_obj = discord.Object(id=int(os.getenv('DISCORD_ID')))

# admin_id = 222844821264531456

# @tree.command(name="lineup", description="Publish lineup for next raid", guild=guild_obj)
# async def lineup(interaction, date: typing.Optional[str] = ''):
#     # defer is here to quick respond to discord, to avoid timeout of application
#     await interaction.response.defer()

#     admin = await client.fetch_user(admin_id)
#     await admin.send('%s a utilisé la commande /%s (avec les arguments: %s)' %(interaction.user, interaction.command.name, date))

#     Lineup = functions.lineup.Lineup()
#     # return [(bool), errors or string]
#     # first argument if there's any errors
#     # second is errors, or expected response if there's no errors
#     response = Lineup.get_lineup(date)
    
#     if response[0]:
#         await interaction.delete_original_response()
#         await interaction.user.send(content=response[1])
#     elif not response[0]:
#         await interaction.edit_original_response(content=response[1])


bot = discord.Bot()

@bot.slash_command(name="lineup")
async def lineup(ctx: discord.ApplicationContext, date: discord.Option(str)):
    print(date)
    await ctx.respond(f"test lu")

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
        await ctx.followup.send(f"Oops, something went wrong ! Try to use the force, Luke !\n({e})")

@bot.event
async def on_ready():
    print("Bot is ready to kick some asses!")

bot.run(os.getenv('DISCORD_BOT_KEY'))