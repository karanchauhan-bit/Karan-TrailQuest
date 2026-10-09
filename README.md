# Karan TrailQuest

Customer-facing adventure tour booking application built with Flask, MongoDB Atlas, Docker, Jenkins and Kubernetes.

## Features

- Responsive adventure travel interface
- Destination cards with **Explore** modal
- **Explore Destinations** smooth-scroll navigation
- Booking form with client-side and server-side validation
- Email format validation
- Exactly 10-digit phone validation
- Destination dropdown + custom destination option
- Travelers dropdown + 6–30 custom group size
- Past travel dates rejected
- MongoDB Atlas booking storage
- Docker / Docker Compose local workflow
- Kubernetes Deployment + Service + NGINX Ingress
- HPA: 2–5 replicas at 60% CPU target
- Readiness and liveness probes
- Jenkins CI/CD pipeline
- Real Kubernetes secret excluded from Git

## Booking data

MongoDB Atlas database:

`karan_trailquest`

Collection:

`bookings`

## Local URL

Direct Flask/Docker testing:

`http://127.0.0.1:5000`

After local Kubernetes + NGINX Ingress setup:

`http://trailquest.local`

## Important secret rule

Never commit:

`k8s/secret.yml`

Use `k8s/secret.example.yml` only as a template.

See `PROJECT_NOTEBOOK.md` for the local-first and EC2 deployment workflow.
