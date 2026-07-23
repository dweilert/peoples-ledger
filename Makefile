.PHONY: test test-browser validate assure phase1-acceptance phase2-acceptance report report-html export-report run

test:
	PYTHONPATH=src python3 -m unittest discover -s tests

test-browser:
	NODE_PATH=$$(npm root -g) playwright test tests/browser/privacy_egress.spec.js --reporter=line

validate:
	PYTHONPATH=src python3 -m peoples_ledger.cli validate

assure:
	PYTHONPATH=src python3 -m peoples_ledger.cli assure

phase1-acceptance:
	PYTHONPATH=src python3 -m peoples_ledger.cli phase1-acceptance

phase2-acceptance:
	PYTHONPATH=src python3 -m peoples_ledger.cli phase2-acceptance

report:
	PYTHONPATH=src python3 -m peoples_ledger.cli report

report-html:
	PYTHONPATH=src python3 -m peoples_ledger.cli report-html

export-report:
	PYTHONPATH=src python3 -m peoples_ledger.cli export-report

run:
	PYTHONPATH=src python3 -m peoples_ledger.backend.server
