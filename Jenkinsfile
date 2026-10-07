pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        IMAGE_REPO = "karan1989/karan-devops-dashboard"
        IMAGE_TAG = "${BUILD_NUMBER}"
        K8S_NAMESPACE = "karan-dashboard"
        MONGO_DB_NAME = "karan_dashboard"
    }

    stages {

        stage("Checkout") {
            steps {
                echo "Downloading source code from GitHub..."
                checkout scm
            }
        }

        stage("Python Syntax Check") {
            steps {
                sh "python3 -m py_compile app.py"
            }
        }

        stage("Install Dependencies") {
            steps {
                sh """
                    python3 -m venv .jenkins-venv
                    .jenkins-venv/bin/pip install -r requirements.txt
                """
            }
        }

        stage("Run Tests") {
            steps {
                sh """
                    .jenkins-venv/bin/python -m unittest discover -s tests -v
                """
            }
        }

        stage("Build Docker Image") {
            steps {
                sh """
                    docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -t ${IMAGE_REPO}:latest .
                """
            }
        }

        stage("Push Docker Image") {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "dockerhub-credentials",
                        usernameVariable: "DOCKERHUB_USERNAME",
                        passwordVariable: "DOCKERHUB_PASSWORD"
                    )
                ]) {
                    sh '''
                        set -e
                        echo "$DOCKERHUB_PASSWORD" | docker login --username "$DOCKERHUB_USERNAME" --password-stdin
                        docker push "$IMAGE_REPO:$IMAGE_TAG"
                        docker push "$IMAGE_REPO:latest"
                        docker logout
                    '''
                }
            }
        }

        stage("Deploy to Kubernetes") {
            steps {
                withCredentials([
                    string(
                        credentialsId: "mongodb-atlas-uri",
                        variable: "MONGO_URI"
                    )
                ]) {
                    sh '''
                        set -e
                        IMAGE_REPO="$IMAGE_REPO"                         IMAGE_TAG="$IMAGE_TAG"                         K8S_NAMESPACE="$K8S_NAMESPACE"                         MONGO_URI="$MONGO_URI"                         bash scripts/deploy.sh
                    '''
                }
            }
        }

        stage("Health Check") {
            steps {
                sh '''
                    set -e
                    K8S_NAMESPACE="$K8S_NAMESPACE" bash scripts/health_check.sh
                '''
            }
        }
    }

    post {
        success {
            echo "Karan DevOps Dashboard deployed successfully with MongoDB Atlas."
        }
        failure {
            echo "Karan DevOps Dashboard Jenkins pipeline failed. Check console output."
        }
        always {
            sh '''
                kubectl get pods -n "$K8S_NAMESPACE" || true
                kubectl get svc -n "$K8S_NAMESPACE" || true
                ps aux | grep '[k]ubectl port-forward' || true
            '''
        }
    }
}
