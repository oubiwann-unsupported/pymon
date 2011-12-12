GOOGLE_REPO := code.google.com/p/pymon
SF_REPO := pymon.git.sourceforge.net/gitroot/pymon/pymon
GITHUB_REPO := github.com:oubiwann/pymon.git
AUTHOR ?= oubiwann

push:
	git push --all https://$(GOOGLE_REPO)
	git push --all ssh://$(AUTHOR)@$(SF_REPO)
	git push --all git@$(GITHUB_REPO)

pull:
	git pull https://$(GOOGLE_REPO)
