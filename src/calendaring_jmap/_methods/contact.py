# SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
JMAP Contacts method builders and response parsers.

Pure functions: no HTTP, no state. AddressBook and ContactCard object
shapes are defined in RFC 9610 (JMAP Contacts); ContactCard properties
follow JSContact (RFC 9553).
"""

from __future__ import annotations

from calendaring_jmap._methods import build_get, build_get_by_query_result, build_query
from calendaring_jmap.objects.contact import JMAPAddressBook, JMAPContact

_CONTACT_QUERY_CALL_ID = "contact-query-0"
_CONTACT_GET_BY_QUERY_CALL_ID = "contact-get-1"


def build_address_book_get(
    account_id: str,
    ids: list[str] | None = None,
    properties: list[str] | None = None,
) -> tuple:
    """Build an ``AddressBook/get`` method call tuple.

    A standard ``/get`` per RFC 8620 section 5.1 (RFC 9610 section 2.1
    defines no custom arguments for it).

    Args:
        account_id: The JMAP accountId to query.
        ids: List of AddressBook IDs to fetch, or ``None`` to fetch all.
        properties: List of property names to return, or ``None`` for all.

    Returns:
        A 3-tuple ``("AddressBook/get", arguments_dict, call_id)``.
    """
    return build_get("AddressBook/get", "ab-get-0", account_id, ids, properties)


def parse_address_book_get(response_args: dict) -> list[JMAPAddressBook]:
    """Parse the arguments dict from an ``AddressBook/get`` method response.

    Args:
        response_args: The second element of a ``methodResponses`` entry
            whose method name is ``"AddressBook/get"``.

    Returns:
        List of ``JMAPAddressBook``.
        Empty if ``"list"`` is absent or empty.
    """
    books = [JMAPAddressBook.from_jmap(item) for item in response_args.get("list", [])]
    # RFC 9610 section 2 requires isDefault to be present and true for
    # exactly one AddressBook in the account; confirmed live that Cyrus's
    # current image omits the key entirely rather than sending it false,
    # which JMAPAddressBook.from_jmap otherwise reads as "not default" even
    # for the account's only address book. When there is exactly one
    # AddressBook and none of them actually claimed isDefault, it is the de
    # facto default regardless of what the server sent, so mark it rather
    # than reporting a default-less account the spec says can't happen.
    if len(books) == 1 and not books[0].is_default:
        books[0].is_default = True
    return books


def build_contact_query(
    account_id: str,
    filter_condition: dict | None = None,
    sort: list[dict] | None = None,
    position: int = 0,
    limit: int | None = None,
) -> tuple:
    """Build a ``ContactCard/query`` method call tuple.

    A standard ``/query`` per RFC 8620 section 5.5. FilterCondition
    properties are defined in RFC 9610 section 3.3.1; see
    ``JMAPClient.search_contacts`` for the
    live-verified ``email``/``text`` matching behavior on Cyrus and
    Stalwart, which differs between the two properties.

    Args:
        account_id: The JMAP accountId to query.
        filter_condition: A FilterCondition dict, e.g.
            ``{"email": "alice@example.com", "text": "Alice"}``. Multiple
            properties combine with an implicit AND. ``None`` means no
            filter (matches every contact).
        sort: List of ``Comparator`` dicts. ``None`` means server default
            ordering.
        position: Zero-based index of the first result to return.
        limit: Maximum number of IDs to return. ``None`` means no limit.

    Returns:
        A 3-tuple ``("ContactCard/query", arguments_dict, call_id)``.
    """
    return build_query(
        "ContactCard/query",
        _CONTACT_QUERY_CALL_ID,
        account_id,
        filter_condition,
        sort,
        position,
        limit,
    )


def build_contact_get_by_query_result(
    account_id: str, properties: list[str] | None = None
) -> tuple:
    """Build a ``ContactCard/get`` call that back-references the ids from
    the ``ContactCard/query`` call ``build_contact_query`` builds.

    Args:
        account_id: The JMAP accountId, must match the query call's.
        properties: List of property names to return, or ``None`` for all.

    Returns:
        A 3-tuple ``("ContactCard/get", arguments_dict, call_id)``, meant
        to be appended after ``build_contact_query``'s own return value
        in the same ``methodCalls`` list.
    """
    return build_get_by_query_result(
        "ContactCard/get",
        _CONTACT_GET_BY_QUERY_CALL_ID,
        "ContactCard/query",
        _CONTACT_QUERY_CALL_ID,
        account_id,
        properties,
    )


def parse_contact_get(response_args: dict) -> list[JMAPContact]:
    """Parse the arguments dict from a ``ContactCard/get`` method response.

    Args:
        response_args: The second element of a ``methodResponses`` entry
            whose method name is ``"ContactCard/get"``.

    Returns:
        List of ``JMAPContact``.
        Empty if ``"list"`` is absent or empty.
    """
    return [JMAPContact.from_jmap(item) for item in response_args.get("list", [])]
