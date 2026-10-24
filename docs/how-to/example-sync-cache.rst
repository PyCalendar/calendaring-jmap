.. SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
.. SPDX-License-Identifier: AGPL-3.0-or-later

================================
Sync an account to a local cache
================================

A complete script that keeps a SQLite cache of an account's events in sync, using :doc:`authentication <authenticate>` and :doc:`incremental sync <sync>` together.

.. code-block:: python

    import sqlite3

    from calendaring_jmap import get_jmap_client

    DB_PATH = "events.db"


    def init_db(conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS events ("
            "  id TEXT PRIMARY KEY,"
            "  calendar_id TEXT NOT NULL,"
            "  ical TEXT NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS sync_state ("
            "  id INTEGER PRIMARY KEY CHECK (id = 0),"
            "  token TEXT NOT NULL"
            ")"
        )
        conn.commit()


    def load_token(conn):
        row = conn.execute("SELECT token FROM sync_state WHERE id = 0").fetchone()
        return row[0] if row else None


    def save_token(conn, token):
        conn.execute(
            "INSERT INTO sync_state (id, token) VALUES (0, ?) "
            "ON CONFLICT(id) DO UPDATE SET token = excluded.token",
            (token,),
        )
        conn.commit()


    def sync_account(client, conn):
        token = load_token(conn)
        if token is None:
            token = client.get_sync_token()
            save_token(conn, token)
            return

        while True:
            added, modified, deleted, old_state, new_state, has_more_changes = (
                client.get_objects_by_sync_token(token)
            )

            for obj in list(added) + list(modified):
                ical_str = obj.get_icalendar_instance().to_ical().decode()
                calendar_id = next(iter(obj.get_data()["calendarIds"]))
                conn.execute(
                    "INSERT INTO events (id, calendar_id, ical) VALUES (?, ?, ?) "
                    "ON CONFLICT(id) DO UPDATE SET ical = excluded.ical",
                    (obj.id, calendar_id, ical_str),
                )
            for event_id in deleted:
                conn.execute("DELETE FROM events WHERE id = ?", (event_id,))

            save_token(conn, new_state)
            conn.commit()

            token = new_state
            if not has_more_changes:
                break


    if __name__ == "__main__":
        with get_jmap_client() as client:
            conn = sqlite3.connect(DB_PATH)
            init_db(conn)
            sync_account(client, conn)
            conn.close()

This reads configuration the same way every other example does, through :func:`~calendaring_jmap.get_jmap_client`'s explicit-argument/environment-variable/config-file chain; see :doc:`authenticate` for how to set that up.

JMAP state covers the whole account, not one calendar, so ``sync_state`` holds a single row for the whole account's token, not one per calendar: :meth:`~calendaring_jmap.client.JMAPClient.get_objects_by_sync_token` returns every changed event across every calendar in the account in one call, and ``obj.get_data()["calendarIds"]`` says which calendar each one actually belongs to. An event can belong to more than one calendar; this cache only has room for one row per event id, so it stores whichever calendar id comes first.

The first run has no stored token, so it only records a baseline and caches nothing; the next run starts fetching real deltas. ``has_more_changes`` being ``True`` means the server truncated the page, not an error; the loop calls :meth:`~calendaring_jmap.client.JMAPClient.get_objects_by_sync_token` again with ``new_state`` until it's ``False``. See :doc:`errors` for the errors this can still raise, such as an account-wide capability or auth failure.
