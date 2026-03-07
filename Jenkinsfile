pipeline {
    agent any

    stages {

        stage('Clone Repo') {
            steps {
                git branch: 'development', url: 'https://github.com/tamanna-bits/aceest-fitness-gym-devops.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m pip install --upgrade pip
                python3 -m pip install poetry
                poetry config virtualenvs.create false
                poetry install --no-interaction --no-ansi --no-root
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh 'poetry run pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness-gym-devops:latest .'
            }
        }

    }
}