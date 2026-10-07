#!/bin/bash
set -e

NAMESPACE="${K8S_NAMESPACE:-karan-dashboard}"
IMAGE_REPO="${IMAGE_REPO:-YOUR_DOCKERHUB_USERNAME/karan-devops-dashboard}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
MONGO_URI="${MONGO_URI:-}"

echo "Deploying Karan DevOps Dashboard with MongoDB Atlas"

if [[ "$IMAGE_REPO" == "YOUR_DOCKERHUB_USERNAME/"* ]]; then
  echo "ERROR: Replace YOUR_DOCKERHUB_USERNAME."
  exit 1
fi

if [[ -z "$MONGO_URI" ]]; then
  echo "ERROR: MONGO_URI is not configured."
  exit 1
fi

kubectl apply -f k8s/namespace.yaml

kubectl create secret generic karan-mongodb-secret   --namespace "$NAMESPACE"   --from-literal=MONGO_URI="$MONGO_URI"   --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/app-service.yaml

sed   -e "s|IMAGE_REPOSITORY_PLACEHOLDER|$IMAGE_REPO|g"   -e "s|IMAGE_TAG_PLACEHOLDER|$IMAGE_TAG|g"   k8s/app-deployment.yaml | kubectl apply -f -

kubectl rollout status deployment/karan-devops-dashboard   -n "$NAMESPACE" --timeout=180s

kubectl get pods -n "$NAMESPACE"
kubectl get svc -n "$NAMESPACE"
