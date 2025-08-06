pipeline {
    agent any
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'prod'],
            description: 'Target deployment environment'
        )
        choice(
            name: 'ACTION',
            choices: ['deploy', 'stop', 'restart', 'logs'],
            description: 'Container action to perform'
        )
        string(
            name: 'PORT',
            defaultValue: '8080',
            description: 'Port to expose the container on (default: 8080)'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip running tests'
        )
        booleanParam(
            name: 'FORCE_REBUILD',
            defaultValue: false,
            description: 'Force rebuild of Docker image (ignore cache)'
        )
    }
    
    environment {
        // Container and image names
        IMAGE_NAME = "static-website"
        CONTAINER_NAME = "${IMAGE_NAME}-${params.ENVIRONMENT}"
        IMAGE_TAG = "${IMAGE_NAME}:${params.ENVIRONMENT}-${BUILD_NUMBER}"
        IMAGE_LATEST = "${IMAGE_NAME}:${params.ENVIRONMENT}-latest"
        
        // Network for container communication (use default bridge network)
        DOCKER_NETWORK = "bridge"
        
        // Deployment settings
        DEPLOY_PORT = "${params.PORT}"
        
        // Docker socket access (Windows Docker Desktop)
        DOCKER_HOST = "tcp://host.docker.internal:2375"
    }
    
    triggers {
        // Poll SCM every 5 minutes for changes
        pollSCM('H/5 * * * *')
        
        // GitHub webhook trigger (configure in GitHub repo settings)
        githubPush()
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Clean workspace and checkout code
                deleteDir()
                checkout scm
                
                script {
                    echo "🚀 Starting deployment for environment: ${params.ENVIRONMENT}"
                    echo "📦 Container name: ${CONTAINER_NAME}"
                    echo "🖼️  Image tag: ${IMAGE_TAG}"
                    echo "🔌 Port: ${DEPLOY_PORT}"
                    echo "⚡ Action: ${params.ACTION}"
                }
            }
        }
        
        stage('Pre-flight Checks') {
            steps {
                script {
                    // Check if Docker is available
                    def dockerCheck = sh(
                        script: 'command -v docker',
                        returnStatus: true
                    )
                    
                    if (dockerCheck != 0) {
                        error("❌ Docker is not installed or not accessible")
                    }
                    
                    echo "✅ Docker binary found"
                    
                    // Test Docker daemon access
                    def dockerAccessCheck = sh(
                        script: 'docker info --format "{{.ServerVersion}}"',
                        returnStatus: true
                    )
                    
                    if (dockerAccessCheck != 0) {
                        sh '''
                            echo "⚠️  Docker daemon access issue detected"
                            echo "🔧 Attempting to fix permissions..."
                            
                            # Try to fix permissions (may not work in all environments)
                            ls -la /var/run/docker.sock || echo "Cannot list docker socket"
                            
                            echo "📋 Current user and groups:"
                            whoami
                            groups
                            
                            echo "❌ Docker daemon is not accessible"
                            echo "💡 Solution: Run these commands on the host:"
                            echo "   docker exec -u root jenkins usermod -aG docker jenkins"
                            echo "   sudo chmod 666 /var/run/docker.sock"
                            echo "   docker restart jenkins"
                        '''
                        error("Docker daemon permission denied")
                    }
                    
                    sh '''
                        echo "✅ Docker version:"
                        docker --version
                        
                        echo "✅ Docker daemon accessible"
                        echo "Server version: $(docker info --format '{{.ServerVersion}}')"
                    '''
                    
                    // Don't try to create default bridge network - it already exists
                    sh '''
                        echo "✅ Using default Docker bridge network"
                        docker network ls | grep bridge || echo "Bridge network info not available"
                    '''
                    
                    // Check if port is available (if deploying)
                    if (params.ACTION == 'deploy') {
                        sh '''
                            if netstat -tuln | grep ":${DEPLOY_PORT} "; then
                                echo "⚠️  Port ${DEPLOY_PORT} is already in use"
                                echo "📋 Processes using port ${DEPLOY_PORT}:"
                                ss -tulnp | grep ":${DEPLOY_PORT} " || lsof -i :${DEPLOY_PORT} || echo "Could not determine process"
                            else
                                echo "✅ Port ${DEPLOY_PORT} is available"
                            fi
                        '''
                    }
                }
            }
        }
        
        stage('Validate Python Code') {
            when {
                allOf {
                    anyOf {
                        expression { params.ACTION == 'deploy' }
                        expression { params.ACTION == 'restart' }
                    }
                    expression { !params.SKIP_TESTS }
                }
            }
            steps {
                script {
                    // Check Python syntax
                    sh '''
                        echo "🐍 Validating Python code..."
                        
                        # Check if Python is available
                        if command -v python3 >/dev/null 2>&1; then
                            PYTHON_CMD="python3"
                        elif command -v python >/dev/null 2>&1; then
                            PYTHON_CMD="python"
                        else
                            echo "❌ Python is not installed"
                            echo "💡 Installing Python3..."
                            apt-get update && apt-get install -y python3 python3-pip
                            PYTHON_CMD="python3"
                        fi
                        
                        echo "✅ Using Python: $PYTHON_CMD"
                        $PYTHON_CMD --version
                        
                        # Find all Python files and check syntax
                        find . -name "*.py" -type f | while read -r file; do
                            echo "Checking syntax: $file"
                            $PYTHON_CMD -m py_compile "$file" || exit 1
                        done
                        
                        echo "✅ Python syntax validation passed"
                    '''
                    
                    // Check for requirements.txt and validate
                    sh '''
                        if [ -f requirements.txt ]; then
                            echo "📋 Found requirements.txt, validating..."
                            pip3 install --dry-run -r requirements.txt > /dev/null || echo "⚠️  Some requirements may not be installable"
                        else
                            echo "ℹ️  No requirements.txt found"
                        fi
                    '''
                }
            }
        }
        
        stage('Stop Existing Container') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy' }
                    expression { params.ACTION == 'stop' }
                    expression { params.ACTION == 'restart' }
                }
            }
            steps {
                script {
                    sh '''
                        echo "🛑 Stopping existing container if running..."
                        
                        if docker ps -q -f name=${CONTAINER_NAME}; then
                            echo "📦 Found running container: ${CONTAINER_NAME}"
                            docker stop ${CONTAINER_NAME} || true
                            docker rm ${CONTAINER_NAME} || true
                            echo "✅ Container ${CONTAINER_NAME} stopped and removed"
                        else
                            echo "ℹ️  No running container found with name: ${CONTAINER_NAME}"
                        fi
                        
                        # Clean up any orphaned containers
                        docker container prune -f || true
                    '''
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy' }
                    expression { params.ACTION == 'restart' }
                }
            }
            steps {
                script {
                    // Build Docker image
                    def buildArgs = params.FORCE_REBUILD ? '--no-cache' : ''
                    
                    sh """
                        echo "🔨 Building Docker image..."
                        echo "📁 Build context: \$(pwd)"
                        echo "🏗️  Build args: ${buildArgs}"
                        
                        # Build the image
                        docker build ${buildArgs} -t ${IMAGE_TAG} -t ${IMAGE_LATEST} .
                        
                        echo "✅ Docker image built successfully"
                        docker images | grep ${IMAGE_NAME} | head -5
                    """
                }
            }
        }
        
        stage('Test Docker Image') {
            when {
                allOf {
                    anyOf {
                        expression { params.ACTION == 'deploy' }
                        expression { params.ACTION == 'restart' }
                    }
                    expression { !params.SKIP_TESTS }
                }
            }
            steps {
                script {
                    sh '''
                        echo "🧪 Testing Docker image..."
                        
                        # Start container in test mode on default network
                        TEST_CONTAINER="${CONTAINER_NAME}-test"
                        docker run -d --name ${TEST_CONTAINER} ${IMAGE_TAG}
                        
                        # Wait for container to be ready
                        echo "⏳ Waiting for container to start..."
                        sleep 5
                        
                        # Test if the site is accessible using container name
                        echo "🔍 Testing container directly: ${TEST_CONTAINER}"
                        
                        # Test if the site is accessible
                        SUCCESS=false
                        for i in 1 2 3 4 5 6 7 8 9 10; do
                            if curl -f --max-time 5 "http://${TEST_CONTAINER}/" > /dev/null 2>&1; then
                                echo "✅ Website is accessible on attempt $i!"
                                SUCCESS=true
                                break
                            else
                                echo "⏳ Attempt $i/10 failed, retrying..."
                                sleep 2
                            fi
                        done
                        
                        if [ "$SUCCESS" = "false" ]; then
                            echo "❌ Website test failed after 10 attempts"
                            echo "📋 Container logs:"
                            docker logs ${TEST_CONTAINER}
                            echo "📋 Container inspect:"
                            docker inspect ${TEST_CONTAINER} --format='{{.NetworkSettings.IPAddress}}'
                            docker stop ${TEST_CONTAINER} || true
                            docker rm ${TEST_CONTAINER} || true
                            exit 1
                        fi
                        
                        # Check response content
                        RESPONSE=$(curl -s "http://${TEST_CONTAINER}/")
                        echo "📄 Response preview:"
                        echo "${RESPONSE}" | head -3
                        
                        # Cleanup test container
                        docker stop ${TEST_CONTAINER} || true
                        docker rm ${TEST_CONTAINER} || true
                        
                        echo "✅ Docker image test passed"
                    '''
                }
            }
        }
        
        stage('Deploy Container') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy' }
                    expression { params.ACTION == 'restart' }
                }
            }
            steps {
                script {
                    sh '''
                        echo "🚀 Deploying container..."
                        
                        # Run the new container on default network
                        docker run -d \\
                            --name ${CONTAINER_NAME} \\
                            --restart unless-stopped \\
                            -p ${DEPLOY_PORT}:80 \\
                            -l "app=static-website" \\
                            -l "environment=${ENVIRONMENT}" \\
                            -l "version=${BUILD_NUMBER}" \\
                            -l "jenkins-job=${JOB_NAME}" \\
                            ${IMAGE_TAG}
                        
                        echo "✅ Container ${CONTAINER_NAME} started successfully"
                        
                        # Wait for container to be ready
                        echo "⏳ Waiting for container to be ready..."
                        sleep 3
                        
                        # Show container info
                        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                    '''
                }
            }
        }
        
        stage('Health Check') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy' }
                    expression { params.ACTION == 'restart' }
                }
            }
            steps {
                script {
                    sh '''
                        echo "🏥 Performing health check..."
                        
                        # Wait for service to be fully ready
                        SUCCESS=false
                        for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
                            # Try container name first, then localhost as fallback
                            if curl -f --max-time 5 "http://${CONTAINER_NAME}/" > /dev/null 2>&1; then
                                echo "✅ Health check passed on attempt $i (using container name)"
                                SUCCESS=true
                                break
                            elif curl -f --max-time 5 "http://host.docker.internal:${DEPLOY_PORT}/" > /dev/null 2>&1; then
                                echo "✅ Health check passed on attempt $i (using host.docker.internal)"
                                SUCCESS=true
                                break
                            else
                                echo "⏳ Health check attempt $i/15 failed, retrying..."
                                sleep 2
                            fi
                        done
                        
                        if [ "$SUCCESS" = "false" ]; then
                            echo "❌ Health check failed after 15 attempts"
                            echo "📋 Container logs:"
                            docker logs ${CONTAINER_NAME} --tail 20
                            echo "📋 Container network info:"
                            docker inspect ${CONTAINER_NAME} --format='{{.NetworkSettings.IPAddress}}'
                            exit 1
                        fi
                        
                        # Test website response using container name
                        echo "📄 Website response test:"
                        if RESPONSE=$(curl -s "http://${CONTAINER_NAME}/"); then
                            if echo "${RESPONSE}" | grep -q "html\\|HTML"; then
                                echo "✅ Valid HTML response detected"
                            else
                                echo "⚠️  Response may not be valid HTML"
                            fi
                        else
                            echo "⚠️  Could not fetch response for testing"
                        fi
                        
                        echo "🌐 Website should be accessible at: http://localhost:${DEPLOY_PORT}"
                        echo "🔗 (Container network name: ${CONTAINER_NAME})"
                    '''
                }
            }
        }
        
        stage('Show Logs') {
            when {
                expression { params.ACTION == 'logs' }
            }
            steps {
                script {
                    sh '''
                        echo "📋 Container logs for: ${CONTAINER_NAME}"
                        
                        if docker ps -q -f name=${CONTAINER_NAME}; then
                            echo "=== RECENT LOGS ==="
                            docker logs ${CONTAINER_NAME} --tail 50 --timestamps
                            
                            echo "\\n=== CONTAINER STATUS ==="
                            docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                            
                            echo "\\n=== CONTAINER STATS ==="
                            docker stats ${CONTAINER_NAME} --no-stream --format "table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}"
                        else
                            echo "❌ Container ${CONTAINER_NAME} is not running"
                            echo "Available containers:"
                            docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
                        fi
                    '''
                }
            }
        }
        
        stage('Cleanup Old Images') {
            when {
                anyOf {
                    expression { params.ACTION == 'deploy' }
                    expression { params.ACTION == 'restart' }
                }
            }
            steps {
                script {
                    sh '''
                        echo "🧹 Cleaning up old images..."
                        
                        # Keep the last 3 images for this environment
                        docker images ${IMAGE_NAME} --format "{{.Tag}} {{.ID}}" | \\
                        grep "${ENVIRONMENT}-[0-9]" | \\
                        sort -V -r | \\
                        tail -n +4 | \\
                        awk '{print $2}' | \\
                        xargs -r docker rmi || echo "No old images to remove"
                        
                        # Cleanup dangling images
                        docker image prune -f || true
                        
                        echo "✅ Image cleanup completed"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Show deployment summary
                def summary = """
                🎯 **Deployment Summary**
                
                **Environment:** ${params.ENVIRONMENT}
                **Action:** ${params.ACTION}
                **Build:** #${BUILD_NUMBER}
                **Container:** ${CONTAINER_NAME}
                **Image:** ${IMAGE_TAG}
                """
                
                if (params.ACTION in ['deploy', 'restart']) {
                    summary += """
                **URL:** http://localhost:${DEPLOY_PORT}
                **Port:** ${DEPLOY_PORT}
                """
                }
                
                echo summary
            }
            
            // Archive build artifacts
            archiveArtifacts artifacts: 'Dockerfile', fingerprint: true, allowEmptyArchive: true
            
            // Clean workspace
            cleanWs(deleteDirs: true, disableDeferredWipeout: true)
        }
        
        success {
            script {
                echo "🎉 Pipeline completed successfully!"
                
                if (params.ACTION in ['deploy', 'restart']) {
                    echo """
                    ✅ Your static website is now running!
                    🌐 Access it at: http://localhost:${DEPLOY_PORT}
                    📦 Container: ${CONTAINER_NAME}
                    🏷️  Image: ${IMAGE_TAG}
                    
                    📋 Useful Docker commands:
                    docker logs ${CONTAINER_NAME}           # View logs
                    docker stop ${CONTAINER_NAME}           # Stop container
                    docker start ${CONTAINER_NAME}          # Start container
                    docker exec -it ${CONTAINER_NAME} sh    # Shell access
                    """
                }
                
                // Store deployment info for other jobs
                writeFile file: 'deployment-info.json', text: """
                {
                    "environment": "${params.ENVIRONMENT}",
                    "container_name": "${CONTAINER_NAME}",
                    "image_tag": "${IMAGE_TAG}",
                    "port": "${DEPLOY_PORT}",
                    "build_number": "${BUILD_NUMBER}",
                    "timestamp": "${new Date().format('yyyy-MM-dd HH:mm:ss')}",
                    "url": "http://localhost:${DEPLOY_PORT}"
                }
                """
                archiveArtifacts artifacts: 'deployment-info.json', fingerprint: true
            }
        }
        
        failure {
            script {
                echo "❌ Pipeline failed!"
                
                // Show container logs if they exist
                sh '''
                    if docker ps -a -q -f name=${CONTAINER_NAME}; then
                        echo "📋 Container logs:"
                        docker logs ${CONTAINER_NAME} --tail 20 || true
                    fi
                    
                    echo "🔍 Available containers:"
                    docker ps -a --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" || true
                    
                    echo "🖼️  Available images:"
                    docker images ${IMAGE_NAME} || true
                '''
            }
        }
        
        unstable {
            echo "⚠️ Pipeline completed with warnings"
        }
    }
}