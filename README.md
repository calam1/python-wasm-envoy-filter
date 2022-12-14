## Building WASM envoy filters using Rust

I have ran prior tutorials before using the 0.1.x versions of proxy_wasm. There is an updated version of this library 0.2 - https://docs.rs/proxy-wasm/0.2.0/proxy_wasm/
The code is pretty different, no more fn_start and some of the arguments have changed for the on_http calls, etc.
I have not found a new tutorial explaining how to run the new lib. But have pieced together how to do this with the following resources
* https://docs.rs/proxy-wasm/0.2.0/proxy_wasm/
* https://events.istio.io/istiocon-2021/slides/c8p-ExtendingEnvoyWasm-EdSnible.pdf
* https://martin.baillie.id/wrote/envoy-wasm-filters-in-rust/

## Basic setup

rust version
```
❯❯❯ rustc --version
rustc 1.64.0 (a55dd71d5 2022-09-19)

```

k8 desktop - kind

created a kind cluster w/nodeport

config.yaml file
```
❯❯❯ cat config.yaml
apiVersion: kind.x-k8s.io/v1alpha4
kind: Cluster
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
    listenAddress: "0.0.0.0" # Optional, defaults to "0.0.0.0"
    protocol: tcp # Optional, defaults to tcp
- role: worker
```

command to create kind cluster, running k8 1.19.16
```
❯❯❯ kind create cluster --image=kindest/node:v1.19.16 --config=config.yaml --name nodeport
```

you need to have istio installed on your machine so that you can have injection enabled in your namespace
```
#create namespace
❯❯❯ kubectl create ns demo
namespace/demo created

# run the following command to see if injection is set for your namespace, since you just created the demo namespace, it won't be labeled
❯❯❯ kubectl get namespace -L istio-injection

NAME                 STATUS   AGE   ISTIO-INJECTION
default              Active   41m
demo                 Active   21s
istio-system         Active   39m   disabled
kube-node-lease      Active   41m
kube-public          Active   41m
kube-system          Active   41m
local-path-storage   Active   41m


# label the namespace and verify
❯❯❯ kubectl label namespace demo istio-injection=enabled --overwrite=true
namespace/demo labeled

# verify, now you see the demo namespace is enabled
❯❯❯ kubectl get namespace -L istio-injection

NAME                 STATUS   AGE    ISTIO-INJECTION
default              Active   42m
demo                 Active   109s   enabled
istio-system         Active   40m    disabled
kube-node-lease      Active   42m
kube-public          Active   42m
kube-system          Active   42m
local-path-storage   Active   42m

```

create the docker image to deploy
```
# run this in the root directory where the Dockerfile is located
❯❯❯ docker build -t python-wasm .
```

load the docker image onto the kind cluster named nodeport
```
❯❯❯ kind load docker-image python-wasm:latest --name nodeport
```

build the wasm filter and deploy it via a ConfigMap (instructions are in the README of the wasm-header repo) in this repo https://github.com/calam1/wasm-header

So I typically deploy the wasm filter first, the directions are in the aforementioned repo

Then I deploy the envoyfilter, then the app, of course you can deploy in whatever order you want
```
❯❯❯ kubectl apply -f deployment/wasm-envoy-filter.yml -n demo
❯❯❯ kubectl apply -f deployment/python-wasm.yml -n demo
```

Note: that the envoyfilter deployed selects the workload of the app we just deployed
```

# snippet of the wasm-envoy-filter.yml
...
...

 workloadSelector:
    labels:
      app: python-wasm
...
...
```

curl the endpoint, you should see 2 new headers; hello: World and powered-by: proxy-wasm
```
 ❯❯❯ curl -v localhost:30000/home                                                                                               on branch: main
*   Trying 127.0.0.1:30000...
* Connected to localhost (127.0.0.1) port 30000 (#0)
> GET /home HTTP/1.1
> Host: localhost:30000
> User-Agent: curl/7.79.1
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< hello: World
< powered-by: proxy-wasm
< content-length: 14
< content-type: text/plain
< date: Mon, 26 Sep 2022 16:32:23 GMT
< server: istio-envoy
< x-envoy-decorator-operation: python-wasm.demo.svc.cluster.local:80/*
<
Hello, World!
```

here are the logs that were generated by the wasm filter
```
│ 2022-09-26T16:32:09.267153Z    warning    envoy wasm    wasm log: #2 completed.                                                                                                                                                            │
│ 2022-09-26T16:32:21.755446Z    warning    envoy wasm    wasm log: #2 -> :authority: localhost:30000                                                                                                                                        │
│ 2022-09-26T16:32:21.755494Z    warning    envoy wasm    wasm log: #2 -> :path: /home                                                                                                                                                       │
│ 2022-09-26T16:32:21.755498Z    warning    envoy wasm    wasm log: #2 -> :method: GET                                                                                                                                                       │
│ 2022-09-26T16:32:21.755501Z    warning    envoy wasm    wasm log: #2 -> user-agent: curl/7.79.1                                                                                                                                            │
│ 2022-09-26T16:32:21.755503Z    warning    envoy wasm    wasm log: #2 -> accept: */*                                                                                                                                                        │
│ 2022-09-26T16:32:21.755505Z    warning    envoy wasm    wasm log: #2 -> x-forwarded-proto: http                                                                                                                                            │
│ 2022-09-26T16:32:21.755507Z    warning    envoy wasm    wasm log: #2 -> x-request-id: 2cb036a6-2c04-9d2e-8894-34493d84ab37                                                                                                                 │
│ 2022-09-26T16:32:21.755611Z    warning    envoy wasm    wasm log: #2 <- :status: 200                                                                                                                                                       │
│ 2022-09-26T16:32:21.755618Z    warning    envoy wasm    wasm log: #2 <- hello: World                                                                                                                                                       │
│ 2022-09-26T16:32:21.755620Z    warning    envoy wasm    wasm log: #2 <- powered-by: proxy-wasm                                                                                                                                             │
│ 2022-09-26T16:32:21.755622Z    warning    envoy wasm    wasm log: #2 <- content-length: 14                                                                                                                                                 │
│ 2022-09-26T16:32:21.755624Z    warning    envoy wasm    wasm log: #2 <- content-type: text/plain                                                                                                                                           │
│ 2022-09-26T16:32:21.765446Z    warning    envoy wasm    wasm log: #2 completed.                                                                                                                                                            │
│ 2022-09-26T16:32:23.111283Z    warning    envoy wasm    wasm log: #3 -> :authority: localhost:30000                                                                                                                                        │
│ 2022-09-26T16:32:23.111385Z    warning    envoy wasm    wasm log: #3 -> :path: /home                                                                                                                                                       │
│ 2022-09-26T16:32:23.111405Z    warning    envoy wasm    wasm log: #3 -> :method: GET                                                                                                                                                       │
│ 2022-09-26T16:32:23.111506Z    warning    envoy wasm    wasm log: #3 -> user-agent: curl/7.79.1                                                                                                                                            │
│ 2022-09-26T16:32:23.111566Z    warning    envoy wasm    wasm log: #3 -> accept: */*                                                                                                                                                        │
│ 2022-09-26T16:32:23.111581Z    warning    envoy wasm    wasm log: #3 -> x-forwarded-proto: http                                                                                                                                            │
│ 2022-09-26T16:32:23.111756Z    warning    envoy wasm    wasm log: #3 -> x-request-id: 186c96d3-33b5-961a-afb2-a86d5cdc0f1f                                                                                                                 │
│ 2022-09-26T16:32:23.111903Z    warning    envoy wasm    wasm log: #3 <- :status: 200                                                                                                                                                       │
│ 2022-09-26T16:32:23.112019Z    warning    envoy wasm    wasm log: #3 <- hello: World                                                                                                                                                       │
│ 2022-09-26T16:32:23.112043Z    warning    envoy wasm    wasm log: #3 <- powered-by: proxy-wasm                                                                                                                                             │
│ 2022-09-26T16:32:23.112055Z    warning    envoy wasm    wasm log: #3 <- content-length: 14                                                                                                                                                 │
│ 2022-09-26T16:32:23.112066Z    warning    envoy wasm    wasm log: #3 <- content-type: text/pl
```