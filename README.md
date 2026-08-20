Backend setup (dev)

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. (Optional) set `DATABASE_URL` or `SECRET_KEY` in a `.env` file in this folder.

3. Initialize the database and create a sample user:

```bash
python init_db.py
```

4. Run the app:

```bash
python app.py
```

Endpoints:
- `POST /register` {email,password}
- `POST /login` {email,password}
- `GET /me` (Authorization: Bearer <token>)
- `GET/POST /reminders` (Authorization)
- `PUT/DELETE /reminders/<id>` (Authorization)
- `POST /progress` {phase: red|yellow|green} (Authorization)
