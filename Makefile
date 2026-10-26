NAME = pac-man.py
CONFIG = config.json
SPEC = pac-man.spec
PYTHON = python3
VENV = .venv
PIP = $(VENV)/bin/pip
PYTHON_VENV = $(VENV)/bin/python
TMP = $(VENV)/.install
WHEEL = Ressources/mazegenerator-00001/mazegenerator-2.1.0-py3-none-any.whl
EXCLUDE = $(VENV),build,dist

all: install

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

$(TMP): requirements.txt $(VENV)/bin/activate
	$(PIP) install -r requirements.txt
	$(PIP) install --force-reinstall $(WHEEL)
	$(PIP) install flake8 mypy pyinstaller
	touch $(TMP)

install: $(TMP)

run: install
	$(PYTHON_VENV) $(NAME) $(CONFIG)

debug: install
	$(PYTHON_VENV) -m pdb $(NAME) $(CONFIG)

lint: install
	$(VENV)/bin/flake8 . --exclude $(EXCLUDE)
	$(VENV)/bin/mypy . \
		--exclude '^(\.venv|build|dist)/' \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict: install
	$(VENV)/bin/flake8 . --exclude $(EXCLUDE)
	$(VENV)/bin/mypy . --exclude '^(\.venv|build|dist)/' --strict

package: install
	$(VENV)/bin/pyinstaller --noconfirm $(SPEC)

clean:
	find . -path ./$(VENV) -prune -o -type d -name "__pycache__" \
		-exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf build

fclean: clean
	rm -rf dist
	rm -rf $(VENV)

re: fclean all

.PHONY: all install run debug lint lint-strict package clean fclean re
