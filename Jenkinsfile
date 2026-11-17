pipeline {
    agent any

    options {
        timestamps()
    }

    environment {
        WINDOWS_PYTHON = 'C:\\Users\\HP\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe'
    }

    stages {
        stage('Set up Python') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 --version'
                        sh 'python3 -m pip install -r requirements.txt'
                    } else {
                        bat '"%WINDOWS_PYTHON%" --version'
                        bat '"%WINDOWS_PYTHON%" -m pip install -r requirements.txt'
                    }
                }
            }
        }
        stage('Run tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'python3 -m unittest discover -s tests -v'
                    } else {
                        bat '"%WINDOWS_PYTHON%" -m unittest discover -s tests -v'
                    }
                }
            }
        }
    }
}
