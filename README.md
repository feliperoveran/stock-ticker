# Stock Ticker
Python API using FastAPI that looks up prices for a given stock and return the
last `ndays` of data, alongside the average closing price on that period.

## Requirements
Two modes of deployment are supported, standalone and on Kubernetes.

For the `standalone` deployment:
* `docker`

For the `kubernetes` deployment:
* `docker`
* `kubectl`
* a Kubernetes cluster

### Kubernetes
This has been tested on [Kubernetes on Docker Desktop](https://docs.docker.com/desktop/kubernetes/#enable-kubernetes).

Other clusters will also work (minikube, k3d, etc) and, to deploy to said clusters, provide the value
of `KUBECTL_CONTEXT` when deploying using `make`. To avoid deploying on an
undesired cluster when another kubectl context is selected, we default the
context to `docker-desktop` unless overridden.

The caveat of using a different local cluster platform is that the docker image
will have to be pushed to the registry, whereas when using k8s on Docker
Desktop, there is no such requirement.

### Docker
The Dockerfile leverages multi-stage builds to allow sharing steps between
images and also keeping the final image sizes as small as possible.
To build the `api` image, we use the `api` target. To build the `test` image, we
use the `test` target.

This details are for information purposes only, as the `Makefile` handles the
selecting the correct target as needed.

## Kubernetes resources
The Kubernetes manifests can be found under the `k8s` and contain the following:
1. Namespace - The namespace under all app resources are deployed
2. ConfigMap - The app's config containing non-sensitive values
3. Deployment - App's deployment
4. Service - A ClusterIP service that exposes the app within the cluster
5. Ingress - The ingress resource definition that exposes the service
   externally. For this example, the Nginx ingress was used.

A secret is also created at deployment time and contains the `STOCKS_API_KEY`.
It was not included as part of the "static" Kubernetes manifests as it includes
a secret and should not be added to source control. So, instead, it is created
once the app is deployed using `STOCKS_API_KEY=<key> make deploy`.

### Getting started
There is automation using `make`.

#### For easy onboarding
* Standalone:
`STOCKS_API_KEY=<api-key> make run`

Then access the app on `http://localhost:8000/ndays`

* Kubernetes
`STOCKS_API_KEY=<api-key> make deploy`
`make configure-ingress`

Then access the app on `http://localhost:8080/stock-ticker/ndays`

#### Build the app image
`make build`

Does not need to be run directly as it is a dependency of the `make deploy`
target.

#### Build the test image
This image contains extra dependencies for running the `pytest` tests and code
coverage reports.

`make build-tests`

Does not need to be run directly as it is a dependency of the `make test`
target.

#### Standalone deployment
`STOCKS_API_KEY=<api-key> make run`

Will build and run the Docker image. Also mounts the volume so the changes are
hot-reloaded and exposes the app on `http://localhost:8000`. So, in order to
call the `/ndays` route, make a request to `http://localhost:8000/ndays`.

#### Deployment to Kubernetes
`STOCKS_API_KEY=<api-key> make deploy`

To deploy the app and all the resources to Kubernetes. The image will be built
(but not pushed, as this example uses k8s on Docker Desktop).

In order to access the app outside of the cluster, an ingress controller has to
be configured. For this, use the `make configure-ingress` target.

When on k8s, the app is exposed by the ingress under:
`http:// localhost:8080/stock-ticker/ndays`.

The port `8080` has been used to avoid conflicts with port 80 - See the `make
configure-ingress` target for more details.

#### Rollout restart
`make rollout-restart`

Used to rollout restart the app replicas and pick up image changes when the tag
has not been modified.

#### Clean Kubernetes resources
`make clean`

To remove all created Kubernetes resources.

#### Ndays response
`make ndays`

Calls the `/ndays` API route on the Kubernetes deployment.

#### Logs
`make logs`

Utility target to fetch the pod's logs. One can also use tools such as `stern`,
but this target provides an easy way to see the logs without custom tooling.

#### Configure Ingress
`make configure-ingress`

Configures the NGINX ingress on the cluster. This allows exposing the app
externally so it can be accessed from outside the cluster. Other ingress
controllers can be used, but will require changes to the Ingress manifest.

## API documentation
API documentation is provided in two formats, Swagger and the raw OpenAPI
manifest.

* Swagger UI: `http://localhost:8080/stock-ticker/docs`
* OpenAPI manifest: `http://localhost:8080/stock-ticker/openapi.json`


## Tests and code coverage
There is 100% test coverage using `pytest` and can be easily run using `make
test`.

Tests are under the `test` directory.

This will run the integration tests, unit tests and code coverage reports.

## API configuration
The API can be configured using environment variables. The following parameters
are supported:

* `SYMBOL`: Stock symbol to fetch - Example "MSFT"
* `NDAYS`: Used to calculate average and return the N number of stock data timeseries - Example "7"
* `STOCKS_API_HOST`: The stocks API host - Example "https://www.alphavantage.co/"
* `STOCKS_API_KEY`: The API key to use when calling the API - Example "123"
* `LOG_LEVEL`: Configures the app's log level - Example "INFO"
* `ENABLE_METRICS`: Whether to enable or not exposing the Prometheus metrics on /metrics - Example "true".
  A nil value will disable the metrics.
* `API_REFRESH_FREQUENCY_MINUTES`: Controls the frequency for refreshing the API
  data. This is the singleton's in-memory cache TTL. Defaults to 60 minutes - Example "60"

## Prometheus metrics
The app has been instrumented using Prometheus. Metrics are exposed on `/metrics`.

Includes the default metrics exposed by the
[prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) and a custom counter
for the cache hits, `stock_api_cache_hit`.

To inspect the metrics:
* Kubernetes: `http://localhost:8080/stock-ticker/metrics`
* Standalone: `http://localhost:8000/metrics`

## Health check
The `/healthz` route is exposed. Not intended to be used externally, but it is
used by Kubernetes for the `liveness` and `readiness` probes.

## In-memory cache
To avoid calling the API on every request, the API client is configured as a
singleton with in-memory cache.

Based on the value of `API_REFRESH_FREQUENCY_MINUTES`, it will call the API and
cache the results until the TTL has expired. And, when that happens, the data
will be re-fetched from the API and the cache will be updated.
This ensures better scalability and dramatically reduces the response time on
subsequent requests when the cache is still hot.

For comparison:
* Cold cache
`time make ndays`
```
real    0m0.192s
user    0m0.007s
sys     0m0.000s
```

* Hot cache
`time make ndays`
```
real    0m0.011s
user    0m0.007s
sys     0m0.000s
```

**Note**: This is **not** a distributed cache. The cache is done per-replica.
So, on a multi-replica deployment, if the first request goes to replica #1 and
the second request goes to replica #2, the API will be fetched on each replica.
Subsequent requests on each of the replicas (as long as the TTL is still valid)
will be cached and the API will not be re-fetched.
