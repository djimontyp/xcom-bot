import discord
from discord import Embed

import src.core.utils
from src.core import database
from src.core.enum import Rank


class RolesService:
    not_set = "Не установлена"

    def __init__(self):
        self.roles = src.core.utils.roles_ids__mapper

    def get_role(self, ctx, role_name: Rank):
        return discord.utils.get(src.core.utils.roles_ids__mapper, id=self.roles[role_name])

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

    @property
    def officer(self):
        if role := self.roles["officer"]:
            return self._role_to_mention(role)

    @property
    def archon(self):
        if role := self.roles["archon"]:
            return self._role_to_mention(role)

    @property
    def ethereal(self):
        if role := self.roles["ethereal"]:
            return self._role_to_mention(role)

    def update(self, **kwargs):
        self.roles.update(**kwargs)

    @staticmethod
    def _role_to_mention(role_id: int):
        return f"<@&{role_id}>"

    def get_embed(self, text: str = "Роли"):
        embed = Embed(title=text)
        embed.add_field(name=Rank.neofit, value=self.neofit or self.not_set)
        embed.add_field(name=Rank.adept, value=self.adept or self.not_set)
        embed.add_field(name=Rank.officer, value=self.officer or self.not_set)
        embed.add_field(name=Rank.master, value=self.master or self.not_set)
        embed.add_field(name=Rank.archon, value=self.archon or self.not_set)
        embed.add_field(name=Rank.ethereal, value=self.ethereal or self.not_set)

        return embed
