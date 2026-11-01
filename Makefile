# SPDX-FileCopyrightText: 2026 calendaring-jmap contributors
# SPDX-License-Identifier: AGPL-3.0-or-later
.DEFAULT_GOAL   = help
SHELL           = bash

# You can set these variables from the command line.
SPHINXOPTS      ?=
PAPER           ?=
VERSION			?=

# Internal variables.
RUFFPATH        = "$(realpath .venv/bin/ruff)"
SPHINXAUTOBUILD = "$(realpath .venv/bin/sphinx-autobuild)"
SPHINXBUILD     = "$(realpath .venv/bin/sphinx-build)"
SPHINXAPIDOC    = "$(realpath .venv/bin/sphinx-apidoc)"
TOWNCRIERPATH   = "$(realpath .venv/bin/towncrier)"
# TODO: determine why sphinx-apidoc ignores this environment variable
SPHINX_APIDOC_OPTIONS = ignore-module-all,members,show-inheritance,undoc-members
DOCS_DIR        = ./docs/
BUILDDIR        = ../_build
SOURCE          = ../src/calendaring_jmap/
APIBUILDDIR     = $(DOCS_DIR)reference/api
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .
VALEFILES       := $(shell find $(DOCS_DIR) -type f -name "*.rst" -print)  # Also add `src` for docstrings.
VALEOPTS        ?=
ZIZMOROPTS      ?=
PYTHONVERSION   = >=3.10,<3.15

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help:  # This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# environment management
.venv:  ## Install required Python, create Python virtual environment, and install package requirements
	@uv python install "$(PYTHONVERSION)"
	@uv venv --python "$(PYTHONVERSION)"
	@uv sync --group dev
	@uv run pre-commit install

.PHONY: sync
sync:  ## Sync package requirements
	@uv sync

.PHONY: init
init: clean clean-python .venv  ## Clean docs build directory, Python virtual environment, and initialize Python virtual environment

.PHONY: clean
clean:  ## Clean docs build directory
	cd $(DOCS_DIR) && rm -rf $(BUILDDIR)/

.PHONY: clean-python
clean-python: clean
	rm -rf .venv/ uv.lock
# /environment management


# documentation builders
.PHONY: html
html: .venv apidoc  ## Build html
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: apidoc
apidoc: .venv  ## Build .rst stub file pages for API reference documentation
	cd $(DOCS_DIR) && $(SPHINXAPIDOC) \
	--templatedir=_templates/apidoc \
	--force \
	--remove-old \
	--separate \
	-o reference/api \
	$(SOURCE) \
	$(SOURCE)/tests*
	@echo
	@echo "Build finished. The .rst stub file pages are in $(APIBUILDDIR)."

.PHONY: livehtml
livehtml: .venv apidoc  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	cd "$(DOCS_DIR)" && ${SPHINXAUTOBUILD} \
		--watch "../src/calendaring_jmap/" \
		--re-ignore ".*\\.swp|.*\\.typed" \
		--ignore "../src/calendaring_jmap/tests" \
		--ignore "../src/calendaring_jmap/fuzzing" \
		--port 8050 \
		-b html . "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

.PHONY: dirhtml
dirhtml: .venv apidoc
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml: .venv apidoc
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: text
text: .venv apidoc
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

.PHONY: sphinx-changes
sphinx-changes: .venv apidoc
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."
# /documentation builders


# test
.PHONY: linkcheck
linkcheck: .venv apidoc  ## Run linkcheck
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: linkcheckbroken
linkcheckbroken: .venv apidoc  ## Run linkcheck and show only broken links
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "[^.]broken\|redirect" --color=always && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: vale
vale: .venv apidoc  ## Run Vale style, grammar, and spell checks
	@uv run vale sync
	@uv run vale --no-wrap $(VALEOPTS) $(VALEFILES); \
	if [ $$? = 0 ]; then \
		echo; \
		echo "Vale passed!"; \
	else \
		echo; \
		echo "Vale spell, style, and grammar check failed."; \
		echo "Read the error messages above to see what didn't pass."; \
		echo "For guidance of how to correct the errors, see:"; \
		echo "https://calendaring-jmap.readthedocs.io/en/stable/contribute.html#spelling-grammar-and-style"; \
		exit 1; \
	fi

#.PHONY: zizmor
#zizmor: .venv  ## Run zizmor static analysis on GitHub Actions workflows
#	@uv run zizmor $(ZIZMOROPTS) .github/workflows/

#.PHONY: doctest
#doctest: .venv apidoc  ## Test snippets and docstrings in the documentation
#	@echo;
#	@pytest src/calendaring_jmap/tests/test_with_doctest.py
#
#.PHONY: docstring
#docstring: .venv apidoc  ## Test docstrings are formatted properly
#	@echo;
#	@pytest -rx src/calendaring_jmap/tests/test_docstrings.py

.PHONY: docs-all
docs-all: .venv apidoc clean vale doctest docstring html linkcheckbroken  ## Clean docs build, then run vale, doctest, html, and linkcheckbroken

#.PHONY: test
#test: .venv  ## Run code tests and coverage
#	@uv run tox
#
#.PHONY: test-dist
#test-dist:  ## Build and test the distribution files
#	@src/calendaring_jmap/tests/test_create_release.sh
# /test


# development
.PHONY: dev
dev: .venv  ## Install required Python, create Python virtual environment, install package and development requirements

.PHONY: format
format: .venv  ## Format the code base with ruff
	$(RUFFPATH) format
	$(RUFFPATH) check --fix
# /development

# deployment
.PHONY: rtd-prepare
rtd-prepare:  ## Prepare environment on Read the Docs
	asdf plugin add uv
	asdf install uv latest
	asdf global uv latest

.PHONY: rtd-pr-preview
rtd-pr-preview: rtd-prepare .venv apidoc ## Build pull request preview on Read the Docs
	cd $(DOCS_DIR) && $(SPHINXBUILD) -b html $(ALLSPHINXOPTS) ${READTHEDOCS_OUTPUT}/html/
# /deployment

# release
#.PHONY: wo
#wo: .venv
#	@uv run scripts/generate_windows_to_olson_mapping.py
#	$(RUFFPATH) format
#
.PHONY: changes-check
changes-check: dev
	$(TOWNCRIERPATH) check

#.PHONY: changes-draft
#changes-draft: dev
#	@test -n "$(VERSION)" || (echo "VERSION is not set. Run 'export VERSION=x.y.z' first." && exit 1)
#	$(TOWNCRIERPATH) build --draft --version ${VERSION} --yes
#
#.PHONY: changes
#changes: dev
#	@test -n "$(VERSION)" || (echo "VERSION is not set. Run 'export VERSION=x.y.z' first." && exit 1)
#	$(TOWNCRIERPATH) build --version ${VERSION} --yes
#
#.PHONY: new-version
#new-version: dev ## Get the new version to use for a release
#	@CURRENT_VERSION=`git tag | sort -V | tail -n 1 | grep -o '[0-9].*'`; \
#	if ls news | grep -q '.breaking'; then OPTION=M; elif ls news | grep -q '.feature'; then OPTION=m; else OPTION=p; fi; \
#	VERSION=`./scripts/semver -$${OPTION} $$CURRENT_VERSION`; \
#	echo "export VERSION=$$VERSION";
# /release
