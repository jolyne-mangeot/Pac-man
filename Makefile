
NAME = pacman.py
ARGS = config.json

REQUIREMENTS = requirements.txt
PROJECT = pacman

VENV = venv
BIN = $(VENV)/bin
PYTHON = python3

CACHE = .mypy_cache

run: install
	source $(BIN)/activate \
	&& $(PYTHON) $(NAME) $(ARGS)

debug: install
	source $(BIN)/activate \
	&& $(PYTHON) -m pdb $(NAME) $(ARGS)

edit: install
	source $(BIN)/activate \
	&& pip install -e .

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	source $(BIN)/activate \
	&& pip install --quiet --upgrade pip \
	&& pip install --quiet -r $(REQUIREMENTS)

clean:
	rm -rf $(CACHE)
	find ./$(PROJECT) | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf

fclean: clean
	rm -rf $(VENV) pacman.egg-info

lint: install
	source $(BIN)/activate \
	&& flake8 . \
	&& mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports\
		--disallow-untyped-defs --check-untyped-defs

lint-strict: install
	source $(BIN)/activate \
	&& flake8 . \
	&& mypy --strict .

.PHONY = run debug edit install clean fclean lint lint-strict
