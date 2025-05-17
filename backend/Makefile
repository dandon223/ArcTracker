flake8 = flake8 --require-plugins darglint,flake8,flake8-rst-docstrings,flake8-pyproject,mccabe,pycodestyle,pyflakes

format:
	isort .
	black .

check: format
	mypy . 
	$(flake8) . 
	pylint app ArcTracker