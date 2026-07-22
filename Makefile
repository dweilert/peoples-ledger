.PHONY: test validate run

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

validate:
	PYTHONPATH=src python3 -m peoples_ledger.cli validate

run:
	PYTHONPATH=src python3 -m peoples_ledger.backend.server
