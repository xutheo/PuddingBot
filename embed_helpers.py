import discord
from discord.ui import Button, View


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


def get_base_embed(timeline, mobile):
    embed = discord.Embed(
        type="rich",
        description=f'Author: {timeline.author}\nTranscriber: {timeline.transcriber}\nEV: {timeline.ev}\nST_DEV: {timeline.st_dev}\nStyle: {timeline.style}\nStatus: {timeline.status}',
        color=0xffffff)
    embed.set_author(name=f'{timeline.id} - {timeline.boss_name}',
                     url='https://docs.google.com/spreadsheets/d/1Zytb-0_ln6WARlCgn3opy-lfnuUr76x83iBNpUnu5wE/edit#gid=' +
                         str(timeline.sheet_id) + '&range=' + chr(timeline.starting_cell_tuple[1] + 64) + str(timeline.starting_cell_tuple[0]),
                     icon_url=f'{timeline.thumbnail_url}')
    unit_string = ''
    for unit in timeline.units:
        unit_string += f'{unit.name}:LV{unit.level}/R{unit.rank}/{unit.star}⭐/UE:{unit.ue}\n'

    embed.add_field(
        name="Units",
        value=f"```{unit_string}```",
        inline=False
    )
    return embed


def get_display_embeds(timeline):
    embeds = [get_base_embed(timeline, False)]
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
            embeds.append(get_base_embed(timeline, False))

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


def get_display_embeds_mobile(timeline):
    embed_string = ''
    embeds = [get_base_embed(timeline, True)]
    embed_idx = 0
    embed_limit = 1000

    for i in range(0, len(timeline.tl_actions)):
        action = timeline.tl_actions[i]
        action_description = action[1] if not timeline.unit_column else action[2]
        flex = action[2] if not timeline.unit_column else action[1]
        #print(embed_string)
        if len(embed_string) + len(action[0]) + len(action_description) + len(flex) + 6 > embed_limit:
            embeds[embed_idx].add_field(
                name="Timeline",
                value=f"```{embed_string}```",
                inline=True)
            #print("actual length: " + str(len(f"```{embed_string}```")))
            embed_string = ''
            embed_idx += 1
            embeds.append(get_base_embed(timeline, True))

        if len(action[0]) + len(action_description) + len(flex) != 0:
            string_begin = f'{action[0]}: ' if len(action[0]) > 0 else ''
            embed_string += string_begin + f'{action_description}\n' if not timeline.unit_column else string_begin + f'{flex} -> {action_description}\n'

    embeds[embed_idx].add_field(
        name="Timeline",
        value=f"```{embed_string}```",
        inline=True)
    for i in range(0, len(embeds)):
        embeds[i].set_footer(text=f'Page {i + 1}/{len(embeds)}')
    return embeds