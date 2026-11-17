pipeline {
    agent any

    options {
        timestamps()
    }

                script {
                    if (isUnix()) {
                        sh 'python3 --version'
                        sh 'python3 -m pip install -r requirements.txt'
                    } else {
                        bat 'py -3 --version'
                        bat 'py -3 -m pip install -r requirements.txt'
                    }
                }
            steps {
                sh 'python3 --version'
                sh 'python3 -m pip install -r requirements.txt'
            }
                script {
                    if (isUnix()) {
                        sh 'python3 -m unittest discover -s tests -v'
                    } else {
                        bat 'py -3 -m unittest discover -s tests -v'
                    }
                }

        stage('Run tests') {
            steps {
                sh 'python3 -m unittest discover -s tests -v'
            }
        }
    }
}
