.PHONY: setup dev test scrape write edition backend frontend clean init-db venv

# Create virtual environment
venv:
	uv venv

# Setup all dependencies
setup: venv
	uv pip install -r backend/requirements.txt
	cd frontend && npm install

# Run development servers
dev:
	docker-compose up

# Run backend only (for local development)
backend:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend only (for local development)
frontend:
	cd frontend && npm start

# Run tests
test:
	cd backend && pytest tests/ -v

# Initialize database
init-db:
	cd backend && python -c "from core.database.session import init_db; init_db()"

# Run scraper
scrape:
	python scrapers/run_scraper.py

# Run story writer (markov engine by default, zero cost)
write:
	python story_writer/run_writer.py

# Publish a fresh edition: scrape feeds then write articles
edition: scrape write

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/node_modules frontend/build 2>/dev/null || true
