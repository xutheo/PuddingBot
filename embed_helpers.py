import discord
from discord.ui import Button, View
from icon_bank import icon_bank, clean_text

class GetTLView(View):
    embed_idx = 0

    def __init__(self, embeds):
        self.embeds = embeds
        super().__init__()

    @discord.ui.button(label="Back", row=0, style=discord.ButtonStyle.blurple)
    async def previous_button_callback(self, button, interaction):
        previous_embed = self.embeds[(self.embed_idx - 1) % len(self.embeds)]
        self.embed_idx -= 1
        await interaction.response.edit_message(embed=previous_embed, view=self)

    @discord.ui.button(label="Done", row=0, style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        current_embed = self.embeds[self.embed_idx % len(self.embeds)]
        await interaction.response.edit_message(embed=current_embed, view=None)

    @discord.ui.button(label="Next", row=0, style=discord.ButtonStyle.blurple)
    async def next_button_callback(self, button, interaction):
        previous_embed = self.embeds[(self.embed_idx + 1) % len(self.embeds)]
        self.embed_idx += 1
        await interaction.response.edit_message(embed=previous_embed, view=self)


def get_base_embed(timeline, include_units=True):
    description = f'Author: {timeline.author}\nTranscriber: {timeline.transcriber}\nEV: {timeline.ev}, ST_DEV: {timeline.st_dev}\nStyle: {timeline.style}'
    #if not timeline.simple:
    #    description += f'\nStatus: {timeline.status}'
    embed = discord.Embed(
        type="rich",
        description="",
        color=0xffffff)
    embed.set_author(name=f'{timeline.id} - {timeline.boss_name}',
                     url='https://docs.google.com/spreadsheets/d/1Zytb-0_ln6WARlCgn3opy-lfnuUr76x83iBNpUnu5wE/edit#gid=' +
                         str(timeline.sheet_id) + '&range=' + chr(timeline.starting_cell_tuple[1] + 64) + str(timeline.starting_cell_tuple[0]),
                     icon_url=f'{timeline.thumbnail_url}')
    unit_string = ''
    for unit in timeline.units:
        unit_cleaned = clean_text(unit.name)
        unit_string += f'{icon_bank[unit_cleaned]} ' if unit_cleaned in icon_bank else f'{unit.name}: '
        unit_string += f'LV{unit.level} | R{unit.rank} | {unit.star}⭐ | UE: {unit.ue}\n' if unit.ue \
            else f'LV{unit.level} | R{unit.rank} | {unit.star}⭐\n'

    if include_units:
        embed.add_field(
            name="Units",
            value=f"{unit_string}",
            inline=True
        )
        embed.add_field(
            name="Description",
            value=f"{description}",
            inline=True
        )
        embed.add_field(
            name='',
            value='',
            inline=False
        )
    return embed


def get_display_embeds(timeline):
    embeds = [get_base_embed(timeline)]
    embed_idx = 0
    embed_limit = 1012
    current_char = 0
    unit_first_total_line_limit = 55  # Dynamic calculation needed when unit column is present
    total_line_limit = 54  # Dynamic calculation needed when unit column is present
    max_time_length = max([len(x[0]) for x in timeline.tl_actions])
    max_unit_length = max([len(x[1]) for x in timeline.tl_actions])
    line_limit = total_line_limit - max_time_length - 4  # Limit of characters per line in the action description embed
    if timeline.unit_column:
        line_limit = unit_first_total_line_limit - max([len(x[1]) for x in timeline.tl_actions]) - max_time_length + 1
    #print("line_limit: " + str(line_limit))

    flex_string = ''  # Either set status column or unit column
    time_string = ''
    action_string = ''

    def get_number_of_extra_lines(text):
        #print(text)
        if len(text) <= line_limit:
            return 0
        line_split = text.split("\n")
        extra_lines = len(line_split) - 1
        print(line_split)
        for line in line_split:
            char_count = 0
            action_split = line.split(" ")
            for act in action_split:
                if len(act) + char_count > line_limit:
                    print("line break: " + act)
                    extra_lines += 1
                    char_count = 0
                char_count += len(act) + 1
        return extra_lines

    for i in range(0, len(timeline.tl_actions)):
        action = timeline.tl_actions[i]
        action_description = action[1] if not timeline.unit_column else action[2]
        flex = action[2] if not timeline.unit_column else action[1]
        number_of_extra_lines = get_number_of_extra_lines(action_description)
        if current_char + len(action_description) + line_limit - 4 >= embed_limit:
            time_string = '\n\n' + time_string # For some reason the first two lines of this string gets cut off in the below embed
            flex_string = '\n\n' + flex_string # For some reason the first two lines of this string gets cut off in the below embed
            action_string = '\n\n' + action_string # For some reason the first two lines of this string gets cut off in the below embed
            embeds[embed_idx].add_field(
                name="Time",
                value=f"```{time_string}```",
                inline=True)
            embeds[embed_idx].add_field(
                name="Unit" if timeline.unit_column else "Action Description",
                value=f"```{action_string if not timeline.unit_column else flex_string}```",
                inline=True)
            embeds[embed_idx].add_field(
                name="Action Description" if timeline.unit_column else "Set Status",
                value=f"```{flex_string if not timeline.unit_column else action_string}```",
                inline=True)
            #print("actual length: " + str(len(f"```{flex_string if not timeline.unit_column else action_string}```")))
            flex_string = ''
            time_string = ''
            action_string = ''
            current_char = 0
            embed_idx += 1
            embeds.append(get_base_embed(timeline))

        time_string += action[0] + (number_of_extra_lines + 1) * "\n"
        flex_string += flex + (number_of_extra_lines + 1) * "\n"
        action_string += action_description + '\n'
        current_char += len(action_description) + 1
        if i != len(timeline.tl_actions) - 1 and len(timeline.tl_actions[i+1][0]) != 0:
            action_string += '-' * (line_limit - 5) + "\n"
            time_string += '-' * max_time_length + "\n"
            flex_string += '-' * min(14, max_unit_length) + "\n" if timeline.unit_column else '-' * 5 + "\n"
            current_char += line_limit - 4
        #print("current_char: " + str(current_char) + " action_string_length: " + str(len(action_string)))

    time_string = '\n\n' + time_string  # For some reason the first two lines of this string gets cut off in the below embed
    flex_string = '\n\n' + flex_string  # For some reason the first two lines of this string gets cut off in the below embed
    action_string = '\n\n' + action_string  # For some reason the first two lines of this string gets cut off in the below embed
    embeds[embed_idx].add_field(
        name="Time",
        value=f"```{time_string}```",
        inline=True)
    embeds[embed_idx].add_field(
        name="Unit" if timeline.unit_column else "Action Description",
        value=f"```{action_string if not timeline.unit_column else flex_string}```",
        inline=True)
    embeds[embed_idx].add_field(
        name="Action Description" if timeline.unit_column else "Set Status",
        value=f"```{flex_string if not timeline.unit_column else action_string}```",
        inline=True)

    for i in range(0, len(embeds)):
        embeds[i].set_footer(text=f'Page {i + 1}/{len(embeds)}')
    return embeds

def get_display_embeds2(timeline, ot):
    embed_string = ''
    embeds = [get_base_embed(timeline)]
    embed_idx = 0
    embed_limit = 1000
    action_string = ''
    time = ''
    field_limit = 25
    fields = 0
    first_field = True
    zipped_status = zip(timeline.units, timeline.starting_set_status[1:6])
    auto_state = timeline.starting_set_status[7]
    statuses = []
    unit_statuses = []
    for status in zipped_status:
        unit_statuses.append(icon_bank[clean_text(status[0].name)])
        statuses.append(f'{icon_bank["greeno"] if status[1] == "SET" else ":x:"}')
    embeds[embed_idx].add_field(
        name='Initial Set Status',
        value=f'{"".join(unit_statuses)}\n{"".join(statuses)}\nAUTO: {auto_state}',
        inline=False)
    for i in range(0, len(timeline.tl_actions)):
        if i == 0:
            fields = 3
            action = timeline.tl_actions[i]
            time = action[0]
            time = convert_time_with_ot(ot, time)
            if time == "-1":
                time = ''
                break
            action_description = action[1] if timeline.simple or not timeline.unit_column else action[2]
            flex = ''
            if not timeline.simple:
                flex = action[2] if not timeline.unit_column else action[1]
            if action_description and flex:
                action_string += f'{action_description}\n' if timeline.simple or not timeline.unit_column else f'{flex} -> {action_description}\n'
            elif flex and not action_description:
                action_string += f'' if timeline.simple or not timeline.unit_column else f'{flex}\n'
            continue

        action = timeline.tl_actions[i]
        new_time = action[0]
        new_time = convert_time_with_ot(ot, new_time)
        if new_time == "-1":
            new_time = ''
            break
        # print(embed_string)
        if new_time:
            if len(time) > 8 or 'route' in time.lower():
                embeds[embed_idx].add_field(
                    name=f'**# {time} #**',
                    value='',
                    inline=False)
                fields += 1
                first_field = True
            else:
                if first_field:
                    embeds[embed_idx].add_field(
                        name="Time",
                        value=f"```{time}```",
                        inline=True)
                    embeds[embed_idx].add_field(
                        name="Action",
                        value=f"```{action_string}```",
                        inline=True)
                    embeds[embed_idx].add_field(
                        name='',
                        value='',
                        inline=True)
                    action_string = ''
                    first_field = False
                    fields += 3
                else:
                    embeds[embed_idx].add_field(
                        name='',
                        value=f"```{time}```",
                        inline=True)
                    embeds[embed_idx].add_field(
                        name='',
                        value=f"```{action_string}```",
                        inline=True)
                    embeds[embed_idx].add_field(
                        name='',
                        value='',
                        inline=True)
                    action_string = ''
                    fields += 3
            time = new_time
            if fields + 3 > field_limit:
                embeds.append(get_base_embed(timeline, include_units=False))
                first_field = True
                embed_idx += 1
                fields = 0


        action_description = action[1] if timeline.simple or not timeline.unit_column else action[2]
        flex = ''
        if not timeline.simple:
            flex = action[2] if not timeline.unit_column else action[1]

        if action_description and flex:
            action_string += f'{action_description}\n' if timeline.simple or not timeline.unit_column else f'{flex} -> {action_description}\n'
        elif flex and not action_description:
            action_string += f'' if timeline.simple or not timeline.unit_column else f'{flex}\n'

        '''if len(embed_string) + len(action[0]) + len(action_description) + len(flex) + 6 > embed_limit:
            embeds[embed_idx].add_field(
                name="Timeline",
                value=f"```{embed_string}```",
                inline=True)
            # print("actual length: " + str(len(f"```{embed_string}```")))
            embed_string = ''
            embed_idx += 1
            embeds.append(get_base_embed(timeline))

        if len(time) + len(action_description) + len(flex) != 0:
            string_begin = f'{time}: ' if len(time) > 0 else ''
            embed_string += string_begin + f'{action_description}\n' if timeline.simple or not timeline.unit_column else string_begin + f'{flex} -> {action_description}\n'
        '''

    '''embeds[embed_idx].add_field(
        name="Timeline",
        value=f"```{embed_string}```",
        inline=True)'''

    if first_field:
        embeds[embed_idx].add_field(
            name="Time",
            value=f"```{time}```",
            inline=True)
        embeds[embed_idx].add_field(
            name="Action",
            value=f"```{action_string}```",
            inline=True)
        embeds[embed_idx].add_field(
            name='',
            value='',
            inline=True)
        action_string = ''
        first_field = False
    else:
        embeds[embed_idx].add_field(
            name='',
            value=f"```{time}```",
            inline=True)
        embeds[embed_idx].add_field(
            name='',
            value=f"```{action_string}```",
            inline=True)
        embeds[embed_idx].add_field(
            name='',
            value='',
            inline=True)
        action_string = ''
    for i in range(0, len(embeds)):
        embeds[i].set_footer(text=f'Page {i + 1}/{len(embeds)}')
    return embeds


def get_display_embeds_mobile(timeline, ot):
    embed_string = ''
    embeds = [get_base_embed(timeline)]
    embed_idx = 0
    embed_limit = 1000
    for i in range(0, len(timeline.tl_actions)):
        action = timeline.tl_actions[i]
        time = action[0]
        time = convert_time_with_ot(ot, time)
        if time == "-1":
            break
        action_description = action[1] if timeline.simple or not timeline.unit_column else action[2]
        flex = ''
        if not timeline.simple:
            flex = action[2] if not timeline.unit_column else action[1]
        #print(embed_string)
        if len(embed_string) + len(time) + len(action_description) + len(flex) + 6 > embed_limit:
            embeds[embed_idx].add_field(
                name="Timeline",
                value=f"```{embed_string}```",
                inline=True)
            #print("actual length: " + str(len(f"```{embed_string}```")))
            embed_string = ''
            embed_idx += 1
            embeds.append(get_base_embed(timeline))

        if len(action[0]) + len(action_description) + len(flex) != 0:
            string_begin = f'{time} - ' if len(time) > 0 else ''
            embed_string += string_begin + f'{action_description}\n' if timeline.simple or not timeline.unit_column else string_begin + f'{flex} -> {action_description}\n'

    embeds[embed_idx].add_field(
        name="Timeline",
        value=f"```{embed_string}```",
        inline=True)
    for i in range(0, len(embeds)):
        embeds[i].set_footer(text=f'Page {i + 1}/{len(embeds)}')
    return embeds


def convert_time_to_seconds(time_string):
    time_split = time_string.split(':')
    time_in_seconds = 0
    if len(time_split) == 2:
        time_in_seconds += 60 * int(time_split[0]) + int(time_split[1])
    else:
        time_in_seconds += int(time_split[0])
    return time_in_seconds


def convert_time_to_string(time_in_seconds):
    minutes = time_in_seconds // 60
    seconds = time_in_seconds % 60
    if minutes == 0:
        return str(seconds)
    else:
        if seconds < 10:
            return str(minutes) + ":0" + str(seconds)
        else:
            return str(minutes) + ":" + str(seconds)


def convert_time_with_ot(ot, time):
    if ot and len(time) > 0:
        if ot > 90 or ot < 0:
            ot = 90
        offset = 90 - ot
        time_in_seconds = convert_time_to_seconds(time)
        if time_in_seconds - offset <= 0:
            return "-1"
        time = convert_time_to_string(time_in_seconds - offset)
        return time
    return time