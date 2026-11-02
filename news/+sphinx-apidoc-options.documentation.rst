The ``apidoc`` make target now actually passes ``SPHINX_APIDOC_OPTIONS`` to ``sphinx-apidoc``, via ``--automodule-options``; the Makefile set the variable but never wired it into the command.
