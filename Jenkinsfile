// ═══════════════════════════════════════════════════════════════════════════
//  ACEest Fitness & Gym – Jenkinsfile
//  Stages: Checkout → Test → SonarQube → Build Image → Push → Deploy
// ═══════════════════════════════════════════════════════════════════════════

pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO = "yourdockerhubuser/aceest-fitness"
        DOCKER_CREDENTIALS = "dockerhub-creds"          // Jenkins credential ID
        SONAR_HOST_URL    = "http://sonarqube:9000"
        SONAR_TOKEN       = credentials("sonar-token")  // Jenkins credential ID
        IMAGE_TAG         = "${env.BUILD_NUMBER}"
        KUBE_NAMESPACE    = "aceest"
    }

    triggers {
        // Poll SCM every 2 minutes for changes
        pollSCM("H/2 * * * *")
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: "10"))
        timestamps()
        timeout(time: 30, unit: "MINUTES")
    }

    stages {

        // ── 1. CHECKOUT ─────────────────────────────────────────────────────
        stage("Checkout") {
            steps {
                checkout scm
                echo "Branch: ${env.GIT_BRANCH}  |  Commit: ${env.GIT_COMMIT}"
            }
        }

        // ── 2. UNIT TESTS ───────────────────────────────────────────────────
        stage("Unit Tests") {
            steps {
                sh """
                    pip install --no-cache-dir -r requirements.txt
                    python -m pytest tests/ -v \
                        --junitxml=reports/junit.xml \
                        --cov=app \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=term-missing
                """
            }
            post {
                always {
                    junit "reports/junit.xml"
                }
            }
        }

        // ── 3. SONARQUBE ANALYSIS ────────────────────────────────────────────
        stage("SonarQube Analysis") {
            steps {
                withSonarQubeEnv("SonarQube") {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=aceest-fitness \
                          -Dsonar.sources=app \
                          -Dsonar.tests=tests \
                          -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_TOKEN}
                    """
                }
            }
        }

        // ── 4. QUALITY GATE ──────────────────────────────────────────────────
        stage("Quality Gate") {
            steps {
                timeout(time: 5, unit: "MINUTES") {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // ── 5. BUILD DOCKER IMAGE ────────────────────────────────────────────
        stage("Build Docker Image") {
            steps {
                sh """
                    docker build \
                        --target production \
                        -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} \
                        -t ${DOCKER_HUB_REPO}:latest \
                        .
                """
            }
        }

        // ── 6. PUSH TO DOCKER HUB ────────────────────────────────────────────
        stage("Push to Docker Hub") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDENTIALS}",
                    usernameVariable: "DOCKER_USER",
                    passwordVariable: "DOCKER_PASS"
                )]) {
                    sh """
                        echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                        docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
                        docker push ${DOCKER_HUB_REPO}:latest
                        docker logout
                    """
                }
            }
        }

        // ── 7. DEPLOY (Rolling Update by default) ────────────────────────────
        stage("Deploy – Rolling Update") {
            when { branch "main" }
            steps {
                sh """
                    kubectl set image deployment/aceest-deployment \
                        aceest=${DOCKER_HUB_REPO}:${IMAGE_TAG} \
                        -n ${KUBE_NAMESPACE}

                    kubectl rollout status deployment/aceest-deployment \
                        -n ${KUBE_NAMESPACE} \
                        --timeout=120s
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS – Image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}"
        }
        failure {
            echo "Pipeline FAILED – Triggering rollback"
            sh "kubectl rollout undo deployment/aceest-deployment -n ${KUBE_NAMESPACE} || true"
        }
        always {
            cleanWs()
        }
    }
}
