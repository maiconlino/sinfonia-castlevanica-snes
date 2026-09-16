PYTHON ?= python3
.PHONY: all assets check
all:
	$(PYTHON) tools/build.py
assets:
	$(PYTHON) tools/build_content.py
	$(PYTHON) tools/generate_graphics.py
	$(PYTHON) tools/build_r3_assets.py
	$(PYTHON) tools/build_audio.py
check: all
	$(PYTHON) tests/validate_r3.py
	$(PYTHON) tests/first_route_r3.py
	$(PYTHON) tests/upper_exit_r3.py
