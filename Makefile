.PHONY: setup generate start stop clean

setup:
	pip install -r requirements.txt

generate:
	python generators/generate_all.py --seed 42 --employees 1000 --months 12 --output ./src

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
