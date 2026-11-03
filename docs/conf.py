# SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Sphinx configuration for calendaring-jmap documentation."""

import datetime
import importlib.metadata
import os
import re
import sys
from pathlib import Path

from packaging.version import Version

HERE = Path(__file__).parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))  # update docs from calendaring_jmap source for livehtml

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = importlib.metadata.version("calendaring-jmap")
# The short X.Y version.
version = Version(str(release)).base_version

project = "calendaring-jmap"
this_year = datetime.date.today().year  # noqa: DTZ011
copyright = f"{this_year}, calendaring-jmap contributors"  # noqa: A001
author = "calendaring-jmap contributors"

extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",  # must be loaded after sphinx.ext.napoleon. See https://github.com/tox-dev/sphinx-autodoc-typehints/issues/15
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_issues",
    "sphinx_last_updated_by_git",
    "sphinx_llms_txt",
    "sphinxext.opengraph",
]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"
exclude_patterns = [
    "reference/api/modules.rst",
]

# niquests' own AsyncSession type hints reference AsyncLifeCycleHook in a way
# sphinx-autodoc-typehints can't resolve from here; nothing in this project's
# own code can fix a third-party library's annotation. Scoped to this one
# warning category so -W still catches anything else.
suppress_warnings = ["sphinx_autodoc_typehints.forward_reference"]

# -- Options for HTML output -------------------------------------------------

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/pycalendar/calendaring-jmap",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
            "attributes": {"target": "_blank", "rel": "noopener me"},
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/calendaring-jmap",
            "icon": "fa-custom fa-pypi",
            "type": "fontawesome",
            "attributes": {"target": "_blank", "rel": "noopener me"},
        },
    ],
    "article_footer_items": ["last-updated"],
    "footer_start": ["nlnet", "donate"],
    "footer_center": "copyright",
    "footer_end": ["rtd-pr-previews", "theme-version", "sphinx-version"],
    "logo": {"text": "calendaring-jmap"},
    "navbar_start": ["navbar-logo", "version"],
    "navigation_with_keys": True,
    "search_bar_text": "Search",
    "secondary_sidebar_items": ["edit-this-page", "page-toc", "sourcelink"],
    "show_nav_level": 2,
    "show_toc_level": 2,
    "use_edit_page_button": True,
}
html_context = {
    "github_user": "pycalendar",
    "github_repo": "calendaring-jmap",
    "github_version": "main",
    "doc_path": "docs",
}
html_static_path = ["_static"]
# Custom fa-custom/fa-pypi icon used in icon_links above.
html_js_files = [
    ("js/custom-icons.js", {"defer": "defer"}),
]
pygments_style = "sphinx"
smartquotes_action = "De"


# -- linkcheck builder configuration ----------------------------------
# Ignore localhost
linkcheck_ignore = [
    # Requires authentication
    r"https://github.com/pycalendar/calendaring-jmap/security/advisories/new",
]
linkcheck_anchors = True
linkcheck_timeout = 5
linkcheck_retries = 1


# -- notfound.extension configuration -----------------------------------------
# https://sphinx-notfound-page.readthedocs.io/en/latest/configuration.html
notfound_template = "404.html"
# Defaults to READTHEDOCS_CANONICAL_URL's path on RTD. Outside RTD, that env
# var isn't set and the extension falls back to a hardcoded "/en/latest/",
# which 404s every asset on a local build. Use root-relative paths instead
# when not building on RTD.
if not os.environ.get("READTHEDOCS"):
    notfound_urls_prefix = "/"


# -- sphinx.ext.autodoc configuration ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
autoclass_content = "both"
autodoc_default_options = {
    "ignore-module-all": True,
    "members": True,
    "show-inheritance": True,
    "undoc-members": True,
}


# Matches only a full, final dotted-path segment starting with "_"
# (e.g. the "_JMAPClientBase" in "~pkg.client._JMAPClientBase"), not a
# role whose class name merely contains an underscore partway through
# (e.g. "My_Public_Thing" must not match).
_PRIVATE_BASE_RE = re.compile(r":py:class:`~?(?:\w+\.)*(_\w+)`")


def _drop_private_bases(app, name, obj, options, bases):
    """Keep a private base (e.g. ``_JMAPClientBase``) off the rendered
    "Bases:" line; ``show-inheritance`` otherwise renders it as-is.

    By the time this event fires (confirmed on Sphinx 9.2.0), each entry
    in ``bases`` is already a rendered ``:py:class:`...``` role string,
    not a class object, so the check matches the role's own target name
    rather than ``__name__``. If a future Sphinx version reverts to
    passing class objects, a non-string entry here is left alone rather
    than raising, so this degrades to a silent no-op instead of a build
    failure; check the rendered reference pages after any Sphinx upgrade
    to confirm this still filters. Falls back to ``object`` if every
    base was private, so the "Bases:" line never renders empty.
    """
    kept = [
        base for base in bases if not (isinstance(base, str) and _PRIVATE_BASE_RE.fullmatch(base))
    ]
    bases[:] = kept or [":py:class:`object`"]


def setup(app):
    app.connect("autodoc-process-bases", _drop_private_bases)


# -- sphinx.ext.intersphinx configuration ------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "icalendar": ("https://icalendar.readthedocs.io/en/latest/", None),
    "niquests": ("https://niquests.readthedocs.io/en/latest/", None),
}


# -- sphinx.ext.napoleon configuration ----------------------------------
napoleon_use_param = True
napoleon_google_docstring = True
napoleon_attr_annotations = True

# Render "Attributes:" as :ivar: field-list entries instead of standalone
# attribute directives, which collide with autodoc's own dataclass field
# introspection and produce "duplicate object description" warnings.
napoleon_use_ivar = True


# -- sphinx_copybutton configuration ----------------------------------
# https://sphinx-copybutton.readthedocs.io/en/latest/use.html
# Exclude line numbers, prompts, and console output when copying code blocks.
copybutton_exclude = ".linenos, .gp, .go"


# -- sphinx_issues configuration -----------------------------------------
# enables :issue:`N`, :pr:`N`, :user:`name` roles
issues_github_path = "pycalendar/calendaring-jmap"


# -- sphinx_last_updated_by_git configuration -------------------------
html_last_updated_fmt = "%Y-%m-%d"


# -- sphinx_llms_txt configuration -------------------------


# -- sphinxext.opengraph configuration -----------------------------------------
html_baseurl = os.environ.get(
    "READTHEDOCS_CANONICAL_URL", "https://calendaring-jmap.readthedocs.io/en/stable/"
)

ogp_site_url = html_baseurl
ogp_site_name = "calendaring-jmap"
ogp_description_length = 200
ogp_type = "website"
ogp_social_cards = {
    "image": "_static/img/pycal-icon.png",
    "image_mini": "_static/img/pycal-icon.png",
    "line_color": "#0f766e",
    "background_color": "#f8f7f4",
}
