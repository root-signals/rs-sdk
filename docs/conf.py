# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "root-signals Python SDK"
copyright = "2025, Root Signals Ltd"  # noqa: A001
author = "Root Signals"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
    "myst_parser",  # markdown support as input
    "sphinx.ext.autodoc",  # for autoapi
    "sphinx.ext.doctest",  # automated test running
    "sphinx.ext.inheritance_diagram",  # for autoapi
    "sphinx.ext.napoleon",  # nicer syntax for docstrings - see https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html
    "sphinx_markdown_builder",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = "alabaster"
html_theme = "furo"
# html_static_path = ["_static"]

autodoc_typehints = "both"  # default is 'signature' (not in description)

autoapi_dirs = ["../src/root"]
autoapi_ignore = ["*/utils.py"]

autoapi_options = [
    # "imported-members", # this is per same top level, and we wind up with cruft from generated code
    # 'inherited-members', # frequently pointless
    # 'private-members', # they should not be used -> omit
    # 'show-inheritance-diagram', # relatively ugly
    # 'special-members',
    "members",
    "show-inheritance",
    "show-module-summary",
    "undoc-members",
]

autoapi_member_order = "groupwise"

github_url = "https://github.com/root-signals/rs-python-sdk"

# Useful for debugging
# autoapi_keep_files = True

# suppress_warnings = ["autoapi"]


def skip_unwanted(app, what, name, obj, skip, options):
    # what: "attribute", "class", "data", "exception", "function", "method", "module", "package"
    # name: fully qualified name of obj
    # obj: object itself

    if ".generated." in name:
        # We only refer to models
        if what == "module" and ".models." not in name:
            return True
        # Our API should hide the actual request objects
        if what == "module" and name.endswith("_request"):
            return True
        # Omit the methods from generated code.
        # In general there's plenty of from_X, to_X for all generated models which are simply not relevant.
        if what == "method":
            return True

    return skip


def setup(sphinx):
    sphinx.connect("autoapi-skip-member", skip_unwanted)
