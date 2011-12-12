GOOGLE_REPO := code.google.com/p/pymon
SF_REPO := pymon.git.sourceforge.net/gitroot/pymon/pymon
GITHUB_REPO := github.com:oubiwann/pymon.git
AUTHOR ?= oubiwann

push:
	git push https://$(GOOGLE_REPO)
	git push ssh://$(AUTHOR)@$(SF_REPO)
	git push git@$(GITHUB_REPO)

pull:
	git pull https://$(GOOGLE_REPO)
