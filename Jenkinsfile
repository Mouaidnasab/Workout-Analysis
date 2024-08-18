pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                // Checkout the code from the repository
                git branch: 'main', url: 'https://github.com/Mouaidnasab/Workout-Analysis'
            }
        }
        stage('Build') {
            steps {
                // Example build step (replace with your build command)
                sh 'echo "Building the project..."'
            }
        }
        stage('Test') {
            steps {
                // Example test step (replace with your test command)
                sh 'echo "Running tests..."'
            }
        }
        stage('Deploy') {
            steps {
                // Example deploy step (replace with your deploy command)
                sh 'echo "Deploying the project..."'
            }
        }
    }
}
