PROJ := pymon
GOOGLE_REPO := code.google.com/p/$(PROJ)
SF_REPO := pymon.git.sourceforge.net/gitroot/pymon/$(PROJ)
GITHUB_REPO := github.com:oubiwann/$(PROJ).git
AUTHOR ?= oubiwann
MSG_FILE ?= MSG
VIRT_DIR ?= .pymon-venv
VERSION := $(shell python pymon/scripts/getVersion.py)
LIB := $(PROJ)


version:
	@echo $(VERSION)


install-txmongo:
	sudo easy_install-2.7 third-party/mongo-async-python-driver/


clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf $(MSG_FILE).backup _trial_temp/ build/ dist/ MANIFEST \
		CHECK_THIS_BEFORE_UPLOAD.txt *.egg-info


push-tags:
	git push --tags git@$(GITHUB_REPO)
	git push --tags https://$(GOOGLE_REPO)
	git push --tags ssh://$(AUTHOR)@$(SF_REPO)


push:
	git push --all git@$(GITHUB_REPO)
	git push --all https://$(GOOGLE_REPO)
	git push --all ssh://$(AUTHOR)@$(SF_REPO)

push-all: push push-tags
.PHONY: push-all

pull:
	git pull -a https://$(GOOGLE_REPO)


update: pull push-all
.PHONY: update


commit-raw:
	git commit -a -v


msg:
	@rm $(MSG_FILE)
	@echo '!!! REMOVE THIS LINE !!!' >> $(MSG_FILE)
	@git diff ChangeLog |egrep -v '^\+\+\+'|egrep '^\+.*'|sed -e 's/^+//' >> $(MSG_FILE)
.PHONY: msg


commit: msg
	git commit -a -v -t $(MSG_FILE)
	mv $(MSG_FILE) $(MSG_FILE).backup
	touch $(MSG_FILE)


commit-push: commit push-all
.PHONY: commit-push


stat: msg
	@echo
	@echo "### Changes ###"
	@echo
	-@cat $(MSG_FILE)|egrep -v '^\!\!\!'
	@echo
	@echo "### Git working branch status ###"
	@echo
	@git status -s
	@echo
	@echo "### Git branches ###"
	@echo
	@git branch

status: stat
.PHONY: status

todo:
	git grep -n -i -2 XXX
.PHONY: todo


build:
	@python setup.py build
	@python setup.py sdist

virtual-build: SUB_DIR ?= test-build
virtual-build: DIR ?= $(VIRT_DIR)/$(SUB_DIR)
virtual-build: clean build
	mkdir -p $(VIRT_DIR)
	-test -d $(DIR) || virtualenv $(DIR)
	@. $(DIR)/bin/activate
	-test -e $(DIR)/bin/twistd || $(DIR)/bin/pip install twisted
	-test -d $(DIR)/lib/python2.7/site-packages/nevow || $(DIR)/bin/pip install nevow
	$(DIR)/bin/pip uninstall -vy PyMonitor
	rm -rf $(DIR)/lib/python2.7/site-packages/PyMonitor-*
	$(DIR)/bin/easy_install-2.7 ./dist/PyMonitor-*
	-@deactivate


virtual-run: SUB_DIR ?= test-build
virtual-run: DIR ?= $(VIRT_DIR)/$(SUB_DIR)
virtual-run: virtual-build
	. $(DIR)/bin/activate
	$(DIR)/bin/pymond


clean-virt: clean
	rm -rf $(VIRT_DIR)


virtual-build-clean: clean-virt build virtual-build
.PHONY: virtual-build-clean


check-docs: files = "docs/USAGE.txt"
check-docs:
	@python -c \
	"from $(LIB).testing import suite;suite.runDocTests('$(files)');"


check-dist:
	@echo "Need to fill this in ..."


check: MOD ?= pymon
check: build check-docs check-votingdocs
	python pymon/testing/runner.py $(MOD)


check-integration:
# placeholder for integration tests
.PHONY: check-integration


build-docs:
	cd docs/sphinx; make html


register:
	python setup.py register


upload: check
	python setup.py sdist upload --show-response


upload-docs: build-docs
	python setup.py upload_docs --upload-dir=docs/html/
