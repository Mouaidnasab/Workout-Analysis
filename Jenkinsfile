pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "your-dockerhub-username/your-repo-name"
        DOCKER_CREDENTIALS_ID = "your-docker-credentials-id"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/your-repo-name.git'
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image('python:3.9').inside {
                        sh 'pip install -r requirements.txt'
                        sh 'python -m unittest discover -s tests'
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
                    DOCKER_IMAGE = docker.build("${env.DOCKER_IMAGE}:${env.BUILD_NUMBER}")
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
                        DOCKER_IMAGE.push("${env.BUILD_NUMBER}")
                        DOCKER_IMAGE.push("latest")
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
                    // Stop and remove the old container (if any)
                    sh 'docker stop my-app || true'
                    sh 'docker rm my-app || true'

                    // Run the new container
                    sh "docker run -d --name my-app -p 8080:8080 ${env.DOCKER_IMAGE}:latest"
                }
            }
        }
    }

    post {
        always {
            cleanWs() // Clean workspace after build
        }
        failure {
            echo 'Pipeline failed, no deployment will be performed.'
        }
        success {
            echo 'Pipeline succeeded, image deployed.'
        }
    }
}
