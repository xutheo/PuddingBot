from keep_alive import keep_alive
import discord
from discord.ext import commands
from tabulate import tabulate
from discord.ui import Button, View
from discord.commands import Option
import sheets_helper
import json

tabulate.PRESERVE_WHITESPACE = True

# Cache the translation mapping
translation_mapping = sheets_helper.get_translation_mapping("Woody Translations")

# Define our bot
guild_id = [839701816991547402, 1002644143589302352, 996415598529613825] # Server ids
bot = commands.Bot(command_prefix=commands.when_mentioned_or("."))

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="WC bot"))
    print("Bot Online!")
    print("-------------------------")
    print(f"Name: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    print(f"Servers in: {len(bot.guilds)}")
    print("-------------------------")

# =============== Transcribe TL =============
@bot.slash_command(guild_ids=guild_id, description="Transcribe TL")
async def transcribe_tl(
        ctx,
        boss: Option(int, "1 - 5", min_value=1, max_value=5),
        unit1, unit2, unit3, unit4, unit5,
        tl: discord.Attachment):

    # Translate timeline using woody-grade translation technology
    timeline = (await tl.read()).decode('UTF-8')
    for entry in translation_mapping:
        timeline = timeline.replace(entry[0], " " + entry[1] + " ")
    tl_worksheet = sheets_helper.get_timelines_worksheet(boss)

    # Define yes button for if we want to save this TL
    yes_button = Button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button_callback(interaction):
        number_of_timelines = int(tl_worksheet.get_value('B1'))
        print(number_of_timelines)
        title_str = 'D' + str(boss)
        if number_of_timelines + 1 < 10:
            title_str += '0' + str(number_of_timelines)
        else:
            title_str += str(number_of_timelines)
        tl_worksheet.update_value('A' + str(number_of_timelines + 2), 'D' + title_str)
        tl_worksheet.update_value('B' + str(number_of_timelines + 2), timeline)
        # Note that the units are stored from F-J for readability in the sheet
        tl_worksheet.update_value('G' + str(number_of_timelines + 2), unit1)
        tl_worksheet.update_value('H' + str(number_of_timelines + 2), unit2)
        tl_worksheet.update_value('I' + str(number_of_timelines + 2), unit3)
        tl_worksheet.update_value('J' + str(number_of_timelines + 2), unit4)
        tl_worksheet.update_value('K' + str(number_of_timelines + 2), unit5)
        tl_worksheet.update_value('B1', str(number_of_timelines + 1))
        await interaction.response.edit_message(content="Saved!", view=None)
    yes_button.callback = yes_button_callback

    # Define no button for if we want to save this TL
    no_button = Button(label="No", style=discord.ButtonStyle.red)
    async def no_button_callback(interaction):
        await interaction.response.edit_message(content="Not Saved!", view=None)
    no_button.callback = no_button_callback

    view = View()
    view.add_item(yes_button)
    view.add_item(no_button)

    await ctx.respond(timeline, ephemeral=True)
    await ctx.respond("Would you like to save this tl?", view=view, ephemeral=True)

# =============== List TLs for a boss =============
@bot.slash_command(guild_ids=guild_id, description="List TLs")
async def list_tls(ctx, boss,
        unit_filter1: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter2: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter3: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter4: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter5: Option(str, "Enter a unit name", required=False, default=None)):
    tl_worksheet = sheets_helper.get_timelines_worksheet(boss)
    number_of_timelines = int(tl_worksheet.get_value('B1'))
    if number_of_timelines == 0:
        await ctx.respond("There are no timelines to display for this boss!", ephemeral=True)
        return

    all_timelines = tl_worksheet.get_values('A2', 'K' + str(number_of_timelines + 1))

    def filter_unit(matrix, unit):
        if unit is None:
            return matrix
        result_matrix = []
        for row in matrix:
            if unit in row[5:10]:
                result_matrix.append(row)
        return result_matrix

    #print(all_timelines)
    all_timelines = filter_unit(all_timelines, unit_filter1)
    all_timelines = filter_unit(all_timelines, unit_filter2)
    all_timelines = filter_unit(all_timelines, unit_filter3)
    all_timelines = filter_unit(all_timelines, unit_filter4)
    all_timelines = filter_unit(all_timelines, unit_filter5)

    if len(all_timelines) == 0:
        await ctx.respond("There are no timelines with those units to display for this boss!", ephemeral=True)
        return

    idx = 0
    # Define previous button for displaying tls
    previous_button = Button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_button_callback(interaction):
        nonlocal idx
        previous_embed = discord.Embed(title=all_timelines[(idx - 1) % len(all_timelines)][0],
                              description=all_timelines[(idx - 1) % len(all_timelines)][1],
                              color=0xfffeff)
        idx -= 1
        await interaction.response.edit_message(embed=previous_embed, view=view)
    previous_button.callback = previous_button_callback

    # Define next button for displaying tls
    next_button = Button(label="Next", style=discord.ButtonStyle.blurple)
    async def next_button_callback(interaction):
        nonlocal idx
        next_embed = discord.Embed(title=all_timelines[(idx + 1) % len(all_timelines)][0],
                              description=all_timelines[(idx + 1) % len(all_timelines)][1],
                              color=0xfffeff)
        idx += 1
        await interaction.response.edit_message(embed=next_embed, view=view)
    next_button.callback = next_button_callback

    # Define done button for displaying tls
    done_button = Button(label="Done", style=discord.ButtonStyle.green)
    async def done_button_callback(interaction):
        current_embed = discord.Embed(title=all_timelines[idx % len(all_timelines)][0],
                              description=all_timelines[idx % len(all_timelines)][1],
                              color=0xfffeff)
        await interaction.response.edit_message(embed=current_embed, view=None)
    done_button.callback = done_button_callback

    view = View()
    view.add_item(previous_button)
    view.add_item(done_button)
    view.add_item(next_button)

    embed = discord.Embed(title=all_timelines[idx][0],
                          description=all_timelines[idx][1],
                          color=0xfffeff)
    await ctx.respond(embed=embed, ephemeral=True, view=view)


keep_alive()
token = json.load(open("service_account.json"))['discord_token']
bot.run(token)