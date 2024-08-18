pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Mouaidnasab/Workout-Analysis'
            }
        }
        stage('Install Pip') {
            steps {
                // Download and install pip if it's not available
                sh 'curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py'
                sh 'python3 get-pip.py --user'
            }
        }
        stage('Install Dependencies') {
            steps {
                // Use the locally installed pip
                sh '~/.local/bin/pip install --upgrade pip'
                sh '~/.local/bin/pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                // Run the tests using the specified python interpreter
                sh 'python3 -m unittest discover -s .'
            }
        }
    }
}
