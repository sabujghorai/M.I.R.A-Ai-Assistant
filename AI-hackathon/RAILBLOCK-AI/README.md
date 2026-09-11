# Railway Block Planner

## Folder structure

This project is two independent servers that talk over HTTP — the
Flask backend does **not** serve the frontend files. Keep this layout:

```
RAILBLOCK-AI/
├── backend/
│   ├── __init__.py       (empty — makes this a package)
│   ├── app.py
│   ├── priority.py
│   ├── optimizer.py
│   └── conflict.py
├── data/
│   ├── maintenance.csv
│   └── trains.csv
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── background.jpeg
└── requirements.txt
```

`app.py` imports with `from backend.priority import ...` and reads
`data/maintenance.csv` as a relative path — so it must always be run
**from the `RAILBLOCK-AI/` root**, not from inside `backend/`.

## 1. Run the backend

```bash
cd RAILBLOCK-AI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m backend.app
```

Running it as a module (`python -m backend.app`, not `python
backend/app.py`) is what makes the `from backend.priority import
...` line resolve correctly. You should see Flask start on
`http://0.0.0.0:8000`. Visit `http://localhost:8000/` in a browser —
you should get back:

```json
{"system": "RAILBLOCK AI", "status": "Running"}
```

If you don't get that, the frontend has nothing to talk to and every
request will fail.

## 2. Run the frontend

The frontend is static files, so any static server works. From
`RAILBLOCK-AI/frontend/`:

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000/`. (Opening `index.html` directly
via `file://` also mostly works, but a local server avoids browser
restrictions on `fetch`.)

## 3. Keep both running

Two terminals, both left open:

- Terminal 1: `python -m backend.app` (from `RAILBLOCK-AI/`) → serves the API on port 8000
- Terminal 2: `python -m http.server 3000` (from `RAILBLOCK-AI/frontend/`) → serves the UI on port 3000

`script.js` is hardcoded to call `http://localhost:8000`
(`API_BASE`), so the backend's port has to stay 8000 unless you
change that constant too.

## What was fixed

- `/api/schedule` never included submitted requests — it returned a
  hardcoded list every time. Requests now get appended to it.
- `/api/optimize` computed a result but never saved it anywhere, and
  always re-optimized the *newest* request instead of the oldest
  unscheduled one. It now persists the computed block time onto the
  request and works through pending requests in order.
- `requirements.txt` pinned `pandas==3.0.5`, which doesn't exist on
  PyPI — install would fail. Pinned to `3.0.4`.
- The "Section" field was free text, so it rarely matched a real
  section code in `trains.csv`, making the optimizer's conflict
  check meaningless. It's now a dropdown of the actual section codes.
- `.confirm-msg` had `display: none` in CSS but the JS never
  switched it back on — the confirmation/error message text was
  being set but was never visible.
- The optimizer button/message elements existed in the JS but not in
  the HTML, so the button did nothing. Added them to the Block
  Schedule view.
