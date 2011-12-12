GOOGLE_REPO := code.google.com/p/pymon
SF_REPO := pymon.git.sourceforge.net/gitroot/pymon/pymon
GITHUB_REPO := github.com:oubiwann/pymon.git
AUTHOR ?= oubiwann
MSG_FILE ?= MSG

LIB := pymon


clean:
	find ./ -name "*~" -exec rm {} \;
	find ./ -name "*.pyc" -exec rm {} \;
	find ./ -name "*.pyo" -exec rm {} \;
	find . -name "*.sw[op]" -exec rm {} \;
	rm -rf MSG.backup _trial_temp/ build/ dist/ MANIFEST \
		CHECK_THIS_BEFORE_UPLOAD.txt *.egg-info


push:
	git push --all https://$(GOOGLE_REPO)
	git push --all ssh://$(AUTHOR)@$(SF_REPO)
	git push --all git@$(GITHUB_REPO)


pull:
	git pull -a https://$(GOOGLE_REPO)


update: pull push
.PHONY: update


commit-raw:
	git commit -a -v


msg:
	git diff ChangeLog |egrep -v '^\+\+\+'|egrep '^\+.*'|sed -e 's/^+//' > $(MSG_FILE)


commit: msg
	git commit -a -v -t $(MSG_FILE)
	mv $(MSG_FILE) $(MSG_FILE).backup
	touch $(MSG_FILE)


commit-push: commit push
.PHONY: commit-push


stat: msg
	@echo
	@echo "### Changes ###"
	@echo
	-@cat $(MSG_FILE)
	@echo
	@echo "### Git working branch status ###"
	@echo
	@git status -s
	@echo
	@echo "### Git branches ###"
	@echo
	@git branch


todo:
	git grep -n -i -2 XXX
.PHONY: todo


build:
	python setup.py build
	python setup.py sdist


check-docs: files = "docs/USAGE.txt"
check-docs:
	@python -c \
	"from $(LIB).testing import suite;suite.runDocTests('$(files)');"


check-votingdocs: files = "docs/methods/*/*.txt"
check-votingdocs:
	@python -c \
	"from $(LIB).testing import suite;suite.runDocTests('$(files)');"

check-dist:
	@echo "Need to fill this in ..."


check: build check-docs check-votingdocs
	trial $(LIB)

build-docs:
	cd docs/sphinx; make html

register:
	python setup.py register

upload: check
	python setup.py sdist upload --show-response

upload-docs: build-docs
	python setup.py upload_docs --upload-dir=docs/html/
