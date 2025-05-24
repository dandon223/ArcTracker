# ArcTracker
Simple web app used for tracking played cards in game of ARCS by Cole Wehrle


## Documentation

Documentations is written in sphinx-needs.
To create it locally Python 3.13 is needed.
```
mkdir .venvs
python3.13 -m venv .venvs/arc_tracker
source .venvs/arc_tracker/bin/activate
pip install -r requirements.txt
make docs
```
Next open ```docs/_build/html/index.html``` file.

## Backend
Backend was written in Django
To run it locally perform this steps:
```
cd backend
python manage.py runserver
```
To upload changes to model run:
```
python manage.py makemigrations app
python manage.py migrate
```