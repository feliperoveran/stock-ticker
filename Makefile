IMAGE_NAME ?= stock-ticker
IMAGE_TAG ?= latest
APP_PORT ?= 8000

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

run: build
ifndef STOCKS_API_KEY
	@echo
	@echo "Environment variable 'STOCKS_API_KEY' must be defined!"
	@exit 1
endif

	docker run --rm -it \
		-e NDAYS=3 \
		-e SYMBOL=MSFT \
		-e STOCKS_API_HOST="https://www.alphavantage.co/" \
		-e STOCKS_API_KEY=${STOCKS_API_KEY} \
		-v $(shell pwd)/app:/app \
		-p $(APP_PORT):$(APP_PORT) $(IMAGE_NAME):$(IMAGE_TAG)

test: build
	docker run --rm -it \
		$(IMAGE_NAME):$(IMAGE_TAG) pytest -vv
