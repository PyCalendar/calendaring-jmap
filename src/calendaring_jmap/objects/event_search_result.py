# SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Paged ``CalendarEvent/query`` result.

Carries a page of events alongside the ``CalendarEvent/query`` response's
own paging fields (:rfc:`8620#section-5.5`), so a caller doing a full
listing can detect truncation instead of treating a short page as complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from calendaring_jmap.objects.calendar_object import JMAPCalendarObject


@dataclass
class EventSearchResult:
    """One page of :meth:`~calendaring_jmap.client.JMAPClient.search_events` results.

    Attributes:
        events: Events matching this page, in server-returned order.
        position: Zero-based index of the first event in ``events`` within
            the complete result set (:rfc:`8620#section-5.5`).
        total: Total number of events matching the server-side filter
            (``calendar_id``/``start``/``end``/``text``) across every page,
            or ``None`` if the caller didn't request it. Set only when the
            caller's own ``calculate_total`` was true, never inferred from
            whether the server's response happened to include a ``total``
            field: confirmed live that Cyrus returns ``total``
            unconditionally, even when ``calculateTotal`` was never sent,
            which :rfc:`8620#section-5.5` says the server "MUST" omit in
            that case. Does not account for
            ``has_attachment``/``participant_email``/``participation_status``/
            ``participant_role``, which filter client-side after the
            server's own count is taken: a search combining one of those
            with ``calculate_total=True`` gets back a ``total`` that can be
            larger than the number of events actually returned across every
            page once the client-side filter is applied.
    """

    events: list[JMAPCalendarObject] = field(default_factory=list)
    position: int = 0
    total: int | None = None
