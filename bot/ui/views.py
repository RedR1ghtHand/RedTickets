import disnake
from disnake import Interaction, ui

from utils import get_message

ticket_channels = get_message("channels")


class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="Create Ticket",
        style=disnake.ButtonStyle.success,
        custom_id="ticket_create_button",
    )
    async def create_ticket_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        from .modals import TicketModal

        await interaction.response.send_modal(TicketModal())

class ChangeReasonSelect(ui.Select):
    def __init__(self, current_category_id: str):
        self.current_category_id = current_category_id
        options = [
            disnake.SelectOption(
                label=field["reason"].capitalize(),
                description=get_message("messages.embeds.ticket_reason_select.option", reason=field["reason"]),
                emoji=field["icon"]
            )
            for field in get_message("channels") if field["id"] != current_category_id
        ]

        super().__init__(
            placeholder="Please, choose new ticket reason...",
            options=options,
            min_values=1,
            max_values=1,
            custom_id="change_reason_select"
        )

    async def callback(self, interaction: Interaction):
        from .modals import ChangeReasonModal
        await interaction.response.send_modal(
            ChangeReasonModal(current_category_id=self.current_category_id)
        )

class ChangeReasonView(ui.View):
    def __init__(self, current_category_id):
        super().__init__(timeout=None)
        self.add_item(ChangeReasonSelect(current_category_id=current_category_id))
class ConfirmCloseView(ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @ui.button(
        label="Confirm",
        style=disnake.ButtonStyle.red,
        custom_id="ticket_close_confirm",
    )
    async def confirm_close(self, button: ui.Button, interaction: disnake.MessageInteraction):
        await interaction.channel.delete(reason=f"Ticket closed by user{interaction.user.name}")


class TicketControlView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @ui.button(
        label=get_message("messages.buttons.close_ticket"),
        style=disnake.ButtonStyle.danger,
        custom_id="ticket_close",
    )
    async def close_ticket_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        if interaction.channel.permissions_for(interaction.user).manage_messages:
            await interaction.response.send_message(
                "Please, confirm closing this ticket",
                view=ConfirmCloseView(),
                ephemeral=True,
                delete_after=30,
            )
        else:
            await interaction.response.send_message(
                get_message("messages.buttons.close_ticket_no_permission"),
                ephemeral=True,
            )

    @ui.button(
        label=get_message("messages.buttons.move_ticket"),
        style=disnake.ButtonStyle.primary,
        custom_id="ticket_move",
    )
    async def move_ticket_button(self, button: ui.Button, interaction: disnake.MessageInteraction):
        if not interaction.channel.permissions_for(interaction.user).manage_messages:
            return await interaction.response.send_message(
                get_message("messages.buttons.move_ticket_no_permission"),
                ephemeral=True,
            )

        if not interaction.message.mentions:
            return await interaction.response.send_message(
                "❗ No ticket creator mention found in the ticket message.",
                ephemeral=True,
            )

        ticket_creator: disnake.Member = interaction.message.mentions[0]
        current_category_id = interaction.channel.category_id

        from .modals import ChangeReasonModal

        await interaction.response.send_modal(
            ChangeReasonModal(
                current_category_id=str(current_category_id),
                ticket_creator=ticket_creator
            )
        )

