pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "mouaidnasab/workoutanalysis"
        BASE_IMAGE = "mouaidnasab/workoutanalysis-base:latest"
        DOCKER_CREDENTIALS_ID = "c2df98b1-ff47-4992-a415-a7235de00f8a"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Mouaidnasab/Workout-Analysis.git'
            }
        }

        stage('Setup Environment') {
            steps {
                // Install necessary system packages
                sh 'apt-get update && apt-get install -y chromium-driver python3-venv'
                
                // Create a virtual environment
                sh 'python3 -m venv venv'
                
                // Activate the virtual environment and install Python packages
                sh '''
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install selenium webdriver_manager
                '''
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image(env.BASE_IMAGE).inside {
                        // Running tests without the need to install other dependencies
                            sh '''
                                . venv/bin/activate
                                python -m unittest discover -s tests
                            '''
                    }
                }
            }
            post {
                failure {
                    script {
                        currentBuild.result = 'FAILURE'
                        echo 'Tests failed! Stopping pipeline.'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { currentBuild.result == null }
            }
            steps {
                script {
                    def customImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_NUMBER}")
                    customImage.tag('latest')
                    env.DOCKER_IMAGE = customImage.imageName()
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { currentBuild.result == null }
            }
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                        docker.image("${env.DOCKER_IMAGE}").push("${env.BUILD_NUMBER}")
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression { currentBuild.result == null }
            }
            steps {
                script {
                    // Stop and remove the existing container if it exists
                    sh 'docker stop my-app || true'
                    sh 'docker rm my-app || true'
                    // Run the container with the pre-installed dependencies
                    sh """
                        docker run -d --name my-app -p 5500:3000 ${DOCKER_IMAGE}:${env.BUILD_NUMBER} flask run --host=0.0.0.0 --port=3000
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            echo 'Pipeline failed, no deployment will be performed.'
        }
        success {
            echo 'Pipeline succeeded, image deployed.'
        }
    }
}
