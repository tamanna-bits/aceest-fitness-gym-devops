pipeline {
    agent any

    stages {

        stage('Clone Repo') {
            steps {
                git 'https://github.com/tamanna-bits/aceest-fitness-gym-devops'
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh '''
                pip install poetry
                poetry config virtualenvs.create false
                poetry install --no-interaction --no-ansi --no-root
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t aceest-fitness-gym-devops .'
            }
        }
    }
}