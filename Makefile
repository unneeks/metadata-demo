.PHONY: setup generate start stop clean demo load-openmetadata run-pipeline run-dq prepare-qlik health

setup:
	python3 -m pip install -r requirements.txt

generate:
	python3 generators/generate_all.py --seed 42 --employees 1000 --months 12 --output ./src

start:
	docker-compose up -d

stop:
	docker-compose down

clean:
	rm -rf src/*
	rm -rf bronze/*
	rm -rf silver/*
	rm -rf gold/*
	rm -rf metadata/*/*
	rm -rf qlik/*.csv
	docker-compose down -v

demo: setup generate start
	bash scripts/bootstrap.sh

load-openmetadata:
	bash scripts/setup_openmetadata.sh
	bash scripts/ingest_metadata.sh
	bash scripts/ingest_glossary.sh
	bash scripts/ingest_lineage.sh

run-pipeline:
	docker-compose exec -T airflow-webserver airflow dags trigger employee_delivery_pipeline

run-dq:
	docker-compose exec -T spark-iceberg spark-submit /opt/airflow/spark/dq_validation.py

prepare-qlik:
	docker-compose exec -T spark-iceberg python3 /opt/airflow/spark/publish_qlik.py

health:
	docker-compose ps
