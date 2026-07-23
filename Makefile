.PHONY: test validate assure run

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

validate:
	PYTHONPATH=src python3 -m peoples_ledger.cli validate

assure:
	PYTHONPATH=src python3 -m peoples_ledger.cli assure

run:
	PYTHONPATH=src python3 -m peoples_ledger.backend.server
