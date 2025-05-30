import Homework
#from keep_alive import keep_alive
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
from embed_helpers import get_display_embeds_compact, get_display_embeds, GetTLView, get_display_embeds2
from functools import partial
from clan_battle_info import get_boss_names, get_boss_urls, score_multipliers, get_time, sqlitedict_base_path
import clan_battle_info
import re
from icon_bank import icon_bank, clean_text
import difflib
from Homework import get_homework, convert_ev_to_float, get_roster, load_roster_from_sheets, save_homework
import time
from concurrent.futures import ThreadPoolExecutor
import datetime
from sqlitedict import SqliteDict
from time import sleep
from Users import (worry_users, chorry_users, borry_users, mark_fc, get_fc_status, reset_fc_dicts,
                   atc_start, atc_end, atc_status, reset_atc_dict, find_user_by_discord_id,
                   find_clan_by_discord_id, find_discord_id_by_priconne_id)
from Metrics import save_metric_from_context, unload_metrics
import asyncio

executor = ThreadPoolExecutor(2)

tabulate.PRESERVE_WHITESPACE = True

# Cache the translation mapping and animation bank
translation_mapping = sheets_helper.get_translation_mapping()
animation_bank = sheets_helper.get_animation_videos()
names_bank = sheets_helper.get_animation_videos_names_bank()

# Define our bot
guild_ids = {"Zalteo Test Server": 1002644143589302352,  # Zalteo Test Server
             "Worry/Chorry": 1025780100291112960,  # Worry/Chorry
             "Zalteo Icon Bank": 1166119511376793661,  # Zalteo Icon Bank
             "Startend": 805006358138585128  # Startend
             }  # Server ids
wc_guild_ids = {"Zalteo Test Server": 1002644143589302352,  # Zalteo Test Server
                "Worry/Chorry": 1025780100291112960,  # Worry/Chorry
                "Zalteo Icon Bank": 1166119511376793661,  # Zalteo Icon Bank
                }
channel_ids = {1002644143589302352:
                   {"super-private": 1067620591038889995,
                    "super-private-2": 1141152593683415060
                   },  # Zalteo Test Server Channels
               1166119511376793661:
                   {"general": 1176655969657303142,
                    "test": 1166119511376793664
                   },  # Zalteo Icon Bank Channels
               1025780100291112960:
                   {
                    #CB cooking channels
                    "editable-sheet-link": 1176707090677518396,
                    "transcribe-requests": 1258770676555448400,
                    "tl-testing-requests": 1258771428887625858,
                    "blue4-comp-finding": 1260617489235181631,
                    "d1-cooking": 1258771069884432456,
                    "d2-cooking": 1258771088993816587,
                    "d3-cooking": 1258771110368116746,
                    "d4-cooking": 1258771128634048573,
                    "d5-cooking": 1258771149265829898,
                    "overtime-cooking": 1258770854859247687,
                    "bc-tier-cooking": 1258770601292861491,

                    #Dining hall channels
                    "clan-battle-discussion": 1221363179464953856,
                    "event-bs-abyss-cooking": 1212636868500520980,
                    "dungeon-cooking": 1093831361804124190,
                    "deep-quest-cooking": 1149686008259022889,
                    "dq-support-begging": 1208177597838790677,
                    "jp-bot-spam": 1094596240274116608,

                    #Clan channels
                    "worry-chef-battle": 1025781394078715934,
                    "worry-boss-1": 1028582387019423784,
                    "worry-boss-2": 1028582408154521680,
                    "worry-boss-3": 1028582424252260372,
                    "worry-boss-4": 1028582442606547054,
                    "worry-boss-5": 1028582461984227511,
                    "worry-announcements": 1025781269411397662,
                    "chorry-clown-battle": 1025781436315336775,
                    "chorry-boss-1": 1056083088951738419,
                    "chorry-boss-2": 1056083142999552070,
                    "chorry-boss-3": 1056083194597867530,
                    "chorry-boss-4": 1056083259672498206,
                    "chorry-boss-5": 1056083315142164510,
                    "chorry-announcements": 1025781292031299604,
                    "discussion": 1131632662331805788,
                    "pudding-help": 1201988712901394543,
                    "clan-announcements": 1025782443388719205,
                    "borry-announcements": 1061314126346997820,
                    "borry-clown-battle": 1061314327719727265,
                    "borry-boss-1": 1063105615616024596,
                    "borry-boss-2": 1063105646553206805,
                    "borry-boss-3": 1063105674155937793,
                    "borry-boss-4": 1063105699342716928,
                    "borry-boss-5": 1063105727855611955,
                    "staff-chat": 1070337797736628224,
                    "leads-chat": 1102862545884303400,
                    "chorry-leads": 1146492866814824618,
                    "borry-leads": 1212991847652266004,
                    "clan-general": 1025780102694436956,

                    # Kitchen channels
                    "chefs-general": 1099083593222983700,
                    "cooking-blue4-guides": 1229137315826237470,
                    "kitchen-leadership": 1258800610808168608,
                    "kitchen-chinese": 1287035090475548724,
                    "deep-quest-simming": 1240668885729022082,
                    "guest-chef-request": 1207545815489454100,

                   },  # Worry/Chorry Channels
               805006358138585128:
                   {
                       "priconne-bot-commands": 850658639354396693,
                       "jp-cb-relaxing-room": 933032227376345148,
                       "pioneers-room": 1202729920883859486
                   }  # Startend Channels
               }  # Channel ids

background_scrape_channel_ids = \
    {
        1002644143589302352:
        {
            "super-private": 1067620591038889995,
            "super-private-2": 1141152593683415060
        },
        1025780100291112960:
        {
            "blue4-comp-finding": 1260617489235181631,
            "d1-cooking": 1258771069884432456,
            "d2-cooking": 1258771088993816587,
            "d3-cooking": 1258771110368116746,
            "d4-cooking": 1258771128634048573,
            "d5-cooking": 1258771149265829898,
            "overtime-cooking": 1258770854859247687,
            "bc-tier-cooking": 1258770601292861491,

            #Dining hall channels
            "clan-battle-discussion": 1221363179464953856,

            #Clan channels
            "worry-chef-battle": 1025781394078715934,
            "worry-boss-1": 1028582387019423784,
            "worry-boss-2": 1028582408154521680,
            "worry-boss-3": 1028582424252260372,
            "worry-boss-4": 1028582442606547054,
            "worry-boss-5": 1028582461984227511,
            "worry-announcements": 1025781269411397662,
            "chorry-clown-battle": 1025781436315336775,
            "chorry-boss-1": 1056083088951738419,
            "chorry-boss-2": 1056083142999552070,
            "chorry-boss-3": 1056083194597867530,
            "chorry-boss-4": 1056083259672498206,
            "chorry-boss-5": 1056083315142164510,
            "chorry-announcements": 1025781292031299604,
            "discussion": 1131632662331805788,
            "pudding-help": 1201988712901394543,
            "clan-announcements": 1025782443388719205,
            "borry-announcements": 1061314126346997820,
            "borry-clown-battle": 1061314327719727265,
            "borry-boss-1": 1063105615616024596,
            "borry-boss-2": 1063105646553206805,
            "borry-boss-3": 1063105674155937793,
            "borry-boss-4": 1063105699342716928,
            "borry-boss-5": 1063105727855611955,
            "staff-chat": 1070337797736628224,
            "leads-chat": 1102862545884303400,
            "chorry-leads": 1146492866814824618,
            "borry-leads": 1212991847652266004,

            # Kitchen channels
            "chefs-general": 1099083593222983700,
        }

    }
non_display_channel_ids = {"bot-dev": 1141149506021367849}
restricted_role_ids = [1200589687623004291, 1025781797696581754, 1025780684574433390]
bot = commands.Bot(command_prefix=commands.when_mentioned_or("."))


def is_allowed_channel(guild_id, channel_id):
    channel_ids_for_guild = channel_ids[guild_id].values()
    if channel_id not in channel_ids_for_guild and channel_id not in non_display_channel_ids.values():
        allowed_channels = ", ".join(channel_ids[guild_id].keys())
        return f"Please use this command in the guild cb channels"
    return None


def is_allowed_role(role_ids):
    for role_id in role_ids:
        if role_id in restricted_role_ids:
            return True
    return False


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
@bot.slash_command(guild_ids=guild_ids.values(), description="Translate TL")
async def translate_tl(
        ctx,
        tl: discord.Attachment,
        show: Option(bool, "Show this timeline to everyone", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
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
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    boss = int(id[1])
    mobile = ctx.author.is_on_mobile()
    print(mobile)
    #compact = False
    id = id.upper()

    timeline = Timelines.get_from_db(boss, id)
    if timeline is None:
        await ctx.respond(f"A timeline with that ID does not exist!\nPlease run \"/load_tls {boss}\" if you have written {id} recently.", ephemeral=True)
        return

    embeds = get_display_embeds_compact(timeline, ot) if mobile or compact or timeline.simple else get_display_embeds2(timeline, ot)
    view = GetTLView(embeds)
    await ctx.respond(embed=embeds[0], ephemeral=(not show), view=view if len(embeds) > 1 else None)


# =============== List all TLs for a boss =============
@bot.slash_command(description="List TLs")
async def list_tls(
        ctx,
        boss: Option(int, "1 - 5", min_value=1, max_value=5),
        show: Option(bool, "Show this timeline to everyone", required=False, default=False),
        compact: Option(bool, "Show a compact version of the TL", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    mobile = ctx.author.is_on_mobile()
    timelines = Timelines.get_single_boss_timelines_from_db(boss)

    view = View()
    timeline_descriptions = ''
    thumbnail_url = get_boss_urls()[boss-1]
    boss_name = get_boss_names()[boss-1]
    simple_tl_descriptions = []
    complex_tl_descriptions = []
    ot_tl_descriptions = []
    async def button_callback(interaction, timeline):
        embeds = get_display_embeds_compact(timeline) if mobile or compact or timeline.simple else get_display_embeds2(timeline)
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
@bot.slash_command(guild_ids=guild_ids.values(), description="Gets animation cancel guide video on specified character.")
async def animation_cancel(
        ctx,
        character,
        show: Option(bool, "Show this to everyone", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
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
    if len(animations) > 0 and animations[0] != '':
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
    else:
        embed.add_field(
            name=f'',
            value=f"Videos do not exist for this character yet!",
            inline=False)

    await ctx.respond(embed=embed, ephemeral=(not show))


# =============== Show Animation Cancel Units command =============
@bot.slash_command(guild_ids=guild_ids.values(),
                description="Displays all characters that have an animation cancel video available.")
async def animation_cancel_unit_names(ctx,show: Option(bool, "Show this to everyone", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    embed = discord.Embed(
        title="Unit names with animation cancel",
        description="These names and nicknames can be used with the /animation_cancel command." + \
                    "For example, /animation_cancel neneka and /animation_cancel nnk will give the videos for neneka.",
        color=0xfffeff
    )
    results = []
    for i in animation_bank:
        if len(animation_bank[i]) > 0 and animation_bank[i][0] != '':
            print(f'{i}: {animation_bank[i]}')
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


# =============== Homework Command =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Evaluates homework for the clan")
async def evaluate_homework(ctx,
                            clan: Option(str, "Clan", choices=['Worry', 'Chorry', 'Borry'], required=True)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    await ctx.defer()
    embed = discord.Embed(
        title="Users with bad homework",
        description="Shame these slackers!",
        color=0xfffeff
    )
    homework = get_homework(clan, cache=False)
    save_homework(clan)
    display_string = ''
    any_conflicts = False
    fields = 0
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
            fields += 1
            if fields >= 25:
                await ctx.respond("More than 25 members have not completed their homework. Please run this again when homework is closer to completion!")
                return

    if not any_conflicts:
        embed = discord.Embed(
            title="All users have completed their homework!  We are CB ready!",
            description="",
            color=0xfffeff
        )
    await ctx.respond(embed=embed)


# =============== Reload translations from woody translation sheet =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Pulls the latest woody-grade translations")
async def update_vocab_bank(ctx):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    global translation_mapping
    global animation_bank
    await ctx.defer()
    translation_mapping = sheets_helper.get_translation_mapping()
    animation_bank = sheets_helper.get_animation_videos()
    names_bank = sheets_helper.get_animation_videos_names_bank()
    await ctx.respond("Retrieved the latest woody-grade translations!", ephemeral=True)


# =============== Load TLs command =============
@bot.slash_command(description="Load TLs")
async def load_tls(ctx, boss):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    start_time = time.time()
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
    end_time = time.time()
    print(f'Total time to load: {end_time-start_time}')
    await ctx.respond(f"Loaded TLs for boss: {boss}", ephemeral=True)


def convert_to_roster_user(user):
    if user.lower() in worry_users:
        return worry_users[user.lower()].roster_name
    if user.lower() in chorry_users:
        return chorry_users[user.lower()].roster_name
    if user.lower() in borry_users:
        return borry_users[user.lower()].roster_name
    return user


def convert_to_hw_user(user):
    if user.lower() in worry_users:
        return worry_users[user.lower()].homework_name
    if user.lower() in chorry_users:
        return chorry_users[user.lower()].homework_name
    if user.lower() in borry_users:
        return borry_users[user.lower()].roster_name
    return user

'''
# =============== Recommend allocation command =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Recommends a three team allocation")
async def recommend_allocation(ctx, user,
        same_boss_alloc: Option(bool, "Allows an allocation with multiple comps for the same boss", required=False, default=False),
        boss_focus: Option(int, "Must include this boss in the allocation", min_value=1, max_value=5, required=False, default=None),
        manual: Option(bool, "Include manual TLs in this recommendation", required=False, default=True),
        show: Option(bool, "Show this recommendation to everyone", required=False, default=False)
        ):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    save_metric_from_context(ctx)
    embed = discord.Embed(
        title=f"Allocation recommendations for {user.capitalize()}",
        description="Eating pudding while doing homework leads to better results.",
        color=0xfffeff
    )
    start = time.time()
    user = convert_to_roster_user(user)
    homework = get_roster(user)
    time_for_roster_sheet = time.time()
    print(time_for_roster_sheet - start)
    if not homework or not homework.roster_box:
        await ctx.respond(f'Could not find a roster for user {user}. Please make sure you are matching your username on the roster sheet EXACTLY.', ephemeral=True)
        return

    max_allocs = homework.get_recommended_allocs(no_manual= not manual, boss_preference=boss_focus, same_boss_alloc=same_boss_alloc)
    time_for_allocs = time.time()
    print(time_for_allocs - time_for_roster_sheet)
    counter = 0
    print(max_allocs)
    for i in range(len(max_allocs)):
        alloc = max_allocs[i]
        boss_excluded = alloc[3]
        #if boss_focus and i == boss_focus:
        #    continue
        if not alloc or not alloc[1]:
            embed.add_field(
                name=f'Exclude Boss {i}',
                value='There are no possible allocations.',
                inline=False
            )
            continue
        comp_description = ""
        total_score = 0
        for comp in alloc[1]:
            total_score += convert_ev_to_float(comp.ev) * score_multipliers[comp.boss]
            unit_display = []
            for unit in comp.units:
                re_unit = clean_text(unit)
                if re_unit in icon_bank:
                    unit_display.append(icon_bank[re_unit])
                else:
                    unit_display.append(unit + ',')
            comp_description += (f'{comp.tl_code}: ' +
                                 ' '.join(unit_display) +
                                 f', EV: {comp.ev}')
            if comp.borrow:
                re_borrow = clean_text(comp.borrow)
                if re_borrow in icon_bank:
                    comp_description += (f', Borrow: {icon_bank[re_borrow]}\n')
                else:
                    comp_description += (f', Borrow: {re_borrow.capitalize()}\n')
            else:
                comp_description += '\n'

        comp_description += f'Total EV: {round(alloc[2], 2)}m, Total Score: {round(total_score, 2)}m'

        print(comp_description)
        embed.add_field(
            name="Max Damage Allocation" if not boss_excluded else f'Allocation Excluding Boss {boss_excluded}',
            value=comp_description,
            inline=False
        )
    await ctx.respond(embed=embed, ephemeral=not show)
'''

def get_score(hw):
    total_score = 0
    if hw.comp1:
        actual_comp = Timelines.get_from_db(hw.comp1.boss, hw.comp1.tl_code)
        total_score += convert_ev_to_float(actual_comp.ev) * score_multipliers[hw.comp1.boss]
    if hw.comp2:
        actual_comp = Timelines.get_from_db(hw.comp2.boss, hw.comp2.tl_code)
        total_score += convert_ev_to_float(actual_comp.ev) * score_multipliers[hw.comp2.boss]
    if hw.comp3:
        actual_comp = Timelines.get_from_db(hw.comp3.boss, hw.comp3.tl_code)
        total_score += convert_ev_to_float(actual_comp.ev) * score_multipliers[hw.comp3.boss]
    return total_score
'''
# =============== Change allocation command =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Recommends a three team allocation")
async def change_allocation(ctx,
        target_tl: Option(str, "Target TL you want to convert to"),
        same_boss_alloc: Option(bool, "Allows an allocation with multiple comps for the same boss", required=False, default=False),
        improve_score: Option(bool, "Only displays changes that improve score", required=False, default=False),
        chorry: Option(bool, "Change for Chorry instead of Worry", required=False, default=False),
        show: Option(bool, "Show this recommendation to everyone", required=False, default=False)
        ):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    #await ctx.defer()

    timeline = Timelines.get_from_db(target_tl[1], target_tl)
    if not timeline:
        await ctx.respond("Please put in a valid TL code for target TL", ephemeral=not show)
        return

    def getBaseEmbed():
        embed = discord.Embed(
            title=f"Users that can change their allocation to {target_tl}",
            description="Units could be un-built for this conversion!",
            color=0xfffeff
        )
        return embed

    embeds = [getBaseEmbed()]
    start = time.time()
    all_homework = get_homework(chorry, cache=True)
    #homework_time = time.time()
    #print(f'homework_time: {homework_time - start}')
    character_count = 0
    cur_embed_idx = 0
    for hw in all_homework:
        roster_user = convert_to_roster_user(hw.user)
        roster = get_roster(roster_user)
        current_score = get_score(hw)
        if not roster:
            continue
        hw.roster_box = roster.roster_box
        homework_time1 = time.time()
        #print(f'valid_alloc_time-1: {homework_time1 - start}')
        valid_allocs = hw.get_valid_converted_alloc(target_tl, same_boss_alloc=same_boss_alloc)
        homework_time2 = time.time()
        #print(f'valid_alloc_time: {homework_time2 - homework_time1}')
        if valid_allocs and len(valid_allocs) > 0:
            comp_description = ''
            for valid_alloc in valid_allocs:
                alloc = valid_alloc[1]
                if improve_score:
                    new_score = 0
                    for comp in alloc[1]:
                        new_score += convert_ev_to_float(comp.ev) * score_multipliers[comp.boss]
                    if new_score < current_score:
                        continue

                homework_time = time.time()
                #print(f'valid_alloc_time2: {homework_time - start}')
                convert_from = valid_alloc[0]
                boss = int(convert_from[1])
                timeline = Timelines.get_from_db(boss, convert_from)
                unit_display = []
                if not timeline:
                    continue

                for unit in timeline.units:
                    re_unit = clean_text(unit.name)
                    if re_unit in icon_bank:
                        unit_display.append(icon_bank[re_unit])
                    else:
                        unit_display.append(unit + ',')
                comp_description += (f'{convert_from}:' +
                                     ''.join(unit_display) + ' --> ')

                for comp in alloc[1]:
                    if comp.tl_code != target_tl:
                        continue
                    unit_display = []
                    for unit in comp.units:
                        re_unit = clean_text(unit)
                        if re_unit in icon_bank:
                            unit_display.append(icon_bank[re_unit])
                        else:
                            unit_display.append(unit + ',')
                    comp_description += (f'{comp.tl_code}:' +
                                         ''.join(unit_display))
                    if comp.borrow:
                        re_borrow = clean_text(comp.borrow)
                        if re_borrow in icon_bank:
                            comp_description += (f' Borrow: {icon_bank[re_borrow]}\n')
                        else:
                            comp_description += (f' Borrow: {re_borrow.capitalize()}\n')
                    else:
                        comp_description += '\n'
                    break
            if len(comp_description) > 0:
                name = f'Possible conversions for {hw.user}'
                if character_count + len(comp_description) + len(name) > 5800:
                    embeds.append(getBaseEmbed())
                    cur_embed_idx += 1
                    character_count = 0

                character_count += len(comp_description) + len(name)
                #print(character_count)
                embeds[cur_embed_idx].add_field(
                    name=f'Possible conversions for {hw.user}',
                    value=comp_description,
                    inline=False
                )

    view = GetTLView(embeds)
    end = time.time()
    print(f"Total time to calculate allocation changes: {end - start}")
    await ctx.respond(embed=embeds[0], ephemeral=(not show), view=view if len(embeds) > 1 else None)
    #print(all_possible_converters)


# =============== Load Roster command =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Load roster boxes for all members (EXPENSIVE operation PLEASE do NOT run more than once)")
async def load_roster(ctx, user,
                      chorry: Option(bool, "Load for Chorry instead of Worry", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)

    role_ids = [role.id for role in ctx.author.roles]
    if not is_allowed_role(role_ids):
        await ctx.respond("You must be an admin to be able to run this command!")
        return
    if user == 'reset' and ctx.author.id == 152242204826533889:
        load_roster_from_sheets('reset', chorry)
        await ctx.respond(f"Reset Roster, chorry: {chorry}", ephemeral=True)
        return
    start_time = time.time()
    await ctx.defer()
    load_roster_from_sheets(user, chorry)
    end_time = time.time()
    print(f'Total time to load: {end_time-start_time}')
    await ctx.respond(f"Loaded Rosters for {user}", ephemeral=True)
'''

@bot.slash_command(guild_ids=[1002644143589302352], description="Resets disband dict")
async def reset_disband(ctx):
    disband_dict = SqliteDict(sqlitedict_base_path + 'disband.sqlite', autocommit=True)
    disband_dict['count'] = 0
    disband_dict['disband_messages'] = []
    disband_dict['last_checked_time'] = {}
    await ctx.respond("Reset the disband dictionary")


# =============== Disband command =============
@bot.slash_command(guild_ids=[1002644143589302352, 1025780100291112960], description="Disband...")
async def disband(ctx):
    save_metric_from_context(ctx)
    #await ctx.defer()
    #await scrape_disband_messages()
    disband_dict = SqliteDict(sqlitedict_base_path + 'disband.sqlite', autocommit=True)
    #disband_dict['count'] = 0
    #disband_dict['disband_messages'] = []
    #disband_dict['last_checked_time'] = {}

    disband_messages_key = 'disband_messages'
    count_key = 'count'
    counter = 0
    disband_messages = []
    if count_key in disband_dict:
        counter = disband_dict[count_key]
    if disband_messages_key in disband_dict:
        disband_messages = disband_dict[disband_messages_key]

    color_code = 0x2E8B57
    disband_ending_message = ''
    if counter == 0:
        disband_ending_message = "We're safe! No disband this CB! <:PuddingSmile:1135860601365733386>"
    elif 0 < counter < 5:
        color_code = 0xffca4f
        disband_ending_message = "Ehhhhh, woody is probably joking. We're fine! <:BorryWeird:1063225784128508035>"
    elif 5 <= counter < 10:
        color_code = 0xf28f0c
        disband_ending_message = "We might've bbed a few times, but we can't possibly disband...right? <a:WorryDodgeFast:1026512767185854486>"
    else:
        color_code = 0xed5555
        disband_ending_message = "It's over. This is the worst thing to happen to Priconne since EN EOS. <:SadWorryDab:1083579383563952158>"

    title_text = f"<:Puddisgust:1026691405797675100> Woody tried disbanding the clan _{counter}_ times this CB. <:Puddisgust:1026691405797675100>"
    if counter == 1:
        title_text = f"<a:PuddingNom:1201481137806127178> Woody tried disbanding the clan _{counter}_ time this CB. <a:PuddingNom:1201481137806127178>"
    elif 0 <= counter < 5:
        title_text = f"<a:PuddingNom:1201481137806127178> Woody tried disbanding the clan _{counter}_ times this CB. <a:PuddingNom:1201481137806127178>"
    embed = discord.Embed(
        title=title_text,
        description=f'Disband threats in moderation are healthy for the clan.',
        color=color_code
    )

    if counter != 0:
        link_message_counter = 0
        disband_messages.reverse()
        disband_thread_message_links = ''
        for disband_message in disband_messages:
            link_message_counter += 1
            if len(disband_message) > 3:
                disband_thread_message_links += f'_"{disband_message[2]}"_\n\t - {disband_message[3]} \n Circa <t:{int(disband_message[0].timestamp())}:d>\n\n'
            else:
                disband_thread_message_links += f'_"{disband_message[2]}"_\n\t - Channel: {disband_message[1]} \n Circa <t:{int(disband_message[0].timestamp())}:d>\n\n'
            if link_message_counter == 3:
                break

        embed.add_field(
            name=f'Most recent attempts',
            value=f'{disband_thread_message_links}\n',
            inline=False
        )

    embed.add_field(
        name=f'{disband_ending_message}',
        value='',
        inline=False
    )
    await ctx.respond(embed=embed, ephemeral=False)

def get_fc_list(clan='Worry'):
    clan_name = "Worry" if clan=='Worry' else "Chorry" if clan=='Chorry' else "Borry"
    embed = discord.Embed(
        title=f'FC Status for {clan_name}',
        description='',
        color=0xfffeff
    )
    statuses = get_fc_status(clan)
    embed.add_field(
        name='',
        value=f'{statuses[0]}',
        inline=True
    )
    embed.add_field(
        name='',
        value=f'{statuses[1]}',
        inline=True
    )
    return embed

# =============== FC command =============
@bot.slash_command(guild_ids=wc_guild_ids.values(), description="Marks FC for user")
async def fc(ctx,
             user: Option(str, "Name of user to fc, or 'list' to see status", default=None)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    clan = find_clan_by_discord_id(str(ctx.author.id))
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    if user == 'reset' and ctx.author.id == 152242204826533889:
        reset_fc_dicts()
        await ctx.respond("Reset fc dictionaries")
        return
    elif user == 'list':
        embed = get_fc_list(clan)
        await ctx.respond(embed=embed, ephemeral=False)
    elif user == 'chorry':
        embed = get_fc_list('Chorry')
        await ctx.respond(embed=embed, ephemeral=False)
    elif user == 'worry':
        embed = get_fc_list('Worry')
        await ctx.respond(embed=embed, ephemeral=False)
    elif user == 'borry':
        embed = get_fc_list('Borry')
        await ctx.respond(embed=embed, ephemeral=False)
    elif not user:
        user = find_user_by_discord_id(ctx.author.id)
        status = mark_fc(user.priconne_id)
        status_display = icon_bank['checkmark'] if status[0] else icon_bank['redx']
        embed = discord.Embed(
            title=f'Updated FC status',
            description=f'',
            color=0xfffeff
        )
        embed.add_field(
            name=f'{user.display_name}: {status_display}',
            value='',
            inline=True
        )
        await ctx.respond(embed=embed, ephemeral=False)
    else:
        clan = ''
        if user.lower() in worry_users:
            clan = 'Worry'
        elif user.lower() in chorry_users:
            clan = 'Chorry'
        elif user.lower() in borry_users:
            clan = 'Borry'
        else:
            await ctx.respond("Could not find user!")
            return
        master_dict = worry_users if clan == 'Worry' else chorry_users if clan == 'Chorry' else borry_users
        actual_user = master_dict[user.lower()]
        status = mark_fc(actual_user.priconne_id)
        status_display = icon_bank['checkmark'] if status[0] else icon_bank['redx']
        embed = discord.Embed(
            title=f'Updated FC status',
            description=f'',
            color=0xfffeff
        )
        embed.add_field(
            name=f'{actual_user.display_name}: {status_display}',
            value='',
            inline=True
        )
        await ctx.respond(embed=embed, ephemeral=False)


# =============== ATC command =============
@bot.slash_command(guild_ids=wc_guild_ids.values(), description="Command to initiate/end piloting")
async def atc(ctx,
             action: Option(str, "Piloting action", choices=['Start', 'End', 'Status', 'Crash', 'Reset'], required=True),
             user: Option(str, "The target user you are piloting/ending pilot", required=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    save_metric_from_context(ctx)
    if action == 'Start':
        result = atc_start(ctx.author.id, user)
        if result == -1:
            await ctx.respond("Could not find target user!")
        elif result == -2:
            await ctx.respond(f'{user} is currently being piloted already.')
        else:
            if isinstance(result, int):
                await ctx.respond(
                    f'Flight departing: <@{ctx.author.id}> {icon_bank["departing"]}{icon_bank["departing"]}{icon_bank["departing"]} <@{result}>')
            else:
                await ctx.respond(
                    f'Flight departing: <@{ctx.author.id}> {icon_bank["departing"]}{icon_bank["departing"]}{icon_bank["departing"]} {result}')
    elif action == 'End':
        result = atc_end(ctx.author.id, user)
        if result == -1:
            await ctx.respond("Could not find target user or target user is not being piloted!")
        elif result == -2:
            await ctx.respond(f'Cannot end. Please have the current pilot end this pilot.')
        else:
            if isinstance(result, int):
                await ctx.respond(
                    f'Flight arriving: <@{ctx.author.id}> {icon_bank["arriving"]}{icon_bank["arriving"]}{icon_bank["arriving"]} <@{result}>')
            else:
                await ctx.respond(
                    f'Flight arriving: <@{ctx.author.id}> {icon_bank["arriving"]}{icon_bank["arriving"]}{icon_bank["arriving"]} {result}')
    elif action == 'Crash':
        result = atc_end(ctx.author.id, user, crash=True)
        if result == -1:
            await ctx.respond("Could not find target user or target user is not being piloted!")
        else:
            if isinstance(result, int):
                await ctx.respond(
                    f'Flight crashed: <@{ctx.author.id}> {icon_bank["boom"]}{icon_bank["arriving"]}{icon_bank["boom"]} <@{result}>')
            else:
                await ctx.respond(
                    f'Flight crashed: <@{ctx.author.id}> {icon_bank["boom"]}{icon_bank["arriving"]}{icon_bank["boom"]} {result}')
    elif action == 'Status':
        atc_statuses = atc_status()
        count = 0
        pilot_strings = []
        for id in atc_statuses:
            member = await bot.fetch_user(id)
            if not member:
                name = 'Unknown'
            else:
                name = member.name
            pilot_string = f'**Pilot: {name}**\n'
            for flight in atc_statuses[id]:
                pilot_string += f'{flight[0]} - {flight[1]}\n'
                count += 1
            pilot_strings.append(pilot_string)
        embed = discord.Embed(
            title=f'Currently in flight: {count}',
            description=f'',
            color=0xfffeff
        )
        for pilot_string in pilot_strings:
            embed.add_field(
                name="",
                value=pilot_string,
                inline=True
            )

        await ctx.respond(embed=embed)
    elif action == 'Reset':
        if ctx.author.id == 152242204826533889:
            reset_atc_dict()
            await ctx.respond("Reset atc statuses")
        else:
            await ctx.respond("You do not have permissions to reset all atc statuses")
    return

async def add_roles(clan, users, remove=True):
    if os.environ['COMPUTERNAME'] == 'ZALTEO' or os.environ['COMPUTERNAME'] == 'LAPTOP-RVEEJPKP':
        guild = bot.get_guild(1002644143589302352)
        test_roles = {
            1: guild.get_role(1242761532052602915),
            2: guild.get_role(1242761554810638378),
            3: guild.get_role(1242761567196418119),
            4: guild.get_role(1242761577376120892),
            5: guild.get_role(1242761591846469814)
        }
        boss_roles = test_roles
        all_roles = list(test_roles.values())
    else:
        guild = bot.get_guild(1025780100291112960)
        worry_boss_roles = {
            1: guild.get_role(1242759370396274768),
            2: guild.get_role(1242759476788858880),
            3: guild.get_role(1242759504735506503),
            4: guild.get_role(1242759524595666955),
            5: guild.get_role(1242759544560422942)
        }

        chorry_boss_roles = {
            1: guild.get_role(1242787138416676874),
            2: guild.get_role(1242787176421527562),
            3: guild.get_role(1242787190908518462),
            4: guild.get_role(1242787203864592445),
            5: guild.get_role(1242787214728106056)
        }

        borry_boss_roles = {
            1: guild.get_role(1298731987778928692),
            2: guild.get_role(1298732060772663389),
            3: guild.get_role(1298732179592974398),
            4: guild.get_role(1298732278272360620),
            5: guild.get_role(1298732281699237888)
        }
        all_roles = list(worry_boss_roles.values()) + list(chorry_boss_roles.values()) + list(borry_boss_roles.values())
        boss_roles = chorry_boss_roles if clan == 'Chorry' else worry_boss_roles if clan == 'Worry' else borry_boss_roles

    if users is not None and len(users) == 0:
        return
    users_lower = None
    if users:
        users_lower = [user.lower() for user in users]
    homework = get_homework(clan, cache=True)
    for hw in homework:
        if users_lower and hw and hw.user and hw.user.lower() not in users_lower:
            continue
        user_discord_id = find_discord_id_by_priconne_id(hw.id)
        if not user_discord_id:
            continue
        boss_roles_to_add = []
        #print(hw.comp1, hw.comp2, hw.comp3)
        print(f"Assigning boss roles for {hw.user}")
        if hw.comp1.tl_code:
            role = boss_roles[int(hw.comp1.tl_code[1])]
            boss_roles_to_add.append(role)
        if hw.comp2.tl_code:
            role = boss_roles[int(hw.comp2.tl_code[1])]
            boss_roles_to_add.append(role)
        if hw.comp3.tl_code:
            role = boss_roles[int(hw.comp3.tl_code[1])]
            boss_roles_to_add.append(role)
        member = guild.get_member(int(user_discord_id))
        if not member:
            try:
                member = await guild.fetch_member(int(user_discord_id))
            except Exception as e:
                print(e)
        if member:
            # Clean up old roles first
            if remove:
                await member.remove_roles(*all_roles)
            await member.add_roles(*boss_roles_to_add)


# =============== Assign roles command =============
@bot.slash_command(guild_ids=wc_guild_ids.values(), description="Command to assign roles for bosses")
async def assign_roles(ctx,
                       clan: Option(str, "Clan", choices=['Worry', 'Chorry', 'Borry'], required=True),
                       user: Option(str, "Assigns roles for specified user", required=False, default=False),
                       remove: Option(bool, "Remove roles", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return

    role_ids = [role.id for role in ctx.author.roles]
    if not user and not is_allowed_role(role_ids):
        await ctx.respond("You must be an admin to be able to run this command for all users!")
        return
    await ctx.defer()

    await add_roles(clan, [user] if user else None, remove)
    if not user:
        await ctx.followup.send(f"Assigned boss roles to all {clan} members.")
    else:
        await ctx.followup.send(f"Assigned boss roles to {user}.")

# =============== Assign roles command =============
@bot.slash_command(guild_ids=wc_guild_ids.values(), description="Command to remove all boss roles from users")
async def remove_roles(ctx,
                       chorry: Option(bool, "Remove roles for chorry members", required=False, default=False)):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
    role_ids = [role.id for role in ctx.author.roles]
    if not is_allowed_role(role_ids):
        await ctx.respond("You must be an admin to be able to run this command!")
        return
    await ctx.defer()
    worry_boss_roles = {
        1: ctx.guild.get_role(1242759370396274768),
        2: ctx.guild.get_role(1242759476788858880),
        3: ctx.guild.get_role(1242759504735506503),
        4: ctx.guild.get_role(1242759524595666955),
        5: ctx.guild.get_role(1242759544560422942)
    }

    chorry_boss_roles = {
        1: ctx.guild.get_role(1242787138416676874),
        2: ctx.guild.get_role(1242787176421527562),
        3: ctx.guild.get_role(1242787190908518462),
        4: ctx.guild.get_role(1242787203864592445),
        5: ctx.guild.get_role(1242787214728106056)
    }

    '''test_roles = {
        1: ctx.guild.get_role(1242761532052602915),
        2: ctx.guild.get_role(1242761554810638378),
        3: ctx.guild.get_role(1242761567196418119),
        4: ctx.guild.get_role(1242761577376120892),
        5: ctx.guild.get_role(1242761591846469814)
    }'''
    if not chorry:
        worry_homework = get_homework(False)
        for hw in worry_homework:
            user_discord_id = find_discord_id_by_priconne_id(hw.id)
            if not user_discord_id:
                continue
            member = ctx.guild.get_member(int(user_discord_id))
            if not member:
                member = await ctx.guild.fetch_member(int(user_discord_id))
            if member:
                all_roles = list(worry_boss_roles.values())
                await member.remove_roles(*all_roles)
    else:
        chorry_homework = get_homework(True)
        for hw in chorry_homework:
            user_discord_id = find_discord_id_by_priconne_id(hw.id)
            if not user_discord_id:
                continue
            member = ctx.guild.get_member(int(user_discord_id))
            if not member:
                member = await ctx.guild.fetch_member(int(user_discord_id))
            if member:
                all_roles = list(chorry_boss_roles.values())
                await member.remove_roles(*all_roles)
    await ctx.respond(f"Removed boss roles for all {'chorry' if chorry else 'worry'} members that are registered with roboninon")

# =============== Help command =============
@bot.slash_command(guild_ids=guild_ids.values(), description="Get a description of all commands")
async def help(ctx):
    message = is_allowed_channel(ctx.guild_id, ctx.channel_id)
    if message:
        await ctx.respond(message)
        return
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
        name="/load_tls - Makes the bot retrieve the latest updates to TLs for a boss",
        value="```boss: Boss that you want the TL from (1-5)```",
        inline=False)

    '''embed.add_field(
        name="/update_vocab_bank - Refreshes woody-grade translations. (ADMIN ONLY)",
        value="",
        inline=False)'''

    embed.add_field(
        name="/evaluate_homework - Shames people who haven't done homework.",
        value="```chorry (Optional): Get evaluation for chorry instead of worry```",
        inline=False)

    embed.add_field(
        name="/recommend_allocation - Recommends you a three team allocation for cb",
        value="```user: Your username, make sure this matches EXACTLY to the name on the roster sheet" +
            "\nmanual (Optional): Include manual TLs in your allocation" +
            "\nboss_focus (Optional): Guarantees this boss in your allocation```",
        inline=False)

    embed.add_field(
        name="/change_allocation - Finds all users who can change to a target TL",
        value="```user: Your username, make sure this matches EXACTLY to the name on the roster sheet" +
            "\ntarget_tl: TL that you want to convert to" +
            "\nchorry (Optional): Gets conversion for chorry instead of worry```",
        inline=False)

    embed.add_field(
        name="/fc - Marks a user's fc usage for the day",
        value="```user (Optional): Target user to mark fc. When empty, displays whole clan's status." +
            "\nchorry (Optional): Only used when user is empty to display chorry's fc status.```",
        inline=False)

    embed.add_field(
        name="/atc - Piloting commands",
        value="```action: Piloting action (start, end, status, crash)" +
            "\nchorry (Optional): Only used when action = status to display chorry's fc status.```",
        inline=False)

    '''embed.add_field(
        name="/load_roster - Loads a roster box from sheets",
        value="```user: Your username, make sure this matches EXACTLY to the name on the roster sheet" +
            "\nchorry (Optional): loads for chorry instead of worry```",
        inline=False)'''

    await ctx.respond(embed=embed, ephemeral=True)

async def scrape_disband_messages():
    disband_dict = SqliteDict(sqlitedict_base_path + 'disband.sqlite', autocommit=True)
    disband_messages_key = 'disband_messages'
    count_key = 'count'
    start_search_key = 'last_checked_time'

    #disband_dict[disband_messages_key] = []
    #disband_dict[start_search_key] = {}
    #disband_dict[count_key] = 0
    if count_key not in disband_dict:
        disband_dict[count_key] = 0
    if start_search_key not in disband_dict:
        disband_dict[start_search_key] = {}
    if disband_messages_key not in disband_dict:
        disband_dict[disband_messages_key] = []

    #1002644143589302352 - test-server
    #152242204826533889 - zalteo
    #1025780100291112960 - clan server
    #416540817168007189 - woody
    server_id = 1025780100291112960
    search_user_id = 416540817168007189
    if os.environ['COMPUTERNAME'] == 'ZALTEO' or os.environ['COMPUTERNAME'] == 'LAPTOP-RVEEJPKP':
        server_id = 1002644143589302352
        search_user_id = 152242204826533889

    start_search_times = disband_dict[start_search_key]
    counter = disband_dict[count_key]
    disband_messages = disband_dict[disband_messages_key]
    #print(f"current_counter: {counter}")

    excluded_channels = [1025781269411397662, 1025781292031299604, 1025782443388719205, 1201988712901394543,
                         1212991847652266004, 1146492866814824618, 1102862545884303400, 1070337797736628224]
    cb_start_time = get_time(True)
    cb_end_time = get_time(False)
    for channel_id in background_scrape_channel_ids[server_id].values():
        try:
            if channel_id in excluded_channels:
                continue
            #print(channel_id)
            channel = bot.get_channel(channel_id)
            start_search_time = cb_start_time
            search_limit = 1000
            if channel_id in start_search_times:
                start_search_time = start_search_times[channel_id]
                print(f"latest search time for channel {channel_id}: {start_search_times[channel_id]}")
            async for message in channel.history(limit=search_limit, after=start_search_time, oldest_first=True):
                if message.created_at > cb_end_time:
                    break
                if message.author.id == search_user_id and 'disband' in message.content.lower():
                    disband_messages.append((message.created_at, message.channel.name, message.content, message.jump_url))
                    counter += 1
                start_search_times[channel_id] = message.created_at
            if channel_id in start_search_times:
                print(f"latest search time for channel {channel_id}: {start_search_times[channel_id]}")
        except discord.errors.Forbidden:
            print(f"Could not access channel with id {channel_id}")

    #print(f"after search current_counter: {counter}")
    disband_messages = list(sorted(disband_messages, key=lambda x: x[0]))
    disband_dict[disband_messages_key] = disband_messages
    disband_dict[count_key] = counter
    disband_dict[start_search_key] = start_search_times


async def background_save_disband_messages():
    await bot.wait_until_ready()
    while True:
        print('Background scraping for disband messages')
        await scrape_disband_messages()
        print('Finished background scraping for disband messages')
        await asyncio.sleep(600)


'''------------------------------------------------------------------Personal server commands------------------------------------------------------------------'''
@bot.slash_command(guild_ids=[1002644143589302352], description="Uploads metrics to gsheets")
async def add_banned_tl(ctx, id):
    if id == 'reset':
        Homework.reset_banned_tls()
        await ctx.respond(f"Reset banned tls")
        return
    else:
        Homework.add_banned_tl(id)
    await ctx.respond(f"Added banned TL: {id}")


@bot.slash_command(guild_ids=[1002644143589302352], description="Uploads metrics to gsheets")
async def save_metrics(ctx):
    unload_metrics()
    await ctx.respond("Unloaded metrics to https://docs.google.com/spreadsheets/d/1G0oY2lQIAAVxDuFBQQSKYsREzqb31Q_t7CENUzdxyAQ")


@bot.slash_command(guild_ids=[1002644143589302352], description="Saves boss info")
async def save_boss_info(ctx, boss,
                         name: Option(str, required=False)):
    if name:
        clan_battle_info.save_boss_name(boss, name)
    await ctx.respond(f"Saved boss info!")


@bot.slash_command(guild_ids=[1002644143589302352], description="Saves boss thumbnail url")
async def save_sheet_info(ctx,
                          clan: Option(str, "Clan", choices=['Worry', 'Chorry', 'Borry'], required=True),
                          hw_sheet_id: Option(str, required=False),
                          sheet_id: Option(str, required=False)):
    if sheet_id:
        clan_battle_info.save_sheet_id(sheet_id)
        bosses_info = sheets_helper.get_bosses_info()
        for boss in bosses_info:
            boss_name = bosses_info[boss][0]
            clan_battle_info.boss_image_urls[boss_name] = bosses_info[boss][1]
            clan_battle_info.save_boss_name(boss, boss_name)
    if hw_sheet_id:
        clan_battle_info.save_homework_sheet_id(hw_sheet_id, clan)
        Homework.clear_cached_homework(clan)

    await ctx.respond(f"Saved sheet info!")

@bot.slash_command(guild_ids=[1002644143589302352], description="Saves Homework")
async def save_hw(ctx,
                  clan: Option(str, "Clan", choices=['Worry', 'Chorry', 'Borry'], required=True)):
    save_homework(clan)
    await ctx.respond(f"Saved homework")

@bot.slash_command(guild_ids=[1002644143589302352], description="Saves boss thumbnail url")
async def save_time(ctx,
                    start: Option(bool, required=True),
                    year: Option(int, required=True),
                    month: Option(int, required=True),
                    day: Option(int, required=True),
                    hour: Option(int, required=True)):
    clan_battle_info.save_time(year, month, day, hour, start)
    await ctx.respond(f"Saved cb time!")

@bot.slash_command(guild_ids=[1002644143589302352], description="Saves boss thumbnail url")
async def add_boss(ctx,
                    name: Option(str, required=True),
                    id: Option(str, required=True)):
    clan_battle_info.boss_image_urls[name] = f'https://redive.estertion.win/icon/unit/{id}.webp'
    await ctx.respond(f"Saved boss url!")

def create_dict_from_hw(hw):
    hw_dict = {}
    for homework in hw:
        hw_dict[homework.user] = homework
    return hw_dict

async def background_save_homework_and_roles():
    await bot.wait_until_ready()
    first_run = True
    while True:
        print('Background saving homework sheet for worry')
        cached_hw = create_dict_from_hw(get_homework(clan='Worry', cache=True))
        save_homework('Worry')
        new_hw = create_dict_from_hw(get_homework(clan='Worry', cache=True))
        to_add_roles = []
        for key in new_hw:
            if key not in cached_hw:
                to_add_roles.append(key.lower())
            else:
                if not cached_hw[key].compare(new_hw[key]):
                    to_add_roles.append(key.lower())
        print(to_add_roles)
        await add_roles('Worry', to_add_roles)
        await asyncio.sleep(120)

        print('Background saving homework sheet for chorry')
        cached_hw = create_dict_from_hw(get_homework(clan='Chorry', cache=True))
        save_homework('Chorry')
        new_hw = create_dict_from_hw(get_homework(clan='Chorry', cache=True))
        to_add_roles = []
        for key in new_hw:
            if key not in cached_hw:
                to_add_roles.append(key.lower())
            else:
                if not cached_hw[key].compare(new_hw[key]):
                    to_add_roles.append(key.lower())
        print(to_add_roles)
        await add_roles('Chorry', to_add_roles)
        await asyncio.sleep(120)

        print('Background saving homework sheet for borry')
        cached_hw = create_dict_from_hw(get_homework(clan='Borry', cache=True))
        save_homework('Borry')
        new_hw = create_dict_from_hw(get_homework(clan='Borry', cache=True))
        to_add_roles = []
        for key in new_hw:
            if key not in cached_hw:
                to_add_roles.append(key.lower())
            else:
                if not cached_hw[key].compare(new_hw[key]):
                    to_add_roles.append(key.lower())
        print(to_add_roles)
        await add_roles('Borry', to_add_roles)
        await asyncio.sleep(120)


#executor.submit(background_save_disband_messages)
#executor.submit(Timelines.background_load_tl)
#executor.submit(background_save_homework_and_roles)
loop = asyncio.get_event_loop()
loop.create_task(background_save_homework_and_roles())
loop.create_task(background_save_disband_messages())

#keep_alive()
token = json.load(open("service_account.json"))['discord_token']
if os.environ['COMPUTERNAME'] == 'ZALTEO' or os.environ['COMPUTERNAME'] == 'LAPTOP-RVEEJPKP':
    token = json.load(open("service_account.json"))['discord_token_test']
bot.run(token)
