import logging
from datetime import datetime

import discord
from discord import Interaction, PermissionOverwrite, TextStyle, ui

import settings
from utils import get_message

from .views import TicketControlView


class TicketModal(ui.Modal):
    def __init__(self, reason_label: str, category_id: int, category_icon: str):
        super().__init__(title=get_message("messages.modals.create_ticket.title", reason=reason_label))
        self.reason_label = reason_label
        self.category_id = category_id
        self.category_icon = category_icon

        self.name = ui.TextInput(label=get_message("messages.modals.create_ticket.label_name"), required=True)
        self.data = ui.TextInput(label=get_message("messages.modals.create_ticket.label_data"), required=False)
        self.description = ui.TextInput(
            label=get_message("messages.modals.create_ticket.label_desc"),
            style=TextStyle.paragraph,
            placeholder=get_message("messages.modals.create_ticket.placeholder_desc"),
            required=True,
            min_length=int(get_message("messages.modals.create_ticket.desc_min_length")),
            max_length=int(get_message("messages.modals.create_ticket.desc_max_length"))
        )

        self.add_item(self.name)
        self.add_item(self.data)
        self.add_item(self.description)

    async def on_submit(self, interaction: Interaction):
        guild = interaction.guild
        category = guild.get_channel(int(self.category_id))

        if not category or not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                "Ticket category not found!", ephemeral=True
            )
            return

        channel = await category.create_text_channel(
            name=get_message(
                "messages.embeds.ticket_created.name", 
                icon=self.category_icon, 
                name=self.name.value.lower().replace(' ', '-')
            ),
            topic=get_message(
                "messages.embeds.ticket_created.topic", 
                reason=self.reason_label,
                user=interaction.user.name,
                date=datetime.now().strftime('%d-%m-%Y %H:%M')
            ),
            overwrites={
                guild.default_role: PermissionOverwrite(view_channel=False),
                interaction.user: PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
                guild.me: PermissionOverwrite(view_channel=True, send_messages=True),
            },
        )

        color = getattr(discord.Color, get_message("messages.embeds.ticket_created.color"))()
        embed = discord.Embed(
            title=get_message(
                "messages.embeds.ticket_created.title", 
                reason=self.reason_label
            ),
            description=get_message(
                "messages.embeds.ticket_created.description", 
                name=self.name.value,
                time=self.data.value or '-',
                desc=self.description.value
            ),
            color=color,
        )

        await channel.send(
            content=get_message(
                "messages.embeds.ticket_created.mention", 
                user=interaction.user.mention
            ), 
            embed=embed, 
            view=TicketControlView(channel, interaction.user)
        )
        await interaction.response.send_message(
            get_message(
                "messages.embeds.ticket_created.channel_mention", 
                channel=channel.mention
            ), ephemeral=True
        )

