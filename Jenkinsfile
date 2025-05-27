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
                        sh '''
                            docker-compose -f docker-compose.yml down || true

                            # Build images (if needed) and start containers
                            docker-compose -f docker-compose.yml up -d --build
                        ''' 
                    }
                }
            }
        }
    }
