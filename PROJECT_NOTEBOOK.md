# Karan TrailQuest — Project Notebook

This notebook is intentionally local-first. Complete and verify each phase before moving to EC2.

## Phase 1 — Pull and inspect

```bash
git pull origin main
git status
tree -a -L 3
```

## Phase 2 — Local environment checks

```bash
python3 --version
git --version
docker --version
docker compose version
kubectl version --client
kind version
```

## Phase 3 — Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Phase 4 — MongoDB Atlas

Create a free Atlas cluster, database user and network access rule.

Copy the example:

```bash
cp .env.example .env
```

Edit `.env` and set your real `MONGO_URI`.

Database name:

`karan_trailquest`

Customer bookings are stored in:

`bookings`

## Phase 5 — Run Flask locally

```bash
source .venv/bin/activate
python app.py
```

Open:

`http://127.0.0.1:5000`

Submit a booking and verify it in MongoDB Atlas Data Explorer under:

`karan_trailquest -> bookings`

## Phase 6 — Docker Compose

```bash
docker compose up --build
docker compose ps
curl http://127.0.0.1:5000/health
```

Stop:

```bash
docker compose down
```

## Phase 7 — Local Kubernetes checks

```bash
kind get clusters
kubectl get nodes
kubectl get ingressclass
kubectl get pods -n ingress-nginx
kubectl top nodes
```

NGINX Ingress Controller and Metrics Server must be working before the final Kubernetes test.

## Phase 8 — Local Kubernetes secret

Create a local-only file:

```bash
cp k8s/secret.example.yml k8s/secret.yml
```

Edit `k8s/secret.yml` and replace the placeholder with the real Atlas URI.

Do not commit this file.

## Phase 9 — Build an image for local Kubernetes

Build/tag the Docker image according to your local kind workflow, then deploy:

```bash
IMAGE_REPO=karan1989/karan-trailquest IMAGE_TAG=latest bash scripts/deploy.sh
```

Verify:

```bash
kubectl get all -n karan-trailquest
kubectl get ingress -n karan-trailquest
kubectl get hpa -n karan-trailquest
kubectl top pods -n karan-trailquest
```

## Phase 10 — Local friendly URL

Add a hosts entry that resolves `trailquest.local` to the address used by your local Ingress setup.

Then open:

`http://trailquest.local`

## Phase 11 — EC2 environment checks FIRST

Do not deploy immediately. Check all dependencies first:

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

Also verify Jenkins can access Kubernetes:

```bash
sudo -u jenkins kubectl get nodes
```

Only after these checks pass should missing components be installed/configured.

## Phase 12 — EC2 prerequisites

Required:

- Docker
- kind cluster
- kubectl
- Jenkins
- Jenkins kubeconfig access
- NGINX Ingress Controller
- Metrics Server
- Docker Hub credentials in Jenkins
- Jenkins Secret File credential named `mongodb-k8s-secret`
- EC2 Security Group allowing HTTP 80 and later HTTPS 443

## Phase 13 — Jenkins secret file

The Jenkins credential `mongodb-k8s-secret` must be a **Secret file** containing the real Kubernetes Secret manifest.

It must use:

- namespace: `karan-trailquest`
- secret name: `karan-trailquest-secret`
- key: `MONGO_URI`

## Phase 14 — Final EC2 deployment

Run the Jenkins pipeline and verify:

```bash
kubectl get pods -n karan-trailquest
kubectl get svc -n karan-trailquest
kubectl get ingress -n karan-trailquest
kubectl get hpa -n karan-trailquest
kubectl top pods -n karan-trailquest
```

The public application should be exposed through NGINX on standard HTTP/HTTPS, not an application port such as `:5000` or `:5050`.
