XARGS := xargs -0 $(shell test $$(uname) = Linux && echo -r)
GREP_T_FLAG := $(shell test $$(uname) = Linux && echo -T)

all:
	@echo "\nThere is no default Makefile target right now. Try:\n"
	@echo "make clean - reset the project and remove auto-generated assets."
	@echo "make pyflakes - run the PyFlakes code checker."
	@echo "make pep8 - run the PEP8 style checker."
	@echo "make test - run the test suite."
	@echo "make check - run all the checkers and tests."
	@echo "make docs - run sphinx to create project documentation.\n"

clean:
	rm -rf dist docs/_build p4p2p/p4p2p.egg-info
	find . \( -name '*.py[co]' -o -name dropin.cache \) -print0 | $(XARGS) rm
	find . \( -name '*.tgz' -o -name dropin.cache \) -print0 | $(XARGS) rm
	find . -name _trial_temp -type d -print0 | $(XARGS) rm -r

pyflakes:
	find . \( -name _build -o -name var \) -type d -prune -o -name '*.py' -print0 | $(XARGS) pyflakes

pep8:
	find . \( -name _build -o -name var \) -type d -prune -o -name '*.py' -print0 | $(XARGS) -n 1 pep8 --repeat

test: clean
	trial --rterrors --coverage test
	@echo "Checking test coverage...\n"
	@-grep -n $(GREP_T_FLAG) '>>>>>' _trial_temp/coverage/p4p2p.*; \
	status=$$?; \
	if [ $$status = 0 ]; \
	then echo "\n\033[0;31m\033[1mWARNING!\033[0m\033[m\017"; \
	echo "Missing test coverage (see report above).\n"; \
	else echo "Mr.TestBot says...\n"; \
	echo "     .oO( Yay! The tests pass with 100% coverage! )"; \
	echo "  \ /"; \
	echo " [O O]"; \
	echo "d| _ |b"; \
	echo " _| |_\n"; \
	fi

check: pep8 pyflakes test

docs: clean
	$(MAKE) -C docs html
	@echo "\nDocumentation can be found here:"
	@echo file://`pwd`/docs/_build/html/index.html
	@echo "\n"
