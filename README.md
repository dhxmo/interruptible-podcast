# interruptible-podcast

untitled root dir

$ docker-compose down && docker-compose up -d

$ uvicorn server.src.app.main:app --host 0.0.0.0 --port 8000 --reload

$ arq src.app.core.worker.settings.WorkerSettings