pipeline {
    agent any

    environment {
        PORT = '8001'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Deploy Keycloak with Docker Compose') {
            steps {
                script {
                    // Stop and remove existing containers
                    sh '''
                        docker-compose -f docker-compose.yml down || true
                    '''

                    // Start updated containers (with --build if images need rebuild)
                    sh '''
                        docker-compose -f docker-compose.yml up -d
                    '''
                }
            }
        }
        stage('Set up Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip setuptools wheel
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run FastAPI Server') {
            steps {
                sh '''
                    source ${VENV_DIR}/bin/activate
                    PYTHONPATH=proyecto uvicorn src.main:app --reload --host 0.0.0.0 --port ${PORT} &
                '''
            }
        }
    }
}
