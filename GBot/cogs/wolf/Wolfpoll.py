from discord.ext.ui import View, Message, Select, SelectOption
import nextcord
from typing import List


class Wolf_Execution_Poll(View):
    def __init__(self, client: nextcord.Client, player_ids: List[int]):
        super().__init__(client.loop)
        self.client = client
        self.poll = {}
        self.player_ids = player_ids

    async def select_animal(
            self,
            interaction: nextcord.Interaction,
            selected: List[nextcord.SelectOption]) -> None:
        for i in selected:
            self.poll[i.value] += 1
        await interaction.response.send_message("投票結果: {}".format(self.poll))

    async def create_option_list(self) -> List[SelectOption]:
        option_list = []
        for i in len(self.player_ids):
            option_list.append(self.client.get_user(self.player_ids[i]).name)
        return option_list

    async def select_user(
            self,
            interaction: nextcord.Interaction,
            selected: List[nextcord.SelectOption]) -> None:
        for i in selected:
            self.poll[i.value] = 1
        if len(self.poll) == self.player_ids:
            await interaction.response.send_message("投票結果: {}".format(selected))

    async def body(self):
        await Message("投票を開始します。", components=[
            [
                Select().options(
                    await self.create_option_list()
                ).on_select(self.select_user)
            ]
        ]
        )
