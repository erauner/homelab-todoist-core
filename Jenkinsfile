#!/usr/bin/env groovy
/**
 * Jenkinsfile for homelab-todoist-core
 *
 * Builds and publishes the shared Python package to Nexus PyPI.
 */

@Library('homelab') _

def podYaml = '''
apiVersion: v1
kind: Pod
metadata:
  labels:
    workload-type: ci-builds
spec:
  imagePullSecrets:
  - name: nexus-registry-credentials
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:3355.v388858a_47b_33-3-jdk21
    resources:
      requests:
        cpu: 100m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi
  - name: python
    image: python:3.12-slim
    command: ['cat']
    tty: true
    resources:
      requests:
        cpu: 200m
        memory: 512Mi
      limits:
        cpu: 1000m
        memory: 1Gi
'''

pipeline {
    agent {
        kubernetes {
            yaml podYaml
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 15, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        NEXUS_PYPI_URL = 'https://nexus.erauner.dev/repository/pypi-hosted/'
    }

    stages {
        stage('Setup') {
            steps {
                container('python') {
                    sh 'pip install uv --quiet'
                    sh 'uv sync --extra dev'
                }
            }
        }

        stage('Lint') {
            steps {
                container('python') {
                    sh 'uv run ruff check src/ tests/'
                }
            }
        }

        stage('Test') {
            steps {
                container('python') {
                    sh 'uv run pytest tests/ -v --tb=short'
                }
            }
        }

        stage('Build') {
            steps {
                container('python') {
                    sh 'uv build'
                }
            }
        }

        stage('Publish to Nexus') {
            when {
                anyOf {
                    branch 'main'
                    tag pattern: 'v*', comparator: 'GLOB'
                }
            }
            steps {
                container('python') {
                    withCredentials([usernamePassword(
                        credentialsId: 'nexus-credentials',
                        usernameVariable: 'NEXUS_USER',
                        passwordVariable: 'NEXUS_PASS'
                    )]) {
                        sh '''
                            pip install twine --quiet
                            twine upload \
                                --repository-url ${NEXUS_PYPI_URL} \
                                --username ${NEXUS_USER} \
                                --password ${NEXUS_PASS} \
                                dist/*
                        '''
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                homelab.postFailurePrComment([repo: 'erauner/homelab-todoist-core'])
                homelab.notifyDiscordFailure()
            }
        }
    }
}
