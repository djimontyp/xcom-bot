from typing import Literal

import discord
from discord import Embed

from src import database


class RolesService:
    not_set = "Не установлена"

    def __init__(self):
        self.roles = database.roles

    def get_role(self, ctx, role_name: Literal["neofit", "adept", "master"]):
        return discord.utils.get(ctx.guild.roles, id=self.roles[role_name])

    @property
    def neofit(self):
        if role := self.roles["neofit"]:
            return self._role_to_mention(role)

    @property
    def adept(self):
        if role := self.roles["adept"]:
            return self._role_to_mention(role)

    @property
    def master(self):
        if role := self.roles["master"]:
            return self._role_to_mention(role)

    def update(self, **kwargs):
        self.roles.update(**kwargs)

    @staticmethod
    def _role_to_mention(role_id: int):
        return f"<@&{role_id}>"

    def get_embed(self, text: str = "Роли"):
        embed = Embed(title=text)
        embed.add_field(name="Неофит", value=self.neofit or self.not_set)
        embed.add_field(name="Адепт", value=self.adept or self.not_set)
        embed.add_field(name="Мастер", value=self.master or self.not_set)
        return embed
