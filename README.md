# Github Actions
Repository to store [reusable Github Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows).

## Pull Request Build
Supposed to be run on pull-request to test if project will build.
To add this action to your repo create `.github/workflows/pull-request.yml` file with following content:
```yaml
name: 'PR Build'

on:
  workflow_dispatch:
  pull_request:
    branches:
      - master
      - 'master-legacy'
      - 'hotfix/**'
    paths-ignore:
      - 'README.md'
      - '.github/**'

jobs:
  build:
    name: 'Zenoo Build'
    uses: zenoolabs/github-actions/.github/workflows/pull-request.yml@v4
    secrets:
      nexus-username: ${{ secrets.NEXUS_USERNAME }}
      nexus-password: ${{ secrets.NEXUS_PASSWORD }}
```

## Release
Supposed to be run on push to master branch to tag new version and upload it to Nexus.
To add this action to your repo create `.github/workflows/release.yml` file with following content:
```yaml
name: Release

on:
  workflow_dispatch:
  push:
    branches:
      - master
      - 'master-legacy'
      - 'hotfix/**'
    paths-ignore:
      - 'README.md'
      - '.github/**'

jobs:
  release:
    name: 'Zenoo Release'
    uses: zenoolabs/github-actions/.github/workflows/release.yml@v4
    secrets:
      nexus-username: ${{ secrets.NEXUS_USERNAME }}
      nexus-password: ${{ secrets.NEXUS_PASSWORD }}
```

## Build & Deploy Container
This action first builds the container image and pushes to AWS Container Registry (ECR) with the help of [JIB Gradle plugin](https://github.com/GoogleContainerTools/jib/tree/master/jib-gradle-plugin) defined in backend. At the last step, it deploys the container to AWS Container Service (ECS) via CLI.

For details, see the workflow steps in [deploy.yml](./.github/workflows/deploy.yml).

To add this action to your repo create `.github/workflows/deploy.yml` file with following content and update inputs and secrets accordingly:

```yaml
name: 'Build & Deploy Container'

on:
  workflow_dispatch:
    inputs:
      command:
        required: true
        type: choice
        description: Deploy/Restart/Down/Start/Stop/Process
        options:
          - deploy
          - restart
          - down
          - start
          - stop
          - ps

jobs:
 buildAndDeploy:
    name: 'Build and deploy container'
    uses: zenoolabs/github-actions/.github/workflows/deploy.yml@v9
    secrets:
      nexus-username: ${{ secrets.NEXUS_USERNAME }}
      nexus-password: ${{ secrets.NEXUS_PASSWORD }}      
      aws-access-key: ${{ secrets.AWS_ACCESS_KEY }}
      aws-secret-key: ${{ secrets.AWS_SECRET_KEY }}
    with:
      region: us-west-2
      cluster: test-us-cluster
      config-name: test-us-config
      profile-name: test-us-profile
      launch-type: EC2
      project-name: hub-instance-template
      target-group-arn: arn:aws:elasticloadbalancing:us-west-2:123456789:targetgroup/hub-instance-template-test-us/8449abe109770c92
      container-name: hub-instance-template
      container-port: 8080
      image-repo: 917319201960.dkr.ecr.us-west-2.amazonaws.com/hub-instance-template:v0.0.1
      docker-folder: docker/test-us
      build-image: true
```

## SonarQube Static Code Analysis Report
Creates SonarQube report. For details, see the workflow steps in [sonarqube.yml](./.github/workflows/sonarqube.yml).

To add this action to your repo create `.github/workflows/sonarqube.yml` file with following content and update inputs and secrets accordingly:
```yaml
name: 'SonarQube Static Code Analysis Report'

on:
  workflow_dispatch:
  pull_request:
    branches:
      - master
      - 'master-legacy'
      - 'hotfix/**'
    paths-ignore:
      - 'README.md'
      - '.github/**'

jobs:
  build:
    name: 'SonarQube SCA Report'
    uses: zenoolabs/github-actions/.github/workflows/sonarqube.yml@v5
    secrets:
      sonarqube-host: ${{ secrets.SONARQUBE_HOST }}
      sonarqube-token: ${{ secrets.SONARQUBE_TOKEN }}
      nexus-username: ${{ secrets.NEXUS_USERNAME }}
      nexus-password: ${{ secrets.NEXUS_PASSWORD }}
    with:
      sonar-project-key: hub      
```
