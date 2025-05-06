import os
import pathlib
import sys
from os.path import dirname

#python_use_unqualified_type_names = True

root_dir = os.path.abspath(dirname(dirname(__file__)))
sys.path.insert(0, root_dir)  # root dir
sys.path.insert(0, os.path.join(dirname(__file__)))  # docs
# sys.path.insert(0, os.path.join(root_dir, "src", "services", "segments_toolkit"))
# sys.path.insert(0, os.path.join(root_dir, "airflow", "dags"))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ArcTracker"
copyright = "ArcTracker Project"
author = "Daniel Górniak"
release = "v0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_needs", "myst_parser"]


#templates_path = ["_templates"]
# exclude_patterns = [
#     "build",
#     "Thumbs.db",
#     ".DS_Store",
#     "demo_page_header.rst",
#     "demo_hints",
# ]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = []

# autodoc
#autodoc_default_options = {"special-members": "__init__,__getitem__,__call__", "exclude-members": "model_computed_fields,model_config,model_fields"}
#autodoc_mock_imports = [
#    "easydict",
#    "deepdiff",
#    "minio",
#    "pcdet",
#    "psycopg2",
#    "pytorch3d",
#    "segments",
#    "torch",
#    "database.database_import_dataset",
#    "logger",
#    "utils",
#    "rest_client"
#]
#ython_use_unqualified_type_names = True

# relative paths in linked readmes can not be resolved
#suppress_warnings = ["myst.xref_missing", "myst.header"]

# sphinx_needs
needs_id_required = False

name_p = os.path.join(os.path.dirname(__file__), "plantuml.jar")

on_rtd = os.environ.get("READTHEDOCS") == "True"
if on_rtd:
    plantuml = "java -Djava.awt.headless=true -jar /usr/share/plantuml/plantuml.jar"
else:
    plantuml = "java -jar %s" % name_p

    plantuml_output_format = "svg_img"

#needs_uml_allowmixing = True
#html_static_path = ["_static"]
