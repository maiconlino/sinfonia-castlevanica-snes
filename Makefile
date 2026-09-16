PYTHON ?= python3
.PHONY: all assets check
all:
	$(PYTHON) tools/build.py
assets:
	$(PYTHON) tools/build_content.py
	$(PYTHON) tools/generate_graphics.py
	$(PYTHON) tools/build_audio.py
check:
	$(PYTHON) tests/validate_rom.py
	$(PYTHON) tests/validate_graphics.py
