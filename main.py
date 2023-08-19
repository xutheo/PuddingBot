from keep_alive import keep_alive
import discord
from discord.ext import commands
from tabulate import tabulate
from discord.ui import Button, View
from discord.commands import Option
import sheets_helper
import json
import unicodedata

tabulate.PRESERVE_WHITESPACE = True

# Cache the translation mapping
translation_mapping = sheets_helper.get_translation_mapping()

# Define our bot
guild_id = [1002644143589302352, 1025780100291112960]  # Server ids
channel_id = [1067620591038889995, 1141149506021367849]  # Channel ids
bot = commands.Bot(command_prefix=commands.when_mentioned_or("."))


async def is_allowed_channel(ctx):
    return ctx.channel.id in channel_id


async def convert_and_translate_timeline(tl, translate=True):
    # Translate timeline using woody-grade translation technology
    timeline = (await tl.read()).decode('UTF-8')
    timeline = unicodedata.normalize("NFKC", timeline)
    if translate:
        for entry in translation_mapping:
            timeline = timeline.replace(entry[0], " " + entry[1] + " ")
    return timeline


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="for timelines"))
    print("Bot Online!")
    print("-------------------------")
    print(f"Name: {bot.user.name}")
    print(f"ID: {bot.user.id}")
    print(f"Servers in: {len(bot.guilds)}")
    print("-------------------------")


# =============== Translate TL =============
@bot.slash_command(guild_ids=guild_id, description="Translate TL")
async def translate_tl(
        ctx,
        tl: discord.Attachment,
        show: Option(bool, "Show this timeline to everyone", required=False, default=False)):
    if not await is_allowed_channel(ctx):
        await ctx.respond("Permission denied")
        return
    timeline = await convert_and_translate_timeline(tl)
    embed = discord.Embed(title="Translated Timeline",
                        description=timeline,
                        color=0xfffeff)
    await ctx.respond(embed=embed, ephemeral=(not show))


# =============== Transcribe TL =============
@bot.slash_command(guild_ids=guild_id, description="Transcribe TL")
async def transcribe_tl(
        ctx,
        boss: Option(int, "1 - 5", min_value=1, max_value=5),
        unit1, unit2, unit3, unit4, unit5,
        tl: discord.Attachment,
        translate: Option(bool, "Translate the TL to english", required=False, default=True)):
    if not await is_allowed_channel(ctx):
        await ctx.respond("Permission denied")
        return

    timeline = await convert_and_translate_timeline(tl)
    tl_worksheet = sheets_helper.get_timelines_worksheet(boss)

    # Define yes button for if we want to save this TL
    yes_button = Button(label="Yes", style=discord.ButtonStyle.green)

    async def yes_button_callback(interaction):
        number_of_timelines = int(tl_worksheet.get_value('B1'))

        # Title dynamically updates in google sheets for when we delete rows
        title_str = "=CONCAT(\"D" + str(boss) + "\", IF(ROW() < 10, CONCAT(0, ROW()), ROW()))"

        # Note that the units are stored from F-J for readability in the sheet
        tl_worksheet.update_value(f'A{number_of_timelines + 2}', title_str, parse=True)
        tl_worksheet.update_values_batch(
            [f'B{number_of_timelines + 2}',
                f'G{number_of_timelines + 2}',
                f'H{number_of_timelines + 2}',
                f'I{number_of_timelines + 2}',
                f'J{number_of_timelines + 2}',
                f'K{number_of_timelines + 2}',
                'B1'],
            [[[timeline]], [[unit1]], [[unit2]], [[unit3]], [[unit4]], [[unit5]], [[str(number_of_timelines + 1)]]])

        await interaction.response.edit_message(content="Saved!", view=None)
    yes_button.callback = yes_button_callback

    # Define no button for if we want to save this TL
    no_button = Button(label="No", style=discord.ButtonStyle.red)

    async def no_button_callback(interaction):
        await interaction.response.edit_message(content="Not Saved!", view=None)
    no_button.callback = no_button_callback

    view = View(timeout=None)
    view.add_item(yes_button)
    view.add_item(no_button)

    embed = discord.Embed(title="New Timeline",
                        description=timeline,
                        color=0xfffeff)
    await ctx.respond(embed=embed, ephemeral=True)
    await ctx.respond("Would you like to save this tl?", view=view, ephemeral=True)


# =============== Lists one timeline with specified id =============
@bot.slash_command(guild_ids=guild_id, description="Gets target TL")
async def list_tl(
        ctx,
        id,
        show: Option(bool, "Show this timeline to everyone", required=False, default=False)):
    boss = id[1]
    row = int(id[2:])

    tl_worksheet = sheets_helper.get_timelines_worksheet(boss)
    timeline = tl_worksheet.get_value('B' + str(row))

    if not timeline or id[2:] == '01':
        await ctx.respond("A timeline with that ID does not exist!", ephemeral=True)
        return

    embed = discord.Embed(title=id,
                        description=timeline,
                        color=0xfffeff)
    await ctx.respond(embed=embed, ephemeral=not show)


# =============== List all TLs for a boss =============
@bot.slash_command(guild_ids=guild_id, description="List TLs")
async def list_tls(ctx, boss,
        unit_filter1: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter2: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter3: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter4: Option(str, "Enter a unit name", required=False, default=None),
        unit_filter5: Option(str, "Enter a unit name", required=False, default=None)):
    if not await is_allowed_channel(ctx):
        await ctx.respond("Permission denied")
        return

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


# =============== Deletes one timeline with specified id =============
@bot.slash_command(guild_ids=guild_id, description="Deletes target TL")
@commands.has_role(1025780684574433390)
async def delete_tl(ctx, id):
    boss = id[1]
    row = int(id[2:])

    tl_worksheet = sheets_helper.get_timelines_worksheet(boss)
    timeline = tl_worksheet.get_value('B' + str(row))

    # Define yes button for if we want to save this TL
    yes_button = Button(label="Yes", style=discord.ButtonStyle.red)

    if not timeline or id[2:] == '01':
        await ctx.respond("A timeline with that ID does not exist!", ephemeral=True)
        return

    async def yes_button_callback(interaction):
        tl_worksheet.delete_rows(row)
        await interaction.response.edit_message(content="Deleted " + id + "!", view=None)
    yes_button.callback = yes_button_callback

    # Define no button for if we want to save this TL
    no_button = Button(label="No", style=discord.ButtonStyle.blurple)

    async def no_button_callback(interaction):
        await interaction.response.edit_message(content="Not Deleted!", view=None)
    no_button.callback = no_button_callback

    view = View()
    view.add_item(yes_button)
    view.add_item(no_button)

    embed = discord.Embed(title=id,
                        description=timeline,
                        color=0xfffeff)
    await ctx.respond(embed=embed, ephemeral=True)
    await ctx.respond("Are you SURE you want to delete this TL?", view=view, ephemeral=True)


# =============== Reload translations from woody translation sheet =============
@bot.slash_command(guild_ids=guild_id, description="Pulls the latest woody-grade translations")
@commands.has_role(1025780684574433390)
async def update_vocab_bank(ctx):
    global translation_mapping
    translation_mapping = sheets_helper.get_translation_mapping()
    await ctx.respond("Retrieved the latest woody-grade translations!", ephemeral=True)


# =============== Help command =============
@bot.slash_command(guild_ids=guild_id, description="Get a description of all commands")
async def help(ctx):
    embed = discord.Embed(title="Commands Help", color=0xfffeff)

    embed.add_field(
        name="/translate_tl - Translates a text file timeline with woody-grade technology",
        value="```\ttl: Attached file containing timeline" +
            "\n\tshow (Optional): If you want to show this TL to everybody```",
        inline=False)

    embed.add_field(
        name="/transcribe_tl - Transcribes a timeline and stores it for further use",
        value="```\tboss: Boss that you want this TL to target (1-5)" +
            "\n\tunit1-5: The five units that are a part of the TL" +
            "\n\ttl: Attached file containing timeline" +
            "\n\ttranslate (Optional): If you want to translate this TL```",
        inline=False)

    embed.add_field(
        name="/list_tl - Gets the target TL with specified ID",
        value="```\tid: ID of the timeline; ex.'D101'```",
        inline=False)

    embed.add_field(
        name="/list_tls - Gets all Tls for a given boss and units filters",
        value="```\tboss: Boss that you want the TL from (1-5)" +
            "\n\tunit_filter1-5 (Optional): Unit filters for the TL```",
        inline=False)

    embed.add_field(
        name="/delete_tl - Deletes the target TL with specified ID. (ADMIN ONLY)",
        value="```\tid: ID of the timeline; ex.'D101'```",
        inline=False)

    embed.add_field(
        name="/update_vocab_bank - Refreshes woody-grade translations. (ADMIN ONLY)",
        value="",
        inline=False)

    await ctx.respond(embed=embed, ephemeral=True)


keep_alive()
token = json.load(open("service_account.json"))['discord_token']
bot.run(token)
