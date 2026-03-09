pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-u root:root'
        }
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Poetry') {
            steps {
                sh '''
                curl -sSL https://install.python-poetry.org | python3 -
                export PATH="$HOME/.local/bin:$PATH"
                poetry --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                export PATH="$HOME/.local/bin:$PATH"
                poetry config virtualenvs.create false
                poetry install --no-interaction --no-ansi --no-root
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                export PATH="$HOME/.local/bin:$PATH"
                poetry run pytest -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness-gym-devops:latest .'
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