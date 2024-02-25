pipeline {
  agent any
  stages {
    stage("verify tooling") {
      steps {
        sh '''
          docker version
          docker info
          docker compose version 
          curl --version
        '''
      }
    }
    stage('Prune Docker data') {
      steps {
        sh 'docker system prune -all --volumes'
      }
    }
    // stage('Start container') {
    //   steps {
    //     sh 'docker compose up -d --no-color --wait'
    //     sh 'docker compose ps'
    //   }
    // }
  }
}