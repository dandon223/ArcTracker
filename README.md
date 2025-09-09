# ArcTracker
Simple web app used for tracking played cards in game of ARCS by Cole Wehrle
For now it is using Django as a backend with sqlite3 as a database.
To run it python 3.13 is needed.

## How to install environment
```
mkdir .venvs
python3.13 -m venv .venvs/arc_tracker
source .venvs/arc_tracker/bin/activate
pip install -r requirements.txt
```

## Backend
To run it locally perform this steps:
```
cd backend
make start
make initial_data
```
To upload changes to model run:
```
make full_restart
```
To test:
```
make format
make check
make test
```

## Frontend
To run it locally perform this steps:
```
nvm use --lts
npm create vite@latest
npm install
npm run dev
```