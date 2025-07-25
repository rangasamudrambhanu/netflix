pipeline {
    agent any

    environment {
        IMAGE_NAME = 'bhanureddy/abctest'
        DOCKER_CREDENTIALS = 'dockerhub'           // Jenkins ID for Docker Hub credentials
        AWS_CREDENTIALS = 'aws-eks-creds'          // Jenkins ID for AWS IAM user credentials
    }

    stages {

        stage('Checkout Code') {
            steps {
                git url: 'https://github.com/rangasamudrambhanu/netflix.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${IMAGE_NAME}")
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    dockerImage.inside {
                        // Run your unit tests using pytest
                        sh 'pytest test_app.py'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS) {
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Clone GitOps Repo') {
            steps {
                dir('gitops') {
                    git url: 'https://github.com/rangasamudrambhanu/gitops.git', branch: 'main'
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([
                    file(credentialsId: 'eks-kubeconfig', variable: 'KUBECONFIG'),
                    [
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: "${AWS_CREDENTIALS}",
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]
                ]) {
                    sh '''
                        echo "✅ Using uploaded kubeconfig"
                        chmod 600 ${KUBECONFIG}

                        echo "📦 Deploying to Kubernetes"
                        kubectl version --client
                        kubectl apply -f gitops/namespace.yaml
                        kubectl apply -f gitops/deployment.yaml
                        kubectl apply -f gitops/service.yaml

                        echo "🌐 Fetching External IP of LoadBalancer"
                        kubectl get svc -n movieflix
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                sh 'docker image prune -f'
            }
        }
    }

    post {
        success {
            echo "✅ Build, test, push, and deploy completed successfully!"
        }
        failure {
            echo "❌ Something went wrong! Check the logs."
        }
    }
}
