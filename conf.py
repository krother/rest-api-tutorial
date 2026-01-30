# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'REST APIs'
copyright = '2026, Kristian Rother and Nikita Grabin'
author = 'Kristian Rother and Nikita Grabin'
release = '1.0'
html_title = f"{project}"


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx.ext.todo',
    'myst_parser',
    ]

exclude_patterns = ['_build', 'Thumbs.db', 'learning_goals.md', 'README.md']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_logo = "_static/academis_logo.png"
html_favicon = "_static/favicon.ico"

html_css_files = [
    "academis.css",
]
html_theme_options = {
    "source_repository": "https://github.com/krother/rest-api-tutorial",
    "source_branch": "maing",
    "source_directory": "",
}