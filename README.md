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
Supposed to be run on push to master branch to tag new version and upload it to Nexus or Docker repository depending on
the value of following input: `docker_image`.

To add this action to your repo create `.github/workflows/release.yml` file with following content:
```yaml
name: Release
run-name: "Release ${{github.ref_name}}"

on:
  workflow_dispatch:
    inputs:
      force_version:
        description: If specified, this version will be forced
        type: string
        required: false
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
    uses: zenoolabs/github-actions/.github/workflows/release.yml@v11
    secrets:
      nexus-username: ${{ secrets.NEXUS_USERNAME }}
      nexus-password: ${{ secrets.NEXUS_PASSWORD }}
      aws-access-key: ${{ secrets.AWS_ACCESS_KEY }}
      aws-secret-key: ${{ secrets.AWS_SECRET_KEY }}
    with:
      docker_image: true
      aws_region: 'eu-west-1'
```

## Compose
This action is used to execute compose steps via ecs-cli. It is mainly used for the deployment of container and should be
executed from the release tag.

For details, see the workflow steps in [compose.yml](./.github/workflows/compose.yml).

To add this action to your repo create `.github/workflows/compose.yml` file with following content and update inputs and
secrets accordingly:

```yaml
name: 'Compose'
run-name: "Compose ${{github.event.inputs.command}} ${{github.ref_name}}"

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
 compose:
    name: 'Compose'
    uses: zenoolabs/github-actions/.github/workflows/compose.yml@v11
    secrets:   
      aws-access-key: ${{ secrets.AWS_ACCESS_KEY }}
      aws-secret-key: ${{ secrets.AWS_SECRET_KEY }}
    with:
      region: eu-west-1
      cluster: test-us-cluster
      config-name: test-us-config
      profile-name: test-us-profile
      launch-type: EC2
      project-name: hub-instance-template
      target-group-arn: arn:aws:elasticloadbalancing:us-west-2:123456789:targetgroup/hub-instance-template-test-us/8449abe109770c92
      container-name: hub-instance-template
      container-port: 8080
      docker-folder: docker/test-us
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
