import os
import sys
from os.path import dirname

root_dir = os.path.abspath(dirname(dirname(__file__)))
sys.path.insert(0, root_dir)  # root dir
sys.path.insert(0, os.path.join(dirname(__file__)))  # docs

project = "ArcTracker"
copyright = "ArcTracker Project"
author = "Daniel Górniak"
release = "v0.1"

extensions = ["sphinx_needs", "myst_parser", "sphinxcontrib.plantuml"]

html_theme = "furo"
html_static_path = []
needs_id_required = False

name_p = os.path.join(os.path.dirname(__file__), "plantuml.jar")

on_rtd = os.environ.get("READTHEDOCS") == "True"
if on_rtd:
    plantuml = "java -Djava.awt.headless=true -jar /usr/share/plantuml/plantuml.jar"
else:
    plantuml = "java -jar %s" % name_p

    plantuml_output_format = "svg_img"
