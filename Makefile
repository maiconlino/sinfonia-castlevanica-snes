PYTHON ?= python3
.PHONY: all assets check replay capture
all:
	$(PYTHON) tools/build.py
assets:
	$(PYTHON) tools/build_content.py
	$(PYTHON) tools/build_routes.py
	$(PYTHON) tools/generate_graphics.py
	$(PYTHON) tools/build_r3_art.py
	$(PYTHON) tools/build_audio.py
check: all
	$(PYTHON) tests/validate_r3.py
	$(PYTHON) tests/regression_r3.py
	$(PYTHON) tests/adaptive_r3.py
	$(PYTHON) tests/replay_r3.py
capture:
	$(PYTHON) tests/capture_r3.py
