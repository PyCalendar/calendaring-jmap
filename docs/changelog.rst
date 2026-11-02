.. SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

==========
Change log
==========

.. meta::
   :description: Every release of calendaring-jmap, newest first, with what changed in each one.

Every calendaring-jmap release, newest first: new features, bug fixes, breaking changes, and documentation updates, each with the pull request that shipped it.

.. py:currentmodule:: calendaring_jmap

.. Do *NOT* add new change log entries to this file.
   Instead create a file in the news directory.
   See CONTRIBUTING.md for the change log entry format.

.. towncrier release notes start

2.0.0 (2026-11-02)
------------------

Breaking changes
~~~~~~~~~~~~~~~~

- ``create_event``, ``send_invite``, and ``update_event`` now take a JSCalendar dict instead of an iCalendar string. ``JMAPCalendar.add_event`` and ``JMAPCalendarObject.save`` are unaffected: they still take and produce iCalendar strings. (`#67 <https://github.com/pycalendar/calendaring-jmap/issues/67>`_)
- ``create_event`` and ``send_invite`` now return a 3-tuple ``(event_id, old_state, new_state)`` instead of just the event id. (`#67 <https://github.com/pycalendar/calendaring-jmap/issues/67>`_)
- ``update_event`` now returns ``(old_state, new_state)`` instead of ``None``. (`#67 <https://github.com/pycalendar/calendaring-jmap/issues/67>`_)
- ``get_objects_by_sync_token`` and ``get_tasks_by_sync_token`` now return a 6-tuple ``(added, modified, deleted, old_state, new_state, has_more_changes)`` instead of a 4-tuple, and no longer raise when the server truncates a page (``hasMoreChanges: true``). Call the method again with ``new_state`` to fetch the next page. (`#69 <https://github.com/pycalendar/calendaring-jmap/issues/69>`_)
- Dropped Python 3.10 support. ``requires-python`` is now ``>=3.11``.
- ``delete_event`` now returns ``(old_state, new_state)`` instead of ``None``, matching ``create_event``/``update_event``. Both Cyrus and Stalwart already send this on every destroy; it was just being discarded.
- ``requests`` is no longer a hard dependency. ``niquests`` is used by default and remains required; ``requests`` is only needed as a fallback if ``niquests`` isn't installed, and is now its own extra: ``pip install calendaring-jmap[requests]``.
- ``search_events`` now accepts ``position``, ``limit``, and ``calculate_total`` for paging through large result sets, and returns an ``EventSearchResult`` instead of a bare list. Use ``.events`` for the matching events.


New features
~~~~~~~~~~~~

- Added calendar management: ``create_calendar``, ``update_calendar``, ``delete_calendar``, ``share_calendar``, ``get_calendar_subscriptions``, and ``set_default_alerts`` on both ``JMAPClient`` and ``AsyncJMAPClient``. (`#11 <https://github.com/pycalendar/calendaring-jmap/issues/11>`_)
- ``get_calendars`` and the event methods now take an ``account_id`` parameter to work with a calendar another user has shared with you. (`#11 <https://github.com/pycalendar/calendaring-jmap/issues/11>`_)
- Added scheduling: ``accept_invitation``, ``decline_invitation``, ``tentatively_accept``, and ``send_invite`` on both ``JMAPClient`` and ``AsyncJMAPClient``. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- ``delete_event`` can now send an iTIP CANCEL to participants via a new ``send_scheduling_messages`` argument. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- Added ``get_availability`` on both ``JMAPClient`` and ``AsyncJMAPClient``, returning busy intervals for one or more accounts over a time period. Falls back to a ``CalendarEvent/query`` scan when ``Principal/getAvailability`` isn't supported. Checking someone else's availability by email is not supported yet. (`#13 <https://github.com/pycalendar/calendaring-jmap/issues/13>`_)
- Added ``upload_attachment``, ``download_attachment``, ``attach_to_event``, and ``get_event_attachments`` on both ``JMAPClient`` and ``AsyncJMAPClient``, for uploading binary data as a JMAP blob and attaching it to a calendar event. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- ``Session`` now parses ``uploadUrl``/``downloadUrl`` from the JMAP session object, resolving a relative or mismatched-scheme URL the same way ``apiUrl`` already was. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- ``ical_to_jscal``/``jscal_to_ical`` now convert the iCalendar ``ATTACH`` property to and from the JSCalendar ``links`` property, for both URI and inline binary forms. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- Added ``get_address_books`` and ``search_contacts`` on both ``JMAPClient`` and ``AsyncJMAPClient``, for resolving contact information (e.g. participant emails) via JMAP Contacts. ``get_address_books`` returns an empty list with a logged warning, instead of raising, when Contacts isn't supported. (`#15 <https://github.com/pycalendar/calendaring-jmap/issues/15>`_)
- Added ``subscribe_push``, ``confirm_push_verification``, ``renew_push``, and ``unsubscribe_push`` on both ``JMAPClient`` and ``AsyncJMAPClient``, for JMAP push subscriptions (:rfc:`8620#section-7.2`). The subscription's callback URL must be HTTPS and publicly reachable by the server; this will not work behind localhost without tunneling. (`#16 <https://github.com/pycalendar/calendaring-jmap/issues/16>`_)
- Added ``has_attachment``, ``participant_email``, ``participation_status``, and ``participant_role`` filters to ``search_events`` on both ``JMAPClient`` and ``AsyncJMAPClient``, plus ``JMAPCalendar.search``. None of these have a matching ``FilterCondition`` property, so they filter client-side against the events the server's existing filters already matched, not on the server. (`#17 <https://github.com/pycalendar/calendaring-jmap/issues/17>`_)
- Added ``get_task_sync_token``, ``get_tasks_by_sync_token``, and ``search_tasks`` to both ``JMAPClient`` and ``AsyncJMAPClient``. ``search_tasks``'s ``due_before``, ``due_after``, and ``progress`` filters have no matching ``Task/query`` filter property (the draft spec never defines one), so they filter client-side against the tasks the server's ``text`` filter already matched, not on the server. ``search_tasks`` falls back to fetching every task and filtering everything client-side, including ``text``, when the server doesn't support ``Task/query`` at all. (`#18 <https://github.com/pycalendar/calendaring-jmap/issues/18>`_)
- ``create_event``, ``send_invite``, ``update_event``, and ``delete_event`` now accept an optional ``if_in_state`` argument. The server rejects the write with ``JMAPMethodError`` (``error_type == "stateMismatch"``) if the account's state has moved since, instead of silently applying over a concurrent change. (`#68 <https://github.com/pycalendar/calendaring-jmap/issues/68>`_)
- Added Python 3.14 support.
- ``JMAPClient``/``AsyncJMAPClient`` now have a public ``get_account_id()``, returning the session's default account id. Fetches the session on first call if it isn't cached yet, the same as any other method here.
- ``JMAPMethodError`` now has a ``properties`` attribute, listing the properties a server's ``invalidProperties`` rejection named, when the server included that list. ``None`` for any other error.
- ``create_event``/``send_invite`` now accept ``calendar_id=None`` to send an event's own ``calendarIds`` unchanged, instead of always overwriting it down to one calendar. Raises ``ValueError`` if the event has no ``calendarIds`` at all.
- ``get_objects_by_sync_token`` and ``get_tasks_by_sync_token`` now accept an optional ``max_changes`` to cap how many changes the server returns in one page.
- ``get_sync_token``, ``get_objects_by_sync_token``, ``get_task_sync_token``, and ``get_tasks_by_sync_token`` now accept an optional ``account_id``, for syncing a calendar or task list shared with you instead of only your own account.


Bug fixes
~~~~~~~~~

- ``ical_to_jscal`` now emits a ``version`` property on every ``Event`` object. Cyrus requires it and rejected every event without one; ``create_event``/``update_event`` failed with ``invalidProperties: ["version"]`` on any current Cyrus build. (`#11 <https://github.com/pycalendar/calendaring-jmap/issues/11>`_)
- ``search_events`` and ``Calendar.search`` now filter with ``inCalendar`` (a single calendar id), matching the current JMAP Calendars spec, instead of the non-existent ``inCalendars`` (a list). Calendar-scoped search previously failed against spec-compliant servers. (`#11 <https://github.com/pycalendar/calendaring-jmap/issues/11>`_)
- ``ical_to_jscal`` no longer emits a ``sendTo`` property on participants, and now emits ``calendarAddress`` instead. Cyrus rejected any event with an ATTENDEE or ORGANIZER without this fix. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- ``ical_to_jscal`` and ``jscal_to_ical`` now use ``recurrenceRule``/``excludedRecurrenceRule`` (singular) instead of RFC 8984's ``recurrenceRules``/``excludedRecurrenceRules`` (an array), which neither Cyrus nor Stalwart accept. Only the first RRULE/EXRULE is kept if a VEVENT has more than one. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- ``ical_to_jscal`` no longer writes a non-mailto ORGANIZER/ATTENDEE URI (e.g. ``sip:alice@example.com``) into the Participant ``email`` property, which RFC 8984 defines as an addr-spec, not an arbitrary URI. Such a participant now has ``calendarAddress`` only. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- ``jscal_to_ical`` no longer double-wraps a non-mailto ``calendarAddress`` in a spurious ``mailto:`` prefix. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- Fixed an ``AttributeError`` when a participant has an explicitly null ``calendarAddress``. (`#12 <https://github.com/pycalendar/calendaring-jmap/issues/12>`_)
- ``get_availability`` no longer returns the wrong account's busy intervals when asked about more than one account. (`#13 <https://github.com/pycalendar/calendaring-jmap/issues/13>`_)
- ``get_availability``'s ``CalendarEvent/query`` fallback now converts each busy interval to UTC using the event's own time zone, instead of returning an offset time for any zone other than UTC. (`#13 <https://github.com/pycalendar/calendaring-jmap/issues/13>`_)
- ``attach_to_event`` sets ``href`` on the attachment's Link, not ``blobId``. The calendars draft allows a Link to carry a blob id directly, but neither Cyrus nor Stalwart actually persists it: Cyrus rejects it outright, and Stalwart silently drops it. A direct download URL round-trips correctly on both. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- On Cyrus, ``get_event_attachments`` may not find an attachment ``attach_to_event`` just wrote. Cyrus accepts a Link with ``rel: "enclosure"`` without error but does not reliably persist that property, and ``get_event_attachments`` filters on it. Stalwart is unaffected. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- ``update_event`` now clears an event's attachments when they're removed from the iCalendar it's given, instead of silently leaving the server's old ``links`` in place. (`#14 <https://github.com/pycalendar/calendaring-jmap/issues/14>`_)
- On Stalwart, ``search_contacts``'s ``text`` filter does not match against a contact's name, only against its email address. A name-only ``text`` search that finds a contact on Cyrus can silently return nothing on Stalwart; use ``email`` when searching for an address. (`#15 <https://github.com/pycalendar/calendaring-jmap/issues/15>`_)
- ``ical_to_jscal`` and ``jscal_to_ical`` now convert the ``URL`` property to and from JSCalendar's ``links``, instead of dropping it entirely. (`#19 <https://github.com/pycalendar/calendaring-jmap/issues/19>`_)
- ``ical_to_jscal`` and ``jscal_to_ical`` now convert a ``VCONFERENCE`` component's ``DESCRIPTION``/``STYLED-DESCRIPTION`` to and from VirtualLocation's ``description``/``descriptionContentType``, instead of dropping it entirely. Cyrus currently rejects ``description`` on a ``VirtualLocation`` with ``invalidProperties`` on ``CalendarEvent/set``; Stalwart round-trips it correctly. (`#19 <https://github.com/pycalendar/calendaring-jmap/issues/19>`_)
- Recurrence override patches now carry ``participants``, ``locations``, ``alerts``, ``status``, ``keywords``, and ``freeBusyStatus`` changes in both conversion directions, instead of silently dropping any per-occurrence change beyond title, start, duration, and description. (`#20 <https://github.com/pycalendar/calendaring-jmap/issues/20>`_)
- ``jscal_to_ical`` now resolves a recurrence override patch returned as flattened per-key JSON-Pointer entries (confirmed on Cyrus, e.g. ``"keywords/urgent": true``), in addition to the whole-map replacement form this package itself always sends. (`#20 <https://github.com/pycalendar/calendaring-jmap/issues/20>`_)
- Alert ``trigger`` values are now emitted and read as proper ``OffsetTrigger``/``AbsoluteTrigger`` objects per RFC 8984, instead of a bare duration or date-time string that a spec-compliant server rejects. (`#20 <https://github.com/pycalendar/calendaring-jmap/issues/20>`_)
- ``ical_to_jscal`` and ``jscal_to_ical`` now convert ``CONFERENCE`` properties to and from JSCalendar's ``virtualLocations``, at both the master event level and inside recurrence override patches, instead of dropping video/phone conference details entirely. (`#20 <https://github.com/pycalendar/calendaring-jmap/issues/20>`_)
- ``ical_to_jscal`` now normalizes non-IANA ``TZID`` values (Windows timezone names, vendor-prefixed globally-unique TZIDs) to IANA names in ``timeZone``, as RFC 8984 requires, instead of passing them through unchanged. (`#44 <https://github.com/pycalendar/calendaring-jmap/issues/44>`_)
- Removed the ``async`` extra. It declared ``niquests[asyncio]``, an extra niquests itself doesn't define; ``pip install calendaring-jmap[async]`` silently installed plain niquests with a pip warning, no different from the base install. Async support has never needed a separate install step: niquests is already a required dependency and ships ``AsyncSession`` unconditionally.
- ``get_jmap_client``/``get_async_jmap_client`` now accept a pre-built ``auth`` object. The ``auth`` keyword argument was silently dropped before reaching the client, so a caller following the documented example got ``JMAPAuthError`` instead of using their own auth object.
- ``ical_to_jscal`` now raises ``ValueError`` when ``DTSTART`` and ``DTEND`` have mismatched value types (one ``DATE``, one ``DATE-TIME``, which RFC 5545 forbids), instead of an unexplained ``TypeError``.
- ``ical_to_jscal`` now raises ``ValueError`` when a VEVENT's ``DTEND``/``DURATION`` resolves to before its ``DTSTART``, instead of silently producing a negative JSCalendar ``duration``, which RFC 8984 forbids and a server would otherwise reject with an opaque ``invalidProperties`` error.
- ``ical_to_jscal`` now raises ``ValueError`` when the master VEVENT is missing ``UID`` or ``DTSTART`` (both mandatory per RFC 5545), instead of a bare, undocumented ``KeyError``.
- ``ical_to_jscal`` now skips a VALARM with no ``TRIGGER`` (mandatory per RFC 5545 and RFC 8984) rather than emitting a JSCalendar Alert with no ``trigger`` property, which RFC 8984 forbids. Other, well-formed alarms on the same event are unaffected.
- ``jscal_to_ical`` now raises ``ValueError`` when the input JSCalendar dict has no ``uid`` (mandatory per RFC 8984), instead of silently emitting an iCalendar VEVENT with no ``UID`` property, which RFC 5545 forbids.


Documentation
~~~~~~~~~~~~~

- Switched the project to uv for Python and dependency management, and to a :file:`Makefile` for the common development commands (tests, linting, docs builds). @stevepiercy (`#63 <https://github.com/pycalendar/calendaring-jmap/issues/63>`_)
- The reference pages under :file:`docs/reference/` are now generated from source with :program:`sphinx-apidoc` instead of hand-maintained. @stevepiercy (`#63 <https://github.com/pycalendar/calendaring-jmap/issues/63>`_)
- Fixed broken links found by ``make linkcheckbroken``, and removed unused theme files. (`#63 <https://github.com/pycalendar/calendaring-jmap/issues/63>`_)
- Added SEO metadata to every docs page: a canonical link, an accurate description, and a social preview image using the Python Calendaring Ecosystem's own branding.
- Added a complete example script that keeps a SQLite cache of a calendar's events in sync.
- Added a how-to page documenting the calendaring_jmap logger and every case where the library logs a warning instead of raising.
- Added a how-to page for checking free/busy availability.
- Added a how-to page for listing address books and searching contacts.
- Added a how-to page for sending invitations and responding to them (accept, decline, tentatively accept).
- Added a how-to page for the full push notification lifecycle: subscribe, confirm verification, renew, unsubscribe.
- Added a how-to page for uploading, attaching, listing, and downloading event attachments.
- Added a how-to page for using ``ical_to_jscal``/``jscal_to_ical`` directly, without making any JMAP request.
- Added a maintainer-facing page documenting the release process.
- Added a reference page collecting every confirmed Cyrus/Stalwart behavioral difference in one table, instead of leaving each one scattered across its own how-to page.
- Added an explanation-page section for why the error hierarchy is split into a generic base and a JMAP-specific layer, fixing a cross-reference in the errors how-to page that previously pointed at nothing.
- Added explanation-page coverage for the conversion layer's own design: why CONFERENCE and VCONFERENCE correlate by URI, and why recurrence override patches compare map-shaped properties by value instead of by key.
- Added explanation-page sections on participant address handling, alert trigger shape, Link/attachment conversion scope, and recurrence rule time zone conversion.
- Added reference pages for ``constants``, ``session``, and ``convert``, which previously had no documentation of their own despite being part of the public API.
- Consolidated the ``account_id`` explanation, previously repeated across most of ``JMAPClient``/``AsyncJMAPClient``'s own methods, into each class's docstring.
- Corrected the authenticate how-to's description of configuration precedence: an explicit ``url`` argument doesn't merge in username, password, auth type, or timeout from environment variables or a config file.
- Corrected the contributor guide's title-underline rule: Sphinx only warns about an overline/underline mismatch on a page's own title, not on an ordinary section heading.
- Cross-linked contribute.rst and release.rst: the change log section had an anchor nothing pointed to, and contribute.rst never mentioned the release page existed.
- Documented ``close()``/``aclose()`` for releasing the HTTP connection without using the client as a context manager.
- Documented ``get_connection_params``, a public function that previously had no reference page.
- Documented the ``ValueError`` conversion-layer validation added in an earlier release, which wasn't documented anywhere.
- Documented the security purpose of the push subscription verification handshake and the callback URL trust requirement.
- Expanded README's Specs section, which only listed 3 of the 7 specs the client actually implements, missing JSCalendar/iCalendar conversion, Contacts, Sharing/Principals, and Tasks entirely.
- Fixed ``docs/how-to/sync.rst`` and ``docs/how-to/example-sync-cache.rst``, which still unpacked ``get_objects_by_sync_token``'s old 4-tuple and described the removed ``serverPartialFail`` exception. The sync-cache example also kept its sync token per calendar; fixed to key it per account, since JMAP state covers the whole account, not one calendar.
- Fixed both Docker test-server READMEs' claim that stopping the container wipes persistent data; neither server's container actually has any to wipe.
- Fixed several cross-references in the API reference that rendered as plain, unlinked text instead of linking to the method or class they named.
- Fixed several stale docs claims left over from before the 1.0.0 release: a "not yet published to PyPI" notice, a missing reference entry for ``BusyInterval``, and a couple of outdated code examples.
- Fixed the Stalwart test-server README's claim that it's used for task integration tests; there are none against either server, and Stalwart's actual exclusive coverage is push notifications.
- Fixed the link in each page's social card, which left out the docs language and version, such as ``/en/stable/``, and so led to a missing page.
- Fixed two links that pointed at ``en/latest`` instead of ``en/stable``.
- Removed CalDAV comparisons from the docs and docstrings; JMAP's own behavior is now described on its own terms.
- Removed the theme/Sphinx version numbers from the docs footer; nobody reading the docs needs to know which Sphinx release built the page.
- The ``apidoc`` make target now actually passes ``SPHINX_APIDOC_OPTIONS`` to :program:`sphinx-apidoc`, via ``--automodule-options``; the :file:`Makefile` set the variable but never wired it into the command.
- The calendars how-to page covers the full calendar management surface (create, update, delete, share, default alerts, subscriptions), not just listing.
- The calendars how-to page now covers reading back a calendar's current sharing configuration from its share_with field, not just writing it with share_calendar.
- The docs site now uses the Python Calendaring Ecosystem's own colors and fonts, in both light and dark mode, instead of the Sphinx theme's defaults.
- The events how-to page now covers ``search_events``, the account-wide search with the attachment, participant email, participation status, and role filters, alongside the existing single-calendar ``cal.search()`` coverage.
- The install how-to page now covers the ``requests`` fallback extra and clarifies that async support needs no separate install step.
- The install how-to page now mentions the package's py.typed marker.
- The one-off Sphinx warning about an unresolvable forward reference in ``niquests``' own type hints is suppressed locally instead of turning off warnings-as-errors project-wide; it's a bug in ``niquests``, not in calendaring-jmap.
- The scheduling how-to page now covers reading a participant's current status, alongside the existing accept/decline/tentatively-accept coverage.
- The tasks how-to page now covers incremental sync and search, alongside the existing create/read/update/delete coverage.


Security fixes
~~~~~~~~~~~~~~

- Now requires ``wassima>=2.1.5``, which drops the compromised eMudhra emSign root certificates from its embedded fallback bundle. CI also installs pip 26.2.2 in every job and publishes to PyPI with ``gh-action-pypi-publish`` v1.14.3, both fixes for the same incident. (`#72 <https://github.com/pycalendar/calendaring-jmap/issues/72>`_)


1.1.0 (2026-09-15)
------------------

New features
~~~~~~~~~~~~

- ``JMAPError`` and its subclasses now subclass ``caldav.lib.error.DAVError`` if ``caldav`` is installed, so code catching ``DAVError`` around CalDAV calls also catches JMAP errors. ``caldav`` is still not a hard dependency. (:issue:`10`)


1.0.0 (2026-09-11)
------------------

New features
~~~~~~~~~~~~

- Extracted the JMAP client from python-caldav into this standalone package. calendaring-jmap no longer depends on ``caldav``: configuration now comes from ``JMAP_URL``/``JMAP_USERNAME``/``JMAP_PASSWORD`` environment variables or a YAML config file instead of ``caldav``'s config system. (:issue:`9`)


Documentation
~~~~~~~~~~~~~

- Added Sphinx documentation scaffolding with the PyData theme. (`#8 <https://github.com/pycalendar/calendaring-jmap/issues/8>`_)
- Added a security policy: how to report a vulnerability, and known risks specific to JMAP session discovery, credential handling, and untrusted calendar data. (`#22 <https://github.com/pycalendar/calendaring-jmap/issues/22>`_)
- Restructured the docs around the Diátaxis framework (tutorial, how-to, reference, explanation), added a security policy and NLnet funding acknowledgment, and cleaned up release metadata ahead of 1.0. (:pr:`42`)


Other tasks
~~~~~~~~~~~

- Maintenance: type checking, test coverage, Docker test fixtures, packaging fix, contributing docs on Read the Docs. (:pr:`40`)
