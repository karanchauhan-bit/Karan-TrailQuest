#!/usr/bin/env bash
set -euo pipefail

IMAGE_REPO="${IMAGE_REPO:-karan1989/karan-trailquest}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
NAMESPACE="${K8S_NAMESPACE:-karan-trailquest}"
DEPLOYMENT_NAME="karan-trailquest-app"

required_files=(
  k8s/namespace.yaml
  k8s/configmap.yaml
  k8s/secret.yml
  k8s/app-service.yaml
  k8s/app-deployment.yaml
  k8s/ingress.yaml
  k8s/hpa.yaml
)

command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl not found."; exit 1; }

for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "ERROR: required file not found: $file"; exit 1; }
done

echo "Deploying Karan TrailQuest"
echo "Namespace : $NAMESPACE"
echo "Image     : ${IMAGE_REPO}:${IMAGE_TAG}"

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/app-service.yaml

sed \
  -e "s|IMAGE_REPOSITORY_PLACEHOLDER|${IMAGE_REPO}|g" \
  -e "s|IMAGE_TAG_PLACEHOLDER|${IMAGE_TAG}|g" \
  k8s/app-deployment.yaml | kubectl apply -f -

kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

kubectl rollout status deployment/${DEPLOYMENT_NAME} -n "$NAMESPACE" --timeout=180s

echo
echo "Pods:"
kubectl get pods -n "$NAMESPACE" -o wide

echo
echo "Services:"
kubectl get svc -n "$NAMESPACE"

echo
echo "Ingress:"
kubectl get ingress -n "$NAMESPACE"

echo
echo "HPA:"
kubectl get hpa -n "$NAMESPACE"
