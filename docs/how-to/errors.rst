.. SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

=============
Handle errors
=============

All calendaring-jmap errors extend :class:`~calendaring_jmap.error.JMAPBaseError`, and the JMAP-specific ones extend :class:`~calendaring_jmap.error.JMAPError`, which adds an ``error_type`` string. See :doc:`../explanation/design` for why the hierarchy is shaped this way.

Catch specific error types
==========================

.. code-block:: python

    from calendaring_jmap.error import (
        JMAPAuthError,
        JMAPCapabilityError,
        JMAPError,
        JMAPMethodError,
    )

    try:
        event_id, old_state, new_state = client.create_event(calendar_id, event)
    except JMAPAuthError:
        print("Authentication failed (401/403)")
    except JMAPCapabilityError:
        print("Server does not support urn:ietf:params:jmap:calendars")
    except JMAPMethodError as e:
        print(f"Server rejected the request: {e.error_type}, {e.reason}")
    except JMAPError as e:
        print(f"Protocol error: {e}")

See :doc:`../reference/errors` for what each error class means and the full list of JMAP method error types.

Malformed iCalendar input
=========================

``create_event``, ``send_invite``, and ``update_event`` take a JSCalendar dict directly and raise nothing client-side on a malformed one; whether a missing required property comes back as the server's own ``invalidProperties`` (surfaced as :class:`~calendaring_jmap.error.JMAPMethodError`) depends on the server and the property. Confirmed live that Cyrus rejects a create missing ``uid``/``start`` with ``invalidProperties``, while Stalwart accepts it, generating its own ``uid`` and leaving the event with no ``start`` at all rather than rejecting the request. ``JMAPMethodError.properties`` lists which properties an ``invalidProperties`` rejection actually named, when the server included that list, so you can tell a duplicate UID apart from an unrelated rejection sharing the same ``error_type``. The ``ValueError`` case below applies to ``ical_to_jscal`` itself, and so to ``JMAPCalendar.add_event``/``JMAPCalendarObject.save``, which call it on your behalf: if the iCalendar string is missing a mandatory property (``UID``, ``DTSTART``) or has a negative duration, conversion raises a plain ``ValueError`` before any request reaches the server. Catch it if you're constructing iCalendar strings by hand rather than passing through data a server already returned to you. ``create_event``/``send_invite`` raise the same exception type for an unrelated reason: passing ``calendar_id=None`` without the event's own ``calendarIds`` set.

.. code-block:: python

    try:
        event_id = cal.add_event(ical)
    except ValueError as e:
        print(f"Malformed iCalendar: {e}")
    except JMAPMethodError as e:
        print(f"Server rejected the request: {e.error_type}, {e.reason}")
