# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SnowForm'
copyright = '2025, Darjan Salaj, Julian Seither, Max Koeppel'
author = 'Darjan Salaj, Julian Seither, Max Koeppel'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The Pygments HCL lexer can't parse valid HCL like `module.x.r["KEY"].name` and
# falls back to relaxed highlighting, which renders fine
suppress_warnings = ['misc.highlighting_failure']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
html_theme = "furo"
html_static_path = ['_static']
