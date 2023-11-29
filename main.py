from keep_alive import keep_alive
import discord
from discord.ext import commands
from tabulate import tabulate
from discord.commands import Option
import sheets_helper
import Timelines
import json
import unicodedata
import os
from discord.ui import Button, View
from embed_helpers import get_display_embeds_mobile, get_display_embeds, GetTLView, get_display_embeds2
from functools import partial
from clan_battle_info import boss_names, boss_image_urls
import re
from threading import Thread
from icon_bank import icon_bank, clean_text
import difflib
from Homework import get_homework

tabulate.PRESERVE_WHITESPACE = True

# Cache the translation mapping and animation bank
translation_mapping = sheets_helper.get_translation_mapping()
animation_bank = sheets_helper.get_animation_videos()
names_bank = sheets_helper.get_animation_videos_names_bank()

# Define our bot
guild_id = [1002644143589302352, 1025780100291112960, 1166119511376793661]  # Server ids
channel_id = [1067620591038889995, 1141149506021367849, 
            1099083593222983700, 1102872644413571103, 
            1102872692178309131, 1102872715473457224, 1176655969657303142]  # Channel ids
bot = commands.Bot(command_prefix=commands.when_mentioned_or("."))


async def is_allowed_channel(ctx):
    #return ctx.channel.id in channel_id
    return True


async def convert_and_translate_timeline(tl, translate=True):
    # Translate timeline using woody-grade translation technology
    timeline = (await tl.read()).decode('UTF-8')
    timeline = unicodedata.normalize("NFKC", timeline)
    if translate:
        timeline = await translate_text(timeline)
    return timeline


async def translate_text(text):
    text = unicodedata.normalize("NFKC", text)
    for entry in translation_mapping:
        text = text.replace(entry[0], " " + entry[1] + " ")
    return text


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


# =============== Lists one timeline with specified id =============
@bot.slash_command(description="Gets target TL")
async def get_tl(
        ctx,
        id,
        ot: Option(int, "Input your ot timer in seconds.", required=False, default=False),
        show: Option(bool, "Show this timeline to everyone", required=False, default=False),
        compact: Option(bool, "Show a compact version of the TL", required=False, default=False)):
    boss = int(id[1])
    mobile = ctx.author.is_on_mobile()
    print(mobile)
    #compact = False

    timeline = Timelines.get_from_db(boss, id)
    if timeline is None:
        await ctx.respond(f"A timeline with that ID does not exist!\nPlease run \"/load_tls {boss}\" if you have written {id} recently.", ephemeral=True)
        return

    embeds = get_display_embeds_mobile(timeline, ot) if mobile or compact or timeline.simple else get_display_embeds2(timeline, ot)
    view = GetTLView(embeds)
    await ctx.respond(embed=embeds[0], ephemeral=(not show), view=view if len(embeds) > 1 else None)


# =============== List all TLs for a boss =============
@bot.slash_command(description="List TLs")
async def list_tls(
        ctx,
        boss: Option(int, "1 - 5", min_value=1, max_value=5),
        show: Option(bool, "Show this timeline to everyone", required=False, default=False),
        compact: Option(bool, "Show a compact version of the TL", required=False, default=False)):
    mobile = ctx.author.is_on_mobile()
    timelines = Timelines.get_single_boss_timelines_from_db(boss)

    view = View()
    timeline_descriptions = ''
    thumbnail_url = boss_image_urls[boss]
    boss_name = boss_names[boss]
    simple_tl_descriptions = []
    complex_tl_descriptions = []
    ot_tl_descriptions = []
    async def button_callback(interaction, timeline):
        embeds = get_display_embeds_mobile(timeline) if mobile or compact or timeline.simple else get_display_embeds2(timeline)
        view = GetTLView(embeds)
        await interaction.response.edit_message(embed=embeds[0], view=view if len(embeds) > 1 else None)

    d = {f'callback{k}': partial(button_callback, timeline=timelines[k]) for k in timelines}
    for id, tl in timelines.items():
        button = Button(label=id, style=discord.ButtonStyle.green)

        button.callback = d[f'callback{id}']
        view.add_item(button)
        unit_display = []
        for unit in tl.units:
            re_unit = clean_text(unit.name)
            if re_unit in icon_bank:
                unit_display.append(icon_bank[re_unit])
            else:
                unit_display.append(unit.name + ',')
        if 'T' in id:
            ot_tl_description = (f'{id}: ' +
                                  ' '.join(unit_display) +
                                  f' EV: {tl.ev.replace("*","")}' + '\n')
            ot_tl_descriptions.append(ot_tl_description)

        elif len(id) > 3:
            simple_tl_description = (f'{id}: ' +
                                      ' '.join(unit_display) +
                                      f' EV: {tl.ev.replace("*","")}' + '\n')
            simple_tl_descriptions.append(simple_tl_description)

        else:
            complex_tl_description = (f'{id}: ' +
                                      ' '.join(unit_display) +
                                      f' EV: {tl.ev.replace("*","")}' + '\n')
            complex_tl_descriptions.append(complex_tl_description)



    embed = discord.Embed(
        type="rich",
        color=0xffffff)
    embed.set_author(name=f'Timelines for boss {boss} - {boss_name}',
                     icon_url=f'{thumbnail_url}')
    display_helper(embed, complex_tl_descriptions, 'complex', boss)
    display_helper(embed, simple_tl_descriptions, 'simple', boss)
    display_helper(embed, ot_tl_descriptions, 'ot', boss)

    await ctx.respond(embed=embed, ephemeral=(not show), view=view)


def display_helper(embed, tl_descriptions, style, boss):
    counter = 0
    page = 0
    value = ''
    for tl in tl_descriptions:
        value += tl
        counter += 1
        if counter == 5:
            if page == 0:
                embed.add_field(
                    name='Manual Timelines' if style == 'complex' else
                         'Simple Timelines' if style == 'simple' else
                         'OT Timelines',
                    value=value,
                    inline=False
                )
                page += 1
            else:
                embed.add_field(
                    name='',
                    value=value,
                    inline=False
                )
            counter = 0
            value = ''
    if page == 0 and counter == 0:
        embed.add_field(
            name='Manual Timelines' if style == 'complex' else
                 'Simple Timelines' if style == 'simple' else
                 'OT Timelines',
            value=f'No manual timelines to display currently.\nPlease run \"/load_tls {boss}\" if you have written one recently.',
            inline=False
        )
    elif page == 0 and counter > 0:
        embed.add_field(
            name='Manual Timelines' if style == 'complex' else
                 'Simple Timelines' if style == 'simple' else
                 'OT Timelines',
            value=value,
            inline=False
        )
    elif counter > 0:
        embed.add_field(
            name='',
            value=value,
            inline=False
        )



# =============== Animation Cancel command =============
@bot.slash_command(guild_ids=guild_id, description="Gets animation cancel guide video on specified character.")
async def animation_cancel(
        ctx,
        character,
        show: Option(bool, "Show this to everyone", required=False, default=False)):

    character_cleaned = clean_text(character)
    closest_matches = difflib.get_close_matches(character_cleaned, names_bank.keys(), n=1)
    if len(closest_matches) == 0 or closest_matches[0] not in animation_bank:
        await ctx.respond(f'Animation cancel video with character "{character}" not found.', ephemeral=True)
        return
    closest_match = closest_matches[0]

    '''
    for i in range(len(animation_bank)):
        if animation_bank[i][0].lower() == character.lower():
            character = animation_bank[i][0]
            skill_num = len(animation_bank[i][1])
            for j in range(skill_num):
                works = True
                skill_data = str(animation_bank[i][1][j]).split(" ")
                
                if len(skill_data) > 2: 
                    skill_name_jp.append(f"{' '.join(skill_data[:-2])} - {skill_data[len(skill_data) - 2]}".strip())
                else:
                    skill_name_jp.append(f"{' '.join(skill_data[:-1])}".strip())
                skill_video.append(skill_data[len(skill_data) - 1].strip())
            break
    '''

    character = names_bank[closest_match]
    if closest_match in icon_bank:
        embed = discord.Embed(
            title=f"{icon_bank[closest_match]} Animation Cancel for {character} {icon_bank[closest_match]}",
            color=0xfffeff
        )
    else:
        embed = discord.Embed(title=f"Animation Cancel for {character}", color=0xfffeff)

    animations = animation_bank[closest_match]
    for animation in animations:
        split_idx = animation.find('https')
        youtube_url = animation[split_idx:]
        skill_description_jp = animation[:split_idx]
        skill_description_en = await translate_text(skill_description_jp)
        all_english = re.match("^[ ()A-Za-z0-9_-]*$", skill_description_en)

        embed.add_field(
            name=f'{skill_description_en}' if all_english else f'{skill_description_jp}',
            value=f"{youtube_url}",
            inline=False)

    await ctx.respond(embed=embed, ephemeral=(not show))


# =============== Show Animation Cancel Units command =============
@bot.slash_command(guild_ids=guild_id, 
                description="Displays all characters that have an animation cancel video available.")
async def animation_cancel_unit_names(ctx,show: Option(bool, "Show this to everyone", required=False, default=False)):
    embed = discord.Embed(
        title="Unit names with animation cancel",
        description="These names and nicknames can be used with the /animation_cancel command." + \
                    "For example, /animation_cancel neneka and /animation_cancel nnk will give the videos for neneka.",
        color=0xfffeff
    )
    results = []
    for i in animation_bank:
        results.append(i.capitalize())

    results.sort()
    results_string = ""
    name_count = 0
    names_in_each_column = len(results)//3
    field_limit = 1024

    for result in results:
        if len(results_string) + len(result) + 1 > field_limit or name_count + 1 > names_in_each_column:
            embed.add_field(
                name="",
                value=results_string,
                inline=True
            )
            results_string = f'{result}\n'
            name_count = 1
            continue

        results_string += f'{result}\n'
        name_count += 1

    embed.add_field(
        name="",
        value=results_string,
        inline=True
    )

    await ctx.respond(embed=embed, ephemeral=(not show))

    ''' embed = discord.Embed(title="Units With Animation Cancel", description="Unit Names With Animation Cancel",
                          color=0xfffeff)
    bad_names = []
    names_bank = animation_bank

    if True:
        for i in names_bank:
            if not any(i in j for j in translation_mapping):
                bad_names.append(i)
    else:
        bad_names = names_bank

    if len(bad_names) == 0:
        await ctx.respond("No characters with messed up names found.")

    bad_names = [bad_names[i:i + (len(bad_names) // 3)] for i in range(0, len(bad_names), len(bad_names) // 3)]
    print(bad_names)
    for i in range(3):
        if len(bad_names) == 4:
            print("hi")
            if len(bad_names[3]) > 1 and (i == 1):
                bad_names[i].append(bad_names[3][1])
            elif i == 0:
                bad_names[i].append(bad_names[3][0])
        embed.add_field(
            name="",
            value="\n".join(bad_names[i]),
            inline=True)

    await ctx.respond(embed=embed, ephemeral=(not show))'''


# =============== Homework Command =============
@bot.slash_command(guild_ids=guild_id, description="Evaluates homework for the clan")
async def evaluate_homework(ctx,
                            chorry: Option(bool, "Evaluate for Chorry instead of Worry", required=False, default=False)):
    await ctx.defer()
    embed = discord.Embed(
        title="Users with bad homework",
        description="Shame these slackers!",
        color=0xfffeff
    )
    homework = get_homework(chorry)
    display_string = ''
    any_conflicts = False
    for hw in homework:
        print(f'{hw.user}\n{hw.comp1}{hw.comp2}{hw.comp3}{hw.evaluate()}')
        hw_string = ''
        conflict = False
        conflicts = hw.evaluate()
        if all(conflicts.length_conflicts) and \
           all(conflicts.ev_conflicts) and \
           all(conflicts.borrow_conflicts) and \
           all(conflicts.tl_code_conflicts):
            conflict = True
            hw_string += f'HW not started!'
        else:
            for i in range(3):
                temp_string = ''
                length_conflict, tl_code_conflict, ev_conflict, borrow_conflict = False, False, False, False
                if conflicts.length_conflicts[i]:
                    hw_string += f'Team {i+1} missing units!\n'
                    temp_string += f'Team {i+1} missing units!\n'
                    length_conflict = True
                    conflict = True
                if conflicts.tl_code_conflicts[i]:
                    hw_string += f'Team {i+1} missing TL Code!\n'
                    temp_string += f'Team {i+1} missing TL Code!\n'
                    tl_code_conflict = True
                    conflict = True
                if conflicts.ev_conflicts[i]:
                    hw_string += f'Team {i+1} missing EV!\n'
                    temp_string += f'Team {i+1} missing EV!\n'
                    ev_conflict = True
                    conflict = True
                if conflicts.borrow_conflicts[i]:
                    hw_string += f'Team {i+1} missing borrow!\n'
                    temp_string += f'Team {i+1} missing borrow!\n'
                    borrow_conflict = True
                    conflict = True
                if conflicts.unit_conflicts[i]:
                    unit = clean_text(conflicts.unit_conflicts[i])
                    if unit in icon_bank:
                        unit = icon_bank[unit]
                    if i == 2:
                        hw_string += f'{unit} in Teams 1 and 3\n'
                    else:
                        hw_string += f'{unit} in Teams {(i + 1)%3} and {(i + 2)%3 if i + 2 != 3 else 3}\n'
                    conflict = True
        if conflict:
            any_conflicts = True
            embed.add_field(
                name=hw.user,
                value=hw_string,
                inline=True
            )

    if not any_conflicts:
        embed = discord.Embed(
            title="All users have completed their homework!  We are CB ready!",
            description="",
            color=0xfffeff
        )
    await ctx.respond(embed=embed)


# =============== Reload translations from woody translation sheet =============
@bot.slash_command(guild_ids=guild_id, description="Pulls the latest woody-grade translations")
@commands.has_role(1025780684574433390)
async def update_vocab_bank(ctx):
    global translation_mapping
    global animation_bank
    await ctx.defer()
    translation_mapping = sheets_helper.get_translation_mapping()
    animation_bank = sheets_helper.get_animation_videos()
    names_bank = sheets_helper.get_animation_videos_names_bank()
    await ctx.respond("Retrieved the latest woody-grade translations!", ephemeral=True)


@bot.slash_command(description="Load TLs")
async def load_tls(ctx, boss):
    acceptable_bosses = ['1', '2', '3', '4', '5', 'all']
    if boss not in acceptable_bosses:
        await ctx.respond(f"Invalid boss number! Please enter a number from 1-5 for boss.", ephemeral=True)
        return

    await ctx.defer()
    if boss == 'all':
        for i in range(1, 6):
            print(f"Loading for boss: {i}")
            Timelines.load_to_db(i, clear=True)
    else:
        Timelines.load_to_db(int(boss), clear=True)
    await ctx.respond(f"Loaded TLs for boss: {boss}", ephemeral=True)


# =============== Help command =============
@bot.slash_command(guild_ids=guild_id, description="Get a description of all commands")
async def help(ctx):
    embed = discord.Embed(title="Commands Help", color=0xfffeff)

    embed.add_field(
        name="/translate_tl - Translates a text file timeline with woody-grade technology",
        value="```tl: Attached file containing timeline" +
            "\nshow (Optional): Show this TL to everybody```",
        inline=False)

    embed.add_field(
        name="/get_tl - Gets the target TL with specified ID",
        value="```id: ID of the timeline; ex.'D10'" +
            "\not (Optional): Time in seconds of your OT" +
            "\nshow (Optional): Show this TL to everybody" +
            "\ncompact (Optional): Compacts the display```",
        inline=False)

    embed.add_field(
        name="/list_tls - Gets all Tls for a given boss",
        value="```boss: Boss that you want the TL from (1-5)" +
            "\nshow (Optional): Show the picked TL to everybody```",
        inline=False)
    
    embed.add_field(
        name="/animation_cancel - Displays animation cancel videos for given character",
        value="```character: Character you want the animation cancel videos for" + 
            "\nshow (Optional): Show the videos to everybody```",
        inline=False
    )
    
    embed.add_field(
        name="/animation_cancel_unit_names - Character names with animation cancel videos",
        value="```show (Optional): Show the list of units to everybody```",
        inline=False
    )

    embed.add_field(
        name="/load_tls - Makes the bot retrieve the latest udpates to TLs for a boss",
        value="```boss: Boss that you want the TL from (1-5)```",
        inline=False)

    embed.add_field(
        name="/update_vocab_bank - Refreshes woody-grade translations. (ADMIN ONLY)",
        value="",
        inline=False)

    embed.add_field(
        name="/evaluate_homework - Shames people who haven't done homework.",
        value="chorry (Optional): Get evaluation for chorry instead of worry",
        inline=False)

    await ctx.respond(embed=embed, ephemeral=True)

#load_to_db_thread = Thread(target=Timelines.background_load_to_db)
#load_to_db_thread.start()

keep_alive()
token = json.load(open("service_account.json"))['discord_token']
if os.environ['COMPUTERNAME'] == 'ZALTEO':
    token = json.load(open("service_account.json"))['discord_token_test']
bot.run(token)
