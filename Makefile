init:
	cd app && uvicorn core.fast_api_automation:app --host 0.0.0.0 --port 8003 --reload

format:
	black --line-length 80 app/core

refresh:
	docker compose stop
	docker compose up