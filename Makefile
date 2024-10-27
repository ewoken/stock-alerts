COLOR_RESET = \033[0m
COLOR_ERROR = \033[31m
COLOR_INFO = \033[32m
COLOR_COMMENT = \033[33m
COLOR_TITLE_BLOCK  = \033[0;44m\033[37m
SHELL := /bin/bash

## Setup the project
setup:
	@printf "\n${COLOR_INFO}Setting up the project...${COLOR_RESET}\n\n"
	# Install any missing binaries
	@brew install --quiet xz
	# Install pyenv and python 3.10
	make install-pyenv
	# install requirements
	make install


## install requirements
install: setup-venv
	@printf "\n${COLOR_INFO}Installing requirements...${COLOR_RESET}\n\n"
	@source .venv/bin/activate &&\
	uv pip install -r requirements.txt

## install pyenv
install-pyenv:
	@printf "\n${COLOR_INFO}Installing pyenv...${COLOR_RESET}\n\n"
	@brew update && brew upgrade --quiet pyenv &&\
	pyenv install --skip-existing 3.10

## install uv
install-uv:
	@printf "\n${COLOR_INFO}Installing uv...${COLOR_RESET}\n\n"
	curl -LsSf https://astral.sh/uv/0.2.22/install.sh | sh


## setup venv
setup-venv: install-uv install-pyenv
	@printf "\n${COLOR_INFO}Setting up venv...${COLOR_RESET}\n\n"
	PYENV_VERSION=3.10 uv venv

## Run all tests
test:
	@echo "Running tests..."
