pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies & Run Tests (Docker)') {
            steps {
                sh '''
                docker run --rm \
                -v $PWD:/app \
                -w /app \
                python:3.11 \
                bash -c "
                pip install poetry &&
                export PATH=\\$HOME/.local/bin:\\$PATH &&
                poetry config virtualenvs.create false &&
                poetry install --no-interaction --no-ansi --no-root &&
                poetry run pytest -v
                "
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t aceest-fitness-gym-devops:latest .
                '''
            }
        }

    }

    post {
        success {
            echo 'Build Successful ✅'
        }
        failure {
            echo 'Build Failed ❌'
        }
        always {
            echo 'Pipeline Finished'
        }
    }
}