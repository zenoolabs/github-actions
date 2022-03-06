# Github Actions
Repository to store [reusable Github Actions](https://docs.github.com/en/actions/using-workflows/reusing-workflows).

## Pull Request Build
Supposed to be run on pull-request to test if project will build.
To add this action to your repo create `.github/workflows/pull-request.yml` file with following content:
```
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
  call-workflow-in-another-repo:
    uses: zenoolabs/github-actions/.github/workflows/pull-request.yml@v1
```

## Release
Supposed to be run on push to master branch to tag new version and upload it to Nexus.
To add this action to your repo create `.github/workflows/release.yml` file with following content:
```
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
  call-workflow-in-another-repo:
    uses: zenoolabs/github-actions/.github/workflows/release.yml@v1
```
