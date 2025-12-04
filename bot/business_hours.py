import logging
from dataclasses import dataclass
from datetime import datetime, time
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import disnake

from utils import get_message

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DayHours:
    start: time
    end: time

    def contains(self, current: time) -> bool:
        return self.start <= current < self.end


class BusinessHours:
    def __init__(self, config: Optional[dict] = None, tz_override: Optional[str] = None):
        self._config = config or get_message("messages.embeds.business_hours", return_raw=True)
        self._tz_override = tz_override

    def refresh(self) -> None:
        self._config = get_message("messages.embeds.business_hours", return_raw=True)

    def _timezone(self) -> ZoneInfo:
        tz_name = self._tz_override or self._config["timezone"]
        return ZoneInfo(tz_name)

    def _day_hours(self, weekday: int) -> Optional[DayHours]:
        day_cfg = self._config["hours"].get(weekday)
        if not day_cfg:
            return None

        try:
            start_h, start_m = map(int, day_cfg["from"].split(":"))
            end_h, end_m = map(int, day_cfg["to"].split(":"))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"Invalid hours config for weekday {weekday}") from exc

        start = time(start_h, start_m)
        end = time(end_h, end_m)

        if start >= end:
            raise ValueError(f"Start time must be before end time for weekday {weekday}")

        return DayHours(start=start, end=end)

    def is_operational(self, at: Optional[datetime] = None) -> bool:
        at = at or datetime.now(self._timezone())
        hours_for_day = self._day_hours(at.weekday())

        if hours_for_day is None:
            logger.debug("Business closed: no hours for weekday %s", at.weekday())
            return False

        inside = hours_for_day.contains(at.time())
        logger.debug(
            "Business hours check start=%s end=%s now=%s inside=%s",
            hours_for_day.start,
            hours_for_day.end,
            at.time(),
            inside,
        )
        return inside

    def is_outside(self, at: Optional[datetime] = None) -> bool:
        return not self.is_operational(at)

    def __str__(self) -> str:
        hours: dict = self._config["hours"]
        weekdays: list = self._config["weekdays"]
        lines = []

        for idx, weekday_name in enumerate(weekdays):
            info = hours.get(idx)
            if not info:
                lines.append(f"- {weekday_name}: {self._config['closed']}")
                continue
            lines.append(f"- {weekday_name}: {info['from']}–{info['to']}")

        return "\n".join(lines)

    async def send_warning(
        self,
        channel: disnake.TextChannel,
        *,
        description: Optional[str] = None,
        embed_kwargs: Optional[dict] = None,
    ):
        description = description or get_message(
            "messages.embeds.business_hours.description",
            context=str(self),
        )

        embed = disnake.Embed(
            title=get_message("messages.embeds.business_hours.title"),
            description=description,
            color=disnake.Color.dark_orange(),
            **(embed_kwargs or {}),
        )
        embed.set_image(url=self._config["image_url"])
        embed.set_footer(text=f"🕒 Timezone: {self._config['timezone']}")
        embed.timestamp = datetime.now(self._timezone())
        await channel.send(embed=embed)
