pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Set up Python') {
            steps {
                sh 'python3 --version'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        stage('Run tests') {
            steps {
                sh 'python3 -m unittest discover -s tests -v'
            }
        }
    }
}
