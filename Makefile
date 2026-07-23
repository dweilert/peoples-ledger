.PHONY: test validate assure report report-html export-report run

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

export-report:
	PYTHONPATH=src python3 -m peoples_ledger.cli export-report

run:
	PYTHONPATH=src python3 -m peoples_ledger.backend.server
