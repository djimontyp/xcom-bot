from itertools import count

import discord
from discord import Interaction, ui
from discord.ui import Item

from src.core.config import settings
from src.core.enum import GameResult
from src.services.player import PlayerService


class ResultsButtons(discord.ui.View):
    def __init__(self, initiator_id: int, invited_id: int):
        super().__init__(timeout=None)

        self.initiator_id = initiator_id
        self.invited_id = invited_id

        self.result: dict[int, GameResult | None] = {
            initiator_id: None,
            invited_id: None,
        }

    def count_results(self, result: GameResult):
        return sum(1 for value in self.result.values() if value is not None and value == result)

    @discord.ui.button(label="Победа 0", style=discord.ButtonStyle.green, custom_id="win_callback")
    async def win_callback(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.win
        await self.process_result(interaction)

    @discord.ui.button(label="Поражение 0", style=discord.ButtonStyle.red, custom_id="lose_callback")
    async def lose_callback(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.lose
        await self.process_result(interaction)

    @discord.ui.button(label="Ничья 0", style=discord.ButtonStyle.grey, custom_id="draw_callback")
    async def draw_callback(self, button: ui.Button, interaction: Interaction):
        await interaction.response.defer()
        self.result[interaction.user.id] = GameResult.draw
        await self.process_result(interaction)

    async def process_result(self, interaction: Interaction):
        await self._update__buttons_labels(interaction)
        result_initiator = self.result[self.initiator_id]
        result_invited = self.result[self.invited_id]

        if all(self.result.values()):
            async with PlayerService(interaction=interaction) as service:
                match result_initiator, result_invited:
                    case GameResult.win, GameResult.lose:
                        async with service.session.begin():
                            await service.rate(self.initiator_id, self.invited_id)
                    case GameResult.lose, GameResult.win:
                        async with service.session.begin():
                            await service.rate(self.invited_id, self.initiator_id)
                    case GameResult.draw, GameResult.draw:
                        ...
                    case _:
                        raise ValueError(f"Парадоксальная комбинация: {result_initiator}, {result_invited}")

                self.stop()
                await interaction.channel.delete()

    async def _update__buttons_labels(self, interaction: Interaction):
        button_win = self.get_item("win_callback")
        button_lose = self.get_item("lose_callback")
        button_draw = self.get_item("draw_callback")
        button_win.label = f"{GameResult.win.value} {self.count_results(GameResult.win)}"
        button_lose.label = f"{GameResult.lose.value} {self.count_results(GameResult.lose)}"
        button_draw.label = f"{GameResult.draw.value} {self.count_results(GameResult.draw)}"
        self.clear_items()
        self.add_item(button_win)
        self.add_item(button_lose)
        self.add_item(button_draw)
        await interaction.message.edit(view=self)

    # View methods
    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id not in self.result:
            raise discord.errors.CheckFailure()
        return True

    async def on_error(self, error: Exception, item: Item, interaction: Interaction) -> None:
        if isinstance(error, discord.errors.CheckFailure):
            await interaction.response.send_message(
                "Вы не участвуете в сессии.", delete_after=settings.DELETE_AFTER, ephemeral=True
            )
        elif isinstance(error, ValueError):
            await interaction.followup.send(str(error), delete_after=settings.DELETE_AFTER)
        else:
            raise error
