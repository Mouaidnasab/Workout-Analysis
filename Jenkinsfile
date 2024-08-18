pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Mouaidnasab/Workout-Analysis'
            }
        }
        stage('Install Dependencies') {
            steps {
                // Install dependencies globally
                sh 'pip install --upgrade pip'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                // Run the tests using the globally installed packages
                sh 'python -m unittest discover -s .'
            }
        }
    }
}
