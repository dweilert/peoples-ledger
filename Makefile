.PHONY: test validate assure report run

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

validate:
	PYTHONPATH=src python3 -m peoples_ledger.cli validate

assure:
	PYTHONPATH=src python3 -m peoples_ledger.cli assure

report:
	PYTHONPATH=src python3 -m peoples_ledger.cli report

report-html:
	PYTHONPATH=src python3 -m peoples_ledger.cli report-html

run:
	PYTHONPATH=src python3 -m peoples_ledger.backend.server
