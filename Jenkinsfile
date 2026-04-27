pipeline {
    agent any

    environment {
        DOCKER_HUB_REPO    = "${env.DOCKERHUB_USER}/${env.DOCKERHUB_REPO}"
        SONAR_HOST_URL     = "${env.SONAR_HOST}"
        KUBE_NAMESPACE     = "${env.KUBE_NS}"
        KUBECONFIG         = "${env.KUBE_CONFIG}"

        DOCKER_CREDENTIALS = credentials("dockerhub-creds")
        SONAR_TOKEN        = credentials("sonar-token")

        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        BUILD_TOOL         = "${env.BUILD_TOOL ?: 'docker'}"
    }

    triggers {
        githubPush()
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
                echo "Build tool: ${env.BUILD_TOOL}"
                echo "Image: ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}"
            }
        }

        // ── 2. UNIT TESTS ───────────────────────────────────────────────────
        stage("Unit Tests") {
            steps {
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --no-cache-dir -r requirements.txt
                    pytest tests/ -v \
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
                          -Dsonar.host.url=${env.SONAR_HOST_URL} \
                          -Dsonar.login=${env.SONAR_TOKEN}
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

        // ── 5. BUILD IMAGE ───────────────────────────────────────────────────
        stage("Build Image") {
            steps {
                script {
                    def buildCmd = env.BUILD_TOOL == "podman" ? "podman" : "docker"
                    sh """
                        ${buildCmd} build \
                            --target production \
                            -t ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} \
                            -t ${env.DOCKER_HUB_REPO}:latest \
                            .
                    """
                }
            }
        }

        // ── 6. PUSH TO DOCKER HUB ────────────────────────────────────────────
        stage("Push to Docker Hub") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${env.DOCKER_CREDENTIALS}",
                    usernameVariable: "DOCKER_USER",
                    passwordVariable: "DOCKER_PASS"
                )]) {
                    script {
                        def buildCmd = env.BUILD_TOOL == "podman" ? "podman" : "docker"
                        def registry = env.BUILD_TOOL == "podman" ? "docker.io" : ""
                        sh """
                            echo ${DOCKER_PASS} | ${buildCmd} login ${registry} -u ${DOCKER_USER} --password-stdin
                            ${buildCmd} push ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}
                            ${buildCmd} push ${env.DOCKER_HUB_REPO}:latest
                            ${buildCmd} logout ${registry}
                        """
                    }
                }
            }
        }

        // ── 7. DEPLOY (Rolling Update) ────────────────────────────────────────
        stage("Deploy – Rolling Update") {
            when { branch "main" }
            steps {
                sh """
                    kubectl set image deployment/aceest-deployment \
                        aceest=${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG} \
                        -n ${env.KUBE_NAMESPACE}

                    kubectl rollout status deployment/aceest-deployment \
                        -n ${env.KUBE_NAMESPACE} \
                        --timeout=120s
                """
            }
        }
    }

    post {
        success {
            echo "Pipeline SUCCESS – Image: ${env.DOCKER_HUB_REPO}:${env.IMAGE_TAG}"
        }
        failure {
            echo "Pipeline FAILED – Triggering rollback"
            sh "kubectl rollout undo deployment/aceest-deployment -n ${env.KUBE_NAMESPACE} || true"
        }
        always {
            cleanWs()
        }
    }
}