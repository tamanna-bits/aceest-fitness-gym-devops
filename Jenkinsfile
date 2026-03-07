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
                python3 -m poetry config virtualenvs.create false
                python3 -m poetry install --no-interaction --no-ansi --no-root
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m poetry run pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'python3 -m docker build -t aceest-fitness-gym-devops .'
            }
        }

    }
}