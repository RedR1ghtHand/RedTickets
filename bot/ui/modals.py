from datetime import datetime
from typing import Optional

import disnake
from disnake import ModalInteraction, TextInputStyle, mentions, ui, user
from disnake.ui.select import mentionable

from bot import BusinessHours
from utils import get_message

from .views import TicketControlView


class TicketModal(ui.Modal):
    def __init__(
        self,
        *,
        business_hours: Optional[BusinessHours] = None,
    ):

        channels_config = get_message("channels")
        select_options = [
            disnake.SelectOption(
                label=field["reason"].capitalize(),
                value=str(field["id"]),
                description=get_message(
                    "messages.embeds.ticket_reason_select.option", reason=field["reason"]
                ),
                emoji=field["icon"],
            )
            for field in channels_config
        ]

        reason_placeholder = get_message("messages.modals.create_ticket.placeholder_reason")
        reason_label_text = get_message("messages.modals.create_ticket.label_reason")

        self.reason_select = ui.StringSelect(
            custom_id="ticket_reason_id_value",
            placeholder=reason_placeholder,
            min_values=1,
            max_values=1,
            options=select_options,
        )

        self.name = ui.TextInput(
            label=get_message("messages.modals.create_ticket.label_name"),
            custom_id="ticket_name",
            required=True,
        )
        self.data = ui.TextInput(
            label=get_message("messages.modals.create_ticket.label_data"),
            custom_id="ticket_data",
            required=False,
        )
        self.description = ui.TextInput(
            label=get_message("messages.modals.create_ticket.label_desc"),
            style=TextInputStyle.paragraph,
            placeholder=get_message("messages.modals.create_ticket.placeholder_desc"),
            custom_id="ticket_description",
            required=True,
            min_length=int(get_message("messages.modals.create_ticket.desc_min_length")),
            max_length=int(get_message("messages.modals.create_ticket.desc_max_length")),
        )

        components = [
            ui.Label(
                text=reason_label_text,
                component=self.reason_select,
            ),
            self.name,
            self.data,
            self.description,
        ]

        super().__init__(
            title=get_message(
                "messages.modals.create_ticket.title",
                reason=get_message("messages.embeds.ticket_reason_select.title"),
            ),
            components=components,
        )

        self.channels_config = channels_config
        self.business_hours = business_hours or BusinessHours()

    async def callback(self, interaction: ModalInteraction):
        guild = interaction.guild

        selected_reason = (
            interaction.values["ticket_reason_id_value"][0] if interaction.values else None
        )

        if selected_reason is None:
            await interaction.response.send_message(
                "You must choose a ticket reason.", ephemeral=True
            )
            return
        
        target_channel = next(
            (ch for ch in self.channels_config if str(ch["id"]) == selected_reason),
            None,
        )

        if not target_channel:
            await interaction.response.send_message(
                "Selected ticket reason is invalid.", ephemeral=True
            )
            return

        category = guild.get_channel(int(target_channel["id"]))

        name_value = interaction.text_values.get(self.name.custom_id) or ""
        data_value = interaction.text_values.get(self.data.custom_id) or ""
        desc_value = interaction.text_values.get(self.description.custom_id) or ""

        if not category or not isinstance(category, disnake.CategoryChannel):
            await interaction.response.send_message(
                "Ticket category not found!", ephemeral=True
            )
            return

        channel = await category.create_text_channel(
            name=get_message(
                "messages.embeds.ticket_created.name",
                icon=target_channel["icon"],
                name=name_value.lower().replace(" ", "-") or "ticket",
            ),
            topic=get_message(
                "messages.embeds.ticket_created.topic",
                reason=target_channel["reason"],
                user=interaction.user.name,
                date=datetime.now().strftime("%d-%m-%Y %H:%M"),
            ),
        )

        await channel.set_permissions(target=interaction.user, view_channel=True)

        color = getattr(disnake.Color, get_message("messages.embeds.ticket_created.color"))()
        embed = disnake.Embed(
            title=get_message(
                "messages.embeds.ticket_created.title",
                reason=target_channel["reason"],
            ),
            description=get_message(
                "messages.embeds.ticket_created.description",
                name=name_value or "-",
                time=data_value or "-",
                desc=desc_value or "-",
            ),
            color=color,
        )

        await channel.send(
            content=get_message(
                "messages.embeds.ticket_created.mention",
                user=interaction.user.mention,
            ),
            embed=embed,
            view=TicketControlView(),
        )

        if self.business_hours.is_outside():
            await self.business_hours.send_warning(channel=channel)

        await interaction.response.send_message(
            get_message(
                "messages.embeds.ticket_created.channel_mention",
                channel=channel.mention,
            ),
            ephemeral=True,
            delete_after=60,
        )

class ChangeReasonModal(ui.Modal):
    def __init__(
        self,
        *,
        current_category_id: str,
        timeout: Optional[float] = 600,
        custom_id: str = "change_reason_select",
        ticket_creator: disnake.Member,
    ) -> None:
        self.current_category = current_category_id
        self.channels_config = get_message("channels")
        self.ticket_creator = ticket_creator

        select_options = [
            disnake.SelectOption(
                label=field["reason"].capitalize(),
                value=str(field["id"]),
                description=get_message("messages.embeds.ticket_reason_select.option", reason=field["reason"]),
                emoji=field["icon"]
            )
            for field in get_message("channels") if field["id"] != current_category_id
        ]
        self.reason_select = ui.StringSelect(
            custom_id="change_reason_select_value",
            placeholder="Select new ticket reason...",
            min_values=1,
            max_values=1,
            options=select_options,
        )

        components = [
            ui.Label(
                text="New ticket reason",
                component=self.reason_select,
            )
        ]

        super().__init__(
            title="Change ticket reason",
            components=components,
            custom_id=custom_id,
            timeout=timeout,
        )

    async def callback(self, interaction: ModalInteraction):
        new_reason_ctx = next(
            (ch for ch in self.channels_config if str(ch["id"]) == interaction.values["change_reason_select_value"][0]),
            None,
        )

        if new_reason_ctx is None:
            await interaction.response.send_message(
                "You must choose a new ticket reason.", ephemeral=True
            )
            return

        guild = interaction.guild
        new_category = guild.get_channel(int(new_reason_ctx["id"])) if guild else None

        if not new_category or not isinstance(new_category, disnake.CategoryChannel):
            await interaction.response.send_message(
                "Could not find the selected ticket category.", ephemeral=True
            )
            return
        
        await interaction.channel.move(
            category=new_category,
            end=True,
            sync_permissions=True,
        )
        
        await interaction.channel.set_permissions(target=self.ticket_creator, view_channel=True)

        await interaction.channel.edit(name=get_message("messages.embeds.ticket_moved.name", new=new_reason_ctx["icon"], old=interaction.channel.name))

        color = getattr(disnake.Color, get_message("messages.embeds.ticket_moved.color"))()
        embed = disnake.Embed(
            title=get_message("messages.embeds.ticket_moved.title"),
            description=get_message(
                "messages.embeds.ticket_moved.description",
                creator=self.ticket_creator.display_name,
                moder=interaction.user.display_name
            ),
            color=color,
        )
        await interaction.response.send_message(f"@here!", embed=embed)
          