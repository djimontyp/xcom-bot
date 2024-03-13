import discord
from discord import Interaction


class Confirm(discord.ui.View):
    def __init__(self, initiator: int, invited: int):
        super().__init__()
        self.value = None
        self.initiator = initiator
        self.invited = invited

    @discord.ui.button(label="Подтвердить", style=discord.ButtonStyle.green)
    async def confirm_callback(self, button: discord.ui.Button, interaction: Interaction):
        self.disable_all_items()
        await interaction.response.send_message("Подтверждено", ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel_callback(self, button: discord.ui.Button, interaction: Interaction):
        self.disable_all_items()

        await interaction.response.send_message("Отменено", ephemeral=True)
        self.value = False
        self.stop()

    async def on_timeout(self) -> None:
        self.disable_all_items()
