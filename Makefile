.DEFAULT_GOAL := build

classifier-lambda-setup:
	if [ ! -d {{venv}} ]; then python3 -m venv venv; fi
	source ./venv/bin/activate && pip3 install -r lambdas/classifier/requirements.txt
.PHONY: classifier-lambda-setup

classifier-lambda-test:
	python3 -m unittest
.PHONY: classifier-lambda-test

examples-setup:
	if [ ! -d {{venv}} ]; then python3 -m venv venv; fi
	source ./venv/bin/activate && pip3 install -r examples/requirements.txt
.PHONY: examples-setup

fix:
	npm run fix

build-ts:
	npm run check

build: build-ts
	cdk synth

setup: classifier-lambda-setup

deploy-cdk: build
	cdk deploy --all
.PHONY: deploy-cdk

deploy-yolo: build
	cdk deploy --all --require-approval never
.PHONY: deploy-yolo

deploy-hotswap: build
	cdk deploy --all --hotswap
.PHONY: deploy-cdk
