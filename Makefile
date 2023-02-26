local:
	cd app && uvicorn core.fast_api_endpoints:app --host 0.0.0.0 --port 8003 --reload

dcu:
	sudo docker compose up

format:
	black --line-length 80 app/core/api_resources.py
	black --line-length 80 app/core/celery_scheduler.py
	black --line-length 80 app/core/celery_worker.py
	black --line-length 80 app/core/constants.py
	black --line-length 80 app/core/models.py
	black --line-length 80 app/core/random_mouse.py
	black --line-length 80 app/core/redis_cache.py
	black --line-length 80 app/core/task_manager.py
	black --line-length 80 app/tests/*

refresh:
	docker compose stop
	docker compose up

tests:
	sudo docker compose run app pytest -vv

clear_imgs:
	python3 clear_img_data.py

clear_src:
	sudo python3 reset_collections.py