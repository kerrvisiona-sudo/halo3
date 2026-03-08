.PHONY: test server install chat

install:
	uv sync
	uv pip install -e .

test:
	uv run python test/test_halo_qwen.py

server:
	uv run python src/halo/api/server.py

chat:
	uv run python src/halo/chat.py

clean:
	rm -rf .ruff_cache __pycache__ src/halo/__pycache__