# Karan TrailQuest — Project Notebook

This notebook documents the complete local-to-EC2 DevOps workflow for the Karan TrailQuest application.

The project uses:

- Flask
- MongoDB Atlas
- Docker
- Docker Compose
- Jenkins CI/CD
- Kubernetes with kind
- NGINX Ingress
- Metrics Server
- Horizontal Pod Autoscaler
- Prometheus
- Grafana
- Prometheus ServiceMonitor

---

## Phase 1 — Pull and inspect

Clone or update the project repository:

```bash
git pull origin main
git status
tree -a -L 3
```

Repository:

```text
https://github.com/karanchauhan-bit/Karan-TrailQuest.git
```

Main project structure:

```text
Dockerfile
Jenkinsfile
PROJECT_NOTEBOOK.md
README.md
app.py
compose.yaml
requirements.txt

k8s/
  namespace.yaml
  configmap.yaml
  secret.example.yml
  secret.yml
  app-deployment.yaml
  app-service.yaml
  ingress.yaml
  hpa.yaml
  servicemonitor.yaml

scripts/
  deploy.sh
  health_check.sh

static/
templates/
tests/
```

---

## Phase 2 — Local environment checks

Verify required tools:

```bash
python3 --version
git --version
docker --version
docker compose version
kubectl version --client
kind version
```

Check Git status:

```bash
git status
```

---

## Phase 3 — Python virtual environment

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

All tests should pass before continuing.

---

## Phase 4 — MongoDB Atlas

Create a MongoDB Atlas cluster, database user and network access rule.

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` and configure the real MongoDB Atlas URI.

Never commit the real URI.

Database:

```text
karan_trailquest
```

Collection:

```text
bookings
```

The real MongoDB connection string must remain private.

---

## Phase 5 — Run Flask locally

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start Flask:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Health endpoint:

```text
http://127.0.0.1:5000/health
```

Metrics endpoint:

```text
http://127.0.0.1:5000/metrics
```

Submit a booking and verify it in MongoDB Atlas Data Explorer:

```text
karan_trailquest -> bookings
```

---

## Phase 6 — Docker Compose

Build and run:

```bash
docker compose up --build
```

Check containers:

```bash
docker compose ps
```

Health check:

```bash
curl http://127.0.0.1:5000/health
```

Metrics check:

```bash
curl http://127.0.0.1:5000/metrics
```

Stop:

```bash
docker compose down
```

---

## Phase 7 — Local Kubernetes checks

Check the kind cluster:

```bash
kind get clusters
kubectl get nodes
```

Check ingress:

```bash
kubectl get ingressclass
kubectl get pods -n ingress-nginx
```

Check Metrics Server:

```bash
kubectl top nodes
```

NGINX Ingress Controller and Metrics Server must be working before testing HPA.

---

## Phase 8 — Kubernetes secret

Create the local secret file:

```bash
cp k8s/secret.example.yml k8s/secret.yml
```

Edit:

```text
k8s/secret.yml
```

Replace the placeholder with the real MongoDB Atlas URI.

The secret must use:

```text
namespace: karan-trailquest
secret name: karan-trailquest-secret
key: MONGO_URI
```

Never commit:

```text
k8s/secret.yml
```

Verify that Git ignores it:

```bash
git status --short
```

---

## Phase 9 — Build and deploy to local Kubernetes

Build the Docker image according to the local kind workflow.

Deploy using:

```bash
IMAGE_REPO=karan1989/karan-trailquest \
IMAGE_TAG=latest \
bash scripts/deploy.sh
```

Verify:

```bash
kubectl get all -n karan-trailquest
kubectl get ingress -n karan-trailquest
kubectl get hpa -n karan-trailquest
kubectl top pods -n karan-trailquest
```

---

## Phase 10 — Local friendly URL

For local Kubernetes testing, add a hosts entry that resolves:

```text
trailquest.local
```

to the address used by the local NGINX Ingress setup.

Then open:

```text
http://trailquest.local
```

---

## Phase 11 — EC2 environment checks

Before deploying to EC2, verify all dependencies.

Run:

```bash
git --version
python3 --version
docker --version
docker compose version
kubectl version --client
kind version
kind get clusters
kubectl get nodes
sudo systemctl status jenkins
kubectl get ingressclass
kubectl get pods -A | grep ingress
kubectl top nodes
```

Verify Jenkins can access Kubernetes:

```bash
sudo -u jenkins kubectl get nodes
```

Do not deploy until the required components are healthy.

---

## Phase 12 — EC2 prerequisites

Required components:

- Docker
- kind Kubernetes cluster
- kubectl
- Jenkins
- Jenkins access to kubeconfig
- NGINX Ingress Controller
- Metrics Server
- Docker Hub credentials in Jenkins
- Jenkins Secret File credential for MongoDB
- Prometheus
- Grafana
- Prometheus Operator
- EC2 Security Group allowing required traffic

The Kubernetes namespace used by the application is:

```text
karan-trailquest
```

The monitoring namespace is:

```text
monitoring
```

---

## Phase 13 — Jenkins credentials

Docker Hub Jenkins credential:

```text
dockerhub-credentials
```

MongoDB Kubernetes secret credential:

```text
mongodb-k8s-secret
```

The Jenkins credential `mongodb-k8s-secret` must be a Secret File containing the real Kubernetes Secret manifest.

It must use:

```text
namespace: karan-trailquest
secret name: karan-trailquest-secret
key: MONGO_URI
```

Never paste real credentials into the Jenkinsfile or Git repository.

---

## Phase 14 — Jenkins CI/CD deployment

The Jenkins pipeline performs:

1. Git checkout
2. Python syntax check
3. Dependency installation
4. Unit tests
5. Docker image build
6. Docker Hub push
7. Kubernetes deployment
8. ServiceMonitor deployment when the CRD exists
9. Rollout verification
10. Health check

Docker image repository:

```text
karan1989/karan-trailquest
```

Each Jenkins build uses the Jenkins build number as the Docker image tag.

Example:

```text
karan1989/karan-trailquest:<BUILD_NUMBER>
```

After Jenkins completes successfully, verify:

```bash
kubectl get pods -n karan-trailquest
kubectl get svc -n karan-trailquest
kubectl get ingress -n karan-trailquest
kubectl get hpa -n karan-trailquest
kubectl top pods -n karan-trailquest
```

The application is exposed using NGINX Ingress on standard HTTP rather than an application port such as `:5000`.

EC2 application hostname:

```text
trailquest.ec2
```

Application URL:

```text
http://trailquest.ec2
```

---

## Phase 15 — Horizontal Pod Autoscaler

Final HPA configuration:

```text
Minimum replicas: 2
Maximum replicas: 5
CPU target: 10%
```

Verify:

```bash
kubectl get hpa -n karan-trailquest
```

Expected pattern:

```text
cpu: <current>%/10%
MINPODS: 2
MAXPODS: 5
```

Check current pod CPU:

```bash
kubectl top pods -n karan-trailquest
```

### HPA load test

Generate HTTP traffic:

```bash
kubectl run load-generator -n karan-trailquest \
  --image=busybox:1.36 \
  --restart=Never \
  -- /bin/sh -c 'for i in 1 2 3 4 5; do while true; do wget -q -O- http://karan-trailquest-service/ >/dev/null; done & done; wait'
```

Monitor scaling:

```bash
kubectl get hpa -n karan-trailquest -w
```

Check pods:

```bash
kubectl get pods -n karan-trailquest
```

Delete the load generator:

```bash
kubectl delete pod load-generator -n karan-trailquest
```

After load decreases, HPA should eventually scale back toward the minimum replica count.

---

## Phase 16 — Application Prometheus metrics

The Flask application exposes:

```text
/metrics
```

Prometheus Python client dependency:

```text
prometheus-client
```

Custom metrics include:

```text
trailquest_http_requests_total
trailquest_http_request_duration_seconds
```

Request counter labels:

```text
method
route
status_code
```

The application intentionally uses:

```text
1 Gunicorn worker per Kubernetes pod
```

This keeps the Prometheus application counters consistent within each pod.

Kubernetes performs horizontal scaling across multiple pods.

---

## Phase 17 — ServiceMonitor

ServiceMonitor manifest:

```text
k8s/servicemonitor.yaml
```

Verify the ServiceMonitor:

```bash
kubectl get servicemonitor -n karan-trailquest
```

Detailed view:

```bash
kubectl describe servicemonitor karan-trailquest -n karan-trailquest
```

The ServiceMonitor tells Prometheus to scrape:

```text
/metrics
```

from the Karan TrailQuest Kubernetes Service.

Scrape configuration:

```text
interval: 15s
scrapeTimeout: 5s
```

The ServiceMonitor uses:

```text
release: monitoring
```

so that it is discovered by the kube-prometheus-stack Prometheus instance.

---

## Phase 18 — Prometheus monitoring

Prometheus runs inside:

```text
monitoring
```

Check monitoring pods:

```bash
kubectl get pods -n monitoring
```

Check application scrape targets using Prometheus.

### EC2 Prometheus port-forward

Run on EC2:

```bash
kubectl port-forward \
  -n monitoring \
  service/monitoring-kube-prometheus-prometheus \
  9090:9090
```

Keep this terminal running.

### Local SSH tunnel

Run from the local machine:

```bash
ssh -i "ec2-project-key.pem" \
  -L 9090:127.0.0.1:9090 \
  ubuntu@<EC2_PUBLIC_IP>
```

Open:

```text
http://127.0.0.1:9090
```

### Verify application targets

PromQL:

```promql
up{namespace="karan-trailquest"}
```

Expected value:

```text
1
```

for every current application target.

### Verify application metrics

```promql
trailquest_http_requests_total
```

Example route labels:

```text
route="health"
route="ready"
route="create_booking"
```

---

## Phase 19 — Grafana monitoring

Grafana runs inside the Kubernetes monitoring namespace.

### EC2 Grafana port-forward

Run on EC2:

```bash
kubectl port-forward \
  -n monitoring \
  service/monitoring-grafana \
  3000:80
```

Keep this terminal running.

### Local SSH tunnel

Run from the local machine:

```bash
ssh -i "ec2-project-key.pem" \
  -L 3000:127.0.0.1:3000 \
  ubuntu@<EC2_PUBLIC_IP>
```

Open:

```text
http://127.0.0.1:3000
```

Prometheus and Grafana remain private and are not directly exposed publicly.

---

## Phase 20 — Grafana HPA dashboard

Dashboard:

```text
Karan TrailQuest HPA Monitoring
```

Panels:

- Current Replicas
- Desired Replicas
- Minimum Replicas
- Maximum Replicas
- Current CPU %
- Target CPU %

### Current replicas

```promql
kube_horizontalpodautoscaler_status_current_replicas{
  namespace="karan-trailquest",
  horizontalpodautoscaler="karan-trailquest-hpa"
}
```

### Desired replicas

```promql
kube_horizontalpodautoscaler_status_desired_replicas{
  namespace="karan-trailquest",
  horizontalpodautoscaler="karan-trailquest-hpa"
}
```

### Minimum replicas

```promql
kube_horizontalpodautoscaler_spec_min_replicas{
  namespace="karan-trailquest",
  horizontalpodautoscaler="karan-trailquest-hpa"
}
```

### Maximum replicas

```promql
kube_horizontalpodautoscaler_spec_max_replicas{
  namespace="karan-trailquest",
  horizontalpodautoscaler="karan-trailquest-hpa"
}
```

### Current CPU %

```promql
100 *
sum(
  rate(container_cpu_usage_seconds_total{
    namespace="karan-trailquest",
    container="karan-trailquest"
  }[2m])
)
/
sum(
  kube_pod_container_resource_requests{
    namespace="karan-trailquest",
    container="karan-trailquest",
    resource="cpu",
    unit="core"
  }
)
```

### Target CPU %

```promql
kube_horizontalpodautoscaler_spec_target_metric{
  namespace="karan-trailquest",
  horizontalpodautoscaler="karan-trailquest-hpa",
  metric_name="cpu",
  metric_target_type="utilization"
}
```

Final target should show:

```text
10
```

---

## Phase 21 — Grafana application dashboard

Dashboard:

```text
Karan TrailQuest Application Monitoring
```

Panels:

- Request Rate
- HTTP Status Codes
- Average Response Time
- P95 Response Time
- Booking Requests
- App Availability

### Request Rate

```promql
sum by (route, method) (
  rate(trailquest_http_requests_total[5m])
)
```

### HTTP Status Codes

```promql
sum by (status_code) (
  rate(trailquest_http_requests_total[5m])
)
```

### Average Response Time

Milliseconds:

```promql
1000 *
sum(
  rate(trailquest_http_request_duration_seconds_sum[5m])
)
/
sum(
  rate(trailquest_http_request_duration_seconds_count[5m])
)
```

### P95 Response Time

Milliseconds:

```promql
1000 *
histogram_quantile(
  0.95,
  sum by (le) (
    rate(trailquest_http_request_duration_seconds_bucket[5m])
  )
)
```

### Successful Booking Requests

```promql
sum(
  trailquest_http_requests_total{
    route="create_booking",
    status_code="201"
  }
)
```

### App Availability

```promql
min(
  up{
    namespace="karan-trailquest",
    job="karan-trailquest-service"
  }
)
```

Interpretation:

```text
1 = healthy
0 = at least one target is unavailable
```

---

## Phase 22 — Final application verification

Check Kubernetes nodes:

```bash
kubectl get nodes
```

Check app pods:

```bash
kubectl get pods -n karan-trailquest
```

Check service:

```bash
kubectl get svc -n karan-trailquest
```

Check ingress:

```bash
kubectl get ingress -n karan-trailquest
```

Check HPA:

```bash
kubectl get hpa -n karan-trailquest
```

Check resource usage:

```bash
kubectl top pods -n karan-trailquest
```

Check ServiceMonitor:

```bash
kubectl get servicemonitor -n karan-trailquest
```

Check monitoring stack:

```bash
kubectl get pods -n monitoring
```

Test health endpoint:

```bash
curl http://trailquest.ec2/health
```

Test application:

```text
http://trailquest.ec2
```

Submit a booking and verify:

1. Browser receives a successful booking reference.
2. MongoDB Atlas contains the booking.
3. Prometheus receives the new application metric.
4. Grafana Booking Requests panel updates.

---

## Phase 23 — EC2 stop/start checklist

EC2 Public IPv4 may change after an instance stop/start.

After starting EC2 again, first check the new Public IPv4 address.

### Update local hosts file

Check:

```bash
grep trailquest.ec2 /etc/hosts
```

The entry should be:

```text
<EC2_PUBLIC_IP> trailquest.ec2
```

Update the old IP when required.

### Update MongoDB Atlas

MongoDB Atlas Network Access must contain:

```text
<EC2_PUBLIC_IP>/32
```

Wait until the entry shows:

```text
Active
```

### SSH to EC2

```bash
ssh -i "ec2-project-key.pem" ubuntu@<EC2_PUBLIC_IP>
```

### Check Kubernetes

```bash
kubectl get nodes
kubectl get pods -n karan-trailquest
kubectl get hpa -n karan-trailquest
kubectl get pods -n monitoring
kubectl get servicemonitor -n karan-trailquest
```

### Recreate monitoring access

Prometheus and Grafana port-forward processes do not survive an EC2 stop/start.

Restart their Kubernetes port-forwards and local SSH tunnels when required.

---

## Phase 24 — Networking notes

The TrailQuest application is accessed directly through Kubernetes NGINX Ingress:

```text
http://trailquest.ec2
```

No application port-forward is required for normal access.

Prometheus and Grafana remain private and use:

```text
kubectl port-forward
+
SSH local tunnel
```

for access.

### Office network filtering

Some office networks using FortiGuard or similar filtering may block:

```text
http://trailquest.ec2
```

because it is a custom local hostname.

The application has been verified to work using a mobile hotspot.

This type of block is a network policy issue, not a Kubernetes or application failure.

---

## Phase 25 — Security rules

Never commit:

```text
.env
k8s/secret.yml
```

Never store the MongoDB URI directly inside:

- GitHub
- Jenkinsfile
- Dockerfile
- Kubernetes Deployment YAML

Never place GitHub Personal Access Tokens directly inside the Git remote URL.

Use normal credential handling instead.

Prometheus and Grafana should remain private unless authentication and secure exposure are configured.

---

## Phase 26 — Final project architecture

```text
User Browser
     |
     v
EC2 Public IP
     |
     v
NGINX Ingress
     |
     v
Kubernetes Service
     |
     v
Flask Application Pods
     |
     v
MongoDB Atlas
```

CI/CD:

```text
GitHub
   |
   v
Jenkins
   |
   +--> Run Tests
   |
   +--> Build Docker Image
   |
   +--> Push to Docker Hub
   |
   +--> Deploy to Kubernetes
   |
   +--> Health Check
```

Monitoring:

```text
Flask /metrics
      |
      v
ServiceMonitor
      |
      v
Prometheus
      |
      v
Grafana
```

Autoscaling:

```text
Metrics Server
      |
      v
HPA
      |
      v
Karan TrailQuest Deployment
      |
      v
2 to 5 Pods
```

---

## Final Project Status

The Karan TrailQuest DevOps project includes:

- Flask application
- MongoDB Atlas database
- Input validation
- Automated unit tests
- Docker containerization
- Docker Compose
- Docker Hub image publishing
- Jenkins CI/CD
- Kubernetes Deployment
- Kubernetes Service
- NGINX Ingress
- Kubernetes Secrets
- Readiness and liveness probes
- Metrics Server
- Horizontal Pod Autoscaling
- Prometheus monitoring
- Flask custom Prometheus metrics
- Prometheus ServiceMonitor
- Grafana HPA dashboard
- Grafana application dashboard
- EC2 deployment
- End-to-end booking verification
- Monitoring and autoscaling verification

Main application URL:

```text
http://trailquest.ec2
```

Final HPA configuration:

```text
Minimum replicas: 2
Maximum replicas: 5
CPU target: 10%
```

The main DevOps project is complete.
