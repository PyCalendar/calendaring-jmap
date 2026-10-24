.. SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

==================
Sync incrementally
==================

JMAP's state-based sync lets you fetch only what changed since the last call, without scanning the full calendar.

Fetch a token, then the delta
=============================

.. code-block:: python

    # Record the current state
    token = client.get_sync_token()

    # ... time passes, events are created, modified, or deleted ...

    # Fetch only the delta
    added, modified, deleted, old_state, new_state, has_more_changes = (
        client.get_objects_by_sync_token(token)
    )

    for obj in added:
        print("New:", obj.get_icalendar_instance())
    for obj in modified:
        print("Updated:", obj.get_icalendar_instance())
    for event_id in deleted:
        print("Deleted ID:", event_id)

``added`` and ``modified`` are lists of :class:`~calendaring_jmap.objects.calendar_object.JMAPCalendarObject`. ``deleted`` is a list of event IDs: those objects no longer exist on the server, so their data can't be fetched. ``new_state`` is the server's new sync token; chaining straight from it avoids the race window a separate :meth:`~calendaring_jmap.client.JMAPClient.get_sync_token` round trip would open. ``old_state`` is the ``token`` argument echoed back, useful for detecting a server that silently accepted a stale or invalid token instead of reporting an error; see :meth:`~calendaring_jmap.client.JMAPClient.get_objects_by_sync_token`'s own docs for what both Cyrus and Stalwart actually do here. This example ignores ``has_more_changes``, fine for a small change set; see the next section for what it means and how to use it.

Handle a truncated change list
==============================

If the server has more changes than it returned in one page, ``has_more_changes`` is ``True`` rather than :meth:`~calendaring_jmap.client.JMAPClient.get_objects_by_sync_token` raising an error. Call it again with ``new_state`` to fetch the next page, repeating until ``has_more_changes`` is ``False``:

.. code-block:: python

    while True:
        added, modified, deleted, old_state, new_state, has_more_changes = (
            client.get_objects_by_sync_token(token)
        )
        # process added/modified/deleted here
        token = new_state
        if not has_more_changes:
            break

See :doc:`errors` for the errors this can still raise, such as an account-wide capability or auth failure.

Persist the token between runs
==============================

This saves ``new_state`` once per run and doesn't loop on ``has_more_changes``, unlike the paging example above; fine for a change set small enough to fit in one page, otherwise loop the same way:

.. code-block:: python

    import json
    import pathlib

    TOKEN_FILE = pathlib.Path("sync_token.json")


    def load_token():
        if TOKEN_FILE.exists():
            return json.loads(TOKEN_FILE.read_text())["token"]
        return None


    def save_token(token):
        TOKEN_FILE.write_text(json.dumps({"token": token}))


    token = load_token()
    if token is None:
        token = client.get_sync_token()
        save_token(token)
    else:
        added, modified, deleted, old_state, new_state, has_more_changes = (
            client.get_objects_by_sync_token(token)
        )
        # process changes here
        save_token(new_state)
