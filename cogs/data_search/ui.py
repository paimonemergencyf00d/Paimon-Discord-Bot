import discord


class SearchResultsDropdown(discord.ui.Select):

    def __init__(self, titles: list[str], embeds: list[discord.Embed]):
        self.embeds = embeds
        options = [
            discord.SelectOption(label=title, value=str(i)) for i, title in enumerate(titles)
        ]
        super().__init__(options=options)

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        await interaction.response.edit_message(embed=self.embeds[index])
