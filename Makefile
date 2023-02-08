IMAGE_NAME ?= stock-ticker
IMAGE_TAG ?= latest
APP_PORT ?= 8000
KUBECTL_CONTEXT ?= docker-desktop
K8S_NAMESPACE ?= forgerock
K8S_SECRET_NAME ?= stock-ticker-secrets

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

check_env_vars:
ifndef STOCKS_API_KEY
	@echo
	@echo "Environment variable 'STOCKS_API_KEY' must be defined!"
	@exit 1
endif

run: check_env_vars build
	docker run --rm -it \
		-e NDAYS=7 \
		-e SYMBOL=MSFT \
		-e STOCKS_API_HOST="https://www.alphavantage.co" \
		-e STOCKS_API_KEY=${STOCKS_API_KEY} \
		-v $(shell pwd)/app:/app \
		-p $(APP_PORT):$(APP_PORT) $(IMAGE_NAME):$(IMAGE_TAG)

test: build
	docker run --rm -it \
		-e NDAYS=3 \
		-e SYMBOL=BESTSTOCK \
		-e STOCKS_API_HOST="https://example.com" \
		-e STOCKS_API_KEY=123 \
		$(IMAGE_NAME):$(IMAGE_TAG) pytest -vv

deploy: check_env_vars build
	@kubectl --context $(KUBECTL_CONTEXT) apply -f k8s/
	@kubectl --context $(KUBECTL_CONTEXT) create secret generic $(K8S_SECRET_NAME) \
		-n $(K8S_NAMESPACE) \
		--from-literal=apikey=${STOCKS_API_KEY} || true
	@kubectl --context $(KUBECTL_CONTEXT) rollout restart deploy -n $(K8S_NAMESPACE)

clean:
	kubectl --context $(KUBECTL_CONTEXT) delete -f k8s/

ndays:
	@curl localhost:8080/stock-ticker/ndays; echo

configure-ingress:
	@kubectl --context=$(KUBECTL_CONTEXT) create ns ingress-nginx || true
	@kubectl --context=$(KUBECTL_CONTEXT) apply --wait=true -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml
	@kubectl --context=$(KUBECTL_CONTEXT) patch svc -n ingress-nginx ingress-nginx-controller --type=merge -p '{"spec": {"ports": [{"port": 8080,"targetPort": 80,"name": "http"}]}}'
	@echo "Waiting for NGINX Ingress to be running..."
	@kubectl --context=$(KUBECTL_CONTEXT) wait --timeout 5m -n ingress-nginx deployment/ingress-nginx-controller --for condition=available
