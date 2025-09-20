PY ?= python3

.PHONY: help checksums validate new-case package-mas

help:
	@echo "Targets:"
	@echo "  make checksums               - Compute/update per-directory SHA256SUMS.txt"
	@echo "  make validate                - Run repository validator"
	@echo "  make new-case ENTITY_ID=foo SLUG=bar"
	@echo "  make package-mas CASE=cases/foo-bar"

checksums:
	$(PY) scripts/compute_checksums.py

validate:
	$(PY) scripts/validate_repo.py

new-case:
	@if [ -z "$(ENTITY_ID)" ] || [ -z "$(SLUG)" ]; then \
		echo "Usage: make new-case ENTITY_ID=foo SLUG=bar"; exit 2; \
	fi
	ENTITY_ID=$(ENTITY_ID) SLUG=$(SLUG) $(PY) scripts/new_case.py --entity $(ENTITY_ID) --slug $(SLUG)

package-mas:
	@if [ -z "$(CASE)" ]; then \
		echo "Usage: make package-mas CASE=cases/foo-bar"; exit 2; \
	fi
	$(PY) scripts/package_mas.py --case $(CASE)
