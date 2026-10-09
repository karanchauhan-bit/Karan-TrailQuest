pipeline {
    agent any

    environment {
        IMAGE_REPO = "karan1989/karan-trailquest"
        IMAGE_TAG = "${BUILD_NUMBER}"
        K8S_NAMESPACE = "karan-trailquest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                sh 'python3 -m py_compile app.py'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    rm -rf .venv
                    python3 -m venv .venv
                    .venv/bin/python -m pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/python -m unittest discover -s tests -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t ${IMAGE_REPO}:${IMAGE_TAG} \
                      -t ${IMAGE_REPO}:latest \
                      .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USERNAME',
                        passwordVariable: 'DOCKERHUB_PASSWORD'
                    )
                ]) {
                    sh '''
                        echo "$DOCKERHUB_PASSWORD" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
                        docker push ${IMAGE_REPO}:${IMAGE_TAG}
                        docker push ${IMAGE_REPO}:latest
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    file(credentialsId: 'mongodb-k8s-secret', variable: 'K8S_SECRET_FILE')
                ]) {
                    sh '''
                        set -e
                        cp "$K8S_SECRET_FILE" k8s/secret.yml
                        chmod 600 k8s/secret.yml

                        IMAGE_REPO="${IMAGE_REPO}" \
                        IMAGE_TAG="${IMAGE_TAG}" \
                        K8S_NAMESPACE="${K8S_NAMESPACE}" \
                        bash scripts/deploy.sh

                        rm -f k8s/secret.yml
                    '''
                }
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    set -e
                    kubectl -n "${K8S_NAMESPACE}" port-forward service/karan-trailquest-service 5000:80 \
                      > /tmp/karan-trailquest-port-forward.log 2>&1 &
                    PORT_FORWARD_PID=$!
                    trap 'kill "$PORT_FORWARD_PID" 2>/dev/null || true' EXIT
                    sleep 5
                    APP_URL="http://127.0.0.1:5000/health" bash scripts/health_check.sh
                '''
            }
        }
    }

    post {
        always {
            sh 'rm -f k8s/secret.yml || true; rm -rf .venv || true'
        }
        success {
            echo "Karan TrailQuest deployed successfully: ${IMAGE_REPO}:${IMAGE_TAG}"
        }
        failure {
            echo 'Pipeline failed. Check the stage logs above.'
        }
    }
}
