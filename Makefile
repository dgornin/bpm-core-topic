# Приёмочные тесты топика. Без make: python tests/run_acceptance.py --level C|B|A
# Другой интерпретатор:   make test-c PYTHON=python
# Другая реализация:      make test-all BPM_IMPL="./target/release/bpmcore"

PYTHON ?= python3
RUNNER = $(PYTHON) tests/run_acceptance.py

.PHONY: test test-c test-b test-a test-all lint

test-c:
	$(RUNNER) --level C

test-b:
	$(RUNNER) --level B

test-a:
	$(RUNNER) --level A

test-all: test-a

test: test-all

# lint не пишет __pycache__ (в том числе в tests/): компиляция в памяти, -B при импорте.
lint:
	$(PYTHON) -B -c "import sys; [compile(open(f, encoding='utf-8').read(), f, 'exec') for f in sys.argv[1:]]" bpmcore/*.py tests/run_acceptance.py
	$(PYTHON) -B -c "import json, bpmcore.snapshot as s; assert json.load(open('spec/snapshot.json', encoding='utf-8')) == s.DEFAULT_SNAPSHOT, 'spec/snapshot.json и bpmcore/snapshot.py разошлись'"
