pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "mouaidnasab/workoutanalysis"
        DOCKER_CREDENTIALS_ID = "c2df98b1-ff47-4992-a415-a7235de00f8a"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Mouaidnasab/Workout-Analysis.git'
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image('python:3.9').inside {
                        sh 'apt-get update && apt-get install -y libgl1-mesa-glx'
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
                    sh 'docker stop my-app || true'
                    sh 'docker rm my-app || true'
                    sh """
                        docker run -d --name my-app -p 3000:3000 ${DOCKER_IMAGE}:${env.BUILD_NUMBER} /bin/bash -c '
                        apt-get update && apt-get install -y libgl1-mesa-glx &&
                        python app.py'
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
