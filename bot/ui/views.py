import discord
from discord import Interaction, ui
from discord.ext import commands

import settings
from utils import get_message

ticket_channels = get_message("channels")
class TicketReasonSelect(ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=field["reason"].capitalize(),
                description=get_message("messages.embeds.ticket_reason_select.option", reason=field["reason"]),
                emoji=field["icon"]
            )
            for field in get_message("channels")
        ]

        super().__init__(
            placeholder=get_message("messages.embeds.ticket_reason_select.placeholder"),
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: Interaction):
        from .modals import TicketModal
        reason_label = self.values[0]
        matched = next(
            (msg for msg in get_message("channels") if msg.get("reason", "").lower() == reason_label.lower()),
            None
        )
        target_channel_id = int(matched["id"])
        target_channel_icon = matched["icon"]
        await interaction.response.send_modal(TicketModal(reason_label, target_channel_id, target_channel_icon))


class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketReasonSelect())


class TicketControlView(ui.View):
    def __init__(self, channel, owner):
        super().__init__(timeout=None)
        self.channel = channel
        self.owner = owner
        
    @ui.button(label="Закрити тикет", style=discord.ButtonStyle.danger, custom_id="ticket_close")
    @commands.has_permissions(manage_messages=True)
    async def close_button(self, interaction: Interaction, button: ui.Button):
        await self.channel.delete()
            

    @ui.button(label="Перемістити тикет", style=discord.ButtonStyle.primary, custom_id="ticket_move")
    @commands.has_permissions(manage_messages=True)
    async def move_button(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message("Тикет переміщено", ephemeral=True)
