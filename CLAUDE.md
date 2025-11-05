# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains **reusable GitHub Actions workflows** for automating CI/CD pipelines. These workflows are designed to be referenced by other repositories using the `uses:` syntax in GitHub Actions.

**Technology Stack:**
- GitHub Actions (reusable workflows)
- Java/Gradle build system (JDK 21)
- AWS ECS (Elastic Container Service) for deployments
- Docker/ECR for container images
- SonarQube for static code analysis

## Architecture

### Workflow Types

This repository provides several workflow categories:

1. **Build & Test Workflows**
   - `pull-request.yml` - PR builds with Gradle tests
   - `pull-request-legacy.yml` - Legacy PR build workflow

2. **Release Workflows**
   - `release.yml` - Main release workflow (Docker or JAR publishing)
   - `release-legacy.yml` - Legacy release workflow
   - `auto-tag.yml` - Automatic semantic versioning on merge to main

3. **Container Workflows**
   - `image-build.yml` - Build and publish Docker images
   - `image-deploy.yml` - Deploy images to ECS
   - `image-version.yml` - Version management for images

4. **Deployment Workflows**
   - `compose.yml` - ECS compose operations (deploy/scale/restart/stop/start)

5. **Quality Workflows**
   - `sonarqube.yml` - Static code analysis with optional dependency checking
   - `get-sonarqube-report.yml` - Download SonarQube reports

### Key Workflow Patterns

**Reusable Workflow Structure:**
All workflows use `workflow_call` as the trigger, making them reusable from other repositories via:
```yaml
uses: zenoolabs/github-actions/.github/workflows/<workflow-name>.yml@<version>
```

**AWS Authentication:**
- Modern workflows use OIDC role assumption (`aws-actions/configure-aws-credentials@v4`)
- Legacy workflows use access key/secret key pairs
- ECR authentication handled via `amazon-ecr-login` action

**Gradle Integration:**
- All builds use JDK 21 (Temurin distribution)
- Gradle caching enabled via `actions/setup-java`
- Nexus credentials passed via environment variables: `ORG_GRADLE_PROJECT_nexusUsername`, `ORG_GRADLE_PROJECT_nexusPassword`

**Version Management:**
- Versions extracted via `./gradlew cV -q -Prelease.quiet`
- Release workflow uses `createRelease` and `pushRelease` Gradle tasks
- Auto-tagging workflow bumps versions based on commit messages: `[major]`, `[minor]`, or patch (default)

## Important Conventions

### Release Workflow Inputs

The `release.yml` workflow is the primary release mechanism and supports:
- **docker_image** (boolean): Determines if Docker image or JAR is published
- **dispatch_event** (boolean): Triggers deployment repository updates
- **force_version** (string): Override automatic version detection
- **service_name**, **image_repo**, **deployment_repo**: Used for deployment dispatching

### Compose Workflow Commands

The `compose.yml` workflow accepts these commands via `workflow_dispatch`:
- `deploy` - Deploy new service with scaling
- `scale` - Scale existing service
- `restart` - Stop then start service
- `down/start/stop/ps` - Standard ECS-CLI compose commands
- **fargate-spot** (boolean): Enable Fargate Spot capacity provider

### SonarQube Workflow Options

The `sonarqube.yml` workflow has two modes:
- **Standard mode** (default): Build + SonarQube analysis
- **Full mode** (`full-run: true`): Adds dependency check + report download
- **enable-dependency-cache** (boolean, default: true): Cache OWASP dependency database

### Auto-Tagging Behavior

The `auto-tag.yml` workflow automatically creates version tags on push to `main`:
- Commit message with `[major]` or "breaking change" → major version bump
- Commit message with `[minor]` or "feature" → minor version bump
- Default → patch version bump
- Uses `github-actions[bot]` as committer

### Pull Request Workflow Options

The `pull-request.yml` workflow supports optional integration testing:
- **enable-integration-tests** (boolean, default: false): Enable integration test execution
- **integration-test-patterns** (string): Space-separated test patterns (e.g., `'*ClientAWorkflowsSpec* *ClientBWorkflowsSpec*'`)
- **max-parallel-forks** (number, default: 1): Maximum parallel forks for integration tests

Example usage:
```yaml
uses: zenoolabs/github-actions/.github/workflows/pull-request.yml@v4
with:
  enable-integration-tests: true
  integration-test-patterns: '*ClientAWorkflowsSpec* *ClientBWorkflowsSpec* *ClientCWorkflowsSpec*'
  max-parallel-forks: 3
```

## Common Development Tasks

### Updating Workflow Versions

When updating workflows that consuming repositories reference:
1. Make changes to the workflow file in `.github/workflows/`
2. The `auto-tag.yml` workflow automatically creates a new version tag on merge to `main`
3. Consuming repositories can update their `uses:` reference to the new version

### Testing Workflow Changes

Workflows cannot be tested directly in this repository. To test:
1. Create a test repository that consumes the workflow
2. Reference the workflow using a branch name instead of version tag:
   ```yaml
   uses: zenoolabs/github-actions/.github/workflows/release.yml@feature-branch-name
   ```
3. Once validated, merge to `main` and a new version tag will be created

### ECS-CLI Usage

Both `compose.yml` and deployment workflows use ECS-CLI v1.21.0 via custom action `zenoolabs/setup-ecs-cli@v1.1.0`.

ECS-CLI requires:
- Cluster configuration (`ecs-cli configure`)
- Profile configuration with AWS credentials
- Docker compose file in specified `docker-folder`

## Secrets and Variables Required

Consuming repositories must provide these secrets:

**For Gradle builds:**
- `NEXUS_USERNAME`, `NEXUS_PASSWORD` - Nexus artifact repository

**For AWS operations:**
- Modern: `AWS_ECR_ASSUME_ROLE` (variable), `AWS_HOME_REGION` (variable), `AWS_ECR_ACCOUNT` (variable)
- Legacy: `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`

**For SonarQube:**
- `SONARQUBE_HOST`, `SONARQUBE_TOKEN`
- `NVD_API_KEY` (optional, for dependency checks)

**For deployment dispatch:**
- `ACTIONS_ACCESS_TOKEN` (GitHub personal access token)

## Gradle Assumptions

The workflows expect target repositories to have these Gradle tasks:
- `test` - Run tests
- `build` - Build project
- `integrationTest` - Run integration tests (optional, for PR workflow)
- `cV` - Print current version (with `-Prelease.quiet`)
- `createRelease` - Create release tag locally
- `pushRelease` - Push release tag to remote
- `publish` - Publish JAR to Nexus
- `jib` - Build and publish Docker image
- `dependencyCheckAnalyze` - OWASP dependency check
- `sonar` - SonarQube analysis

Properties used:
- `-PgithubRun` - Flag indicating GitHub Actions environment
- `-Prelease.forceVersion=<version>` - Override version
- `-Djib.to.image=<image:tag>` - Override Jib target image
- `-PmaxParallelForks=<number>` - Maximum parallel forks for integration tests