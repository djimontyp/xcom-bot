import discord
from discord import Interaction
from discord.ui import Item

from src.core import database
from src.core.enum import GameResult
from src.services.player import PlayerService


class ResultsButtons(discord.ui.View):
    def __init__(self, initiator_id: int, invited_id: int):
        super().__init__()
        self.initiator_id = initiator_id
        self.invited_id = invited_id

        self.result: dict[int, GameResult | str] = {
            initiator_id: "Ожидание результата...",
            invited_id: "Ожидание результата...",
        }

    @discord.ui.button(label="Победа", style=discord.ButtonStyle.green, custom_id="win_callback")
    async def win_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.win
        await self.calculate(interaction)

    @discord.ui.button(label="Поражение", style=discord.ButtonStyle.red, custom_id="lose_callback")
    async def lose_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.lose
        await self.calculate(interaction)

    @discord.ui.button(label="Ничья", style=discord.ButtonStyle.grey, custom_id="draw_callback")
    async def draw_callback(self, button: discord.ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.draw
        await self.calculate(interaction)

    async def calculate(self, interaction: Interaction):
        initiator, invited = database.players[self.initiator_id], database.players[self.invited_id]
        i_result, v_result = self.result[self.initiator_id], self.result[self.invited_id]

        if all(self.result.values()):
            match i_result, v_result:
                case GameResult.win, GameResult.lose:
                    PlayerService(initiator.id, invited.id).rate()
                case GameResult.lose, GameResult.win:
                    PlayerService(invited.id, initiator.id).rate()
                case GameResult.draw, GameResult.draw:
                    ...
                case _:
                    raise ValueError(f"Парадоксальная комбинация: {i_result}, {v_result}")
            print(f"Результаты сессии: {i_result} vs {v_result} для {initiator.mention} и {invited.mention}.")
            await interaction.response.edit_message(
                content=f"Результаты сессии: {i_result} vs {v_result} для {initiator.mention} и {invited.mention}.",
                view=None,
            )
        await interaction.channel.send(
            f"Обновлены результаты сессии:\n{initiator.mention} [{i_result}] vs {invited.mention} [{v_result}]\n\n",
        )

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id not in self.result:
            raise discord.errors.CheckFailure()
        return True

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(error, discord.errors.CheckFailure):
            await interaction.response.send_message("Вы не участвуете в сессии.", ephemeral=True)
