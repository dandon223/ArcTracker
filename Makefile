.PHONY: docs clean

docs_clean:
	rm -rf docs/_build/
	rm -rf docs/modules/

docs:
	if [ ! -f docs/plantuml.jar  ]; then \
		wget -O docs/plantuml.jar https://sourceforge.net/projects/plantuml/files/1.2023.7/plantuml.1.2023.7.jar; \
	fi
	sphinx-build -b html -a docs docs/_build/html -W -T