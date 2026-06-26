PYTHON ?= python3

.PHONY: test check coq

test:
	$(PYTHON) -m unittest discover -s tests -v

coq:
	coqc coq/JsPearl.v

check: test

