.. SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

================================
Convert iCalendar and JSCalendar
================================

``ical_to_jscal`` and ``jscal_to_ical`` are the same conversion functions :meth:`~calendaring_jmap.objects.calendar.JMAPCalendar.add_event` and :meth:`~calendaring_jmap.objects.calendar_object.JMAPCalendarObject.save` use internally, available directly if you want to convert between formats without making any JMAP request, or if you're calling :meth:`~calendaring_jmap.client.JMAPClient.create_event`/:meth:`~calendaring_jmap.client.JMAPClient.update_event` directly and starting from iCalendar rather than a JSCalendar dict.

.. code-block:: python

    from calendaring_jmap.convert import ical_to_jscal, jscal_to_ical

    jscal = ical_to_jscal(ical_str)
    ical_str_again = jscal_to_ical(jscal)

``ical_to_jscal`` processes the first VEVENT in the string; any sibling VEVENTs sharing the same UID with a RECURRENCE-ID are folded into the result's ``recurrenceOverrides`` map, and EXDATE lines become excluded override entries. Pass ``calendar_id`` if you need the result's own ``calendarIds`` set and aren't passing it straight to ``create_event``/``send_invite``, which set ``calendarIds`` themselves from their own ``calendar_id`` argument regardless of what the dict already has:

.. code-block:: python

    jscal = ical_to_jscal(ical_str, calendar_id=calendar_id)

Both functions raise ``ValueError`` on malformed input. ``add_event``/``save`` call ``ical_to_jscal``/``jscal_to_ical`` internally and surface the same errors; ``create_event``/``send_invite``/``update_event`` take a JSCalendar dict directly and raise nothing from this layer, since no conversion happens inside them. See :doc:`../explanation/design` for the conversion layer's own design decisions.
