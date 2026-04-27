# ACEest – Git Branching & Tagging Strategy

## Branch Model (GitFlow-inspired)

```
main          ← production-ready code only
development       ← integration branch; all features merge here first
feature/*     ← one branch per feature (e.g. feature/add-calorie-api)
bugfix/*      ← targeted fixes (e.g. bugfix/fix-negative-age)
release/*     ← release stabilisation (e.g. release/v2.0)
hotfix/*      ← urgent production patches (e.g. hotfix/v1.0.1)
```

## Commit Message Convention (Conventional Commits)

```
feat:     new feature          →  triggers minor version bump
fix:      bug fix              →  triggers patch bump
perf:     performance improvement → triggers patch bump
test:     adding/updating tests
ci:       pipeline changes
docs:     documentation only
refactor: code restructure, no behaviour change
chore:    dependency bumps, config changes
```

### Examples

```bash
git commit -m "feat: add calorie calculator endpoint"
git commit -m "fix: reject negative age in member creation"
git commit -m "test: add 31 unit tests for gym routes"
git commit -m "ci: add SonarQube quality gate to Jenkinsfile"
```

## Tagging Strategy (Semantic Versioning)

```bash
# Tag a release
git tag -a v1.0.0 -m "Initial Flask API release"
git tag -a v1.1.0 -m "Add calorie calc + validation"
git tag -a v2.0.0 -m "SQLite persistence + progress tracking"
git tag -a v2.1.0 -m "Matplotlib progress charts"
git tag -a v3.0.0 -m "Full dashboard + login + PDF reports"

# Push tags to remote
git push origin --tags
```

## Workflow – Feature to Production

```
git checkout development
git checkout -b feature/my-feature

... commit work ...

git push origin feature/my-feature
Open Pull Request → development
CI runs (pytest + SonarQube)
Code review + approval
Merge → development
```

## Hotfix Workflow

```
Branch from main (not development)

git checkout -b hotfix/v1.0.1 main

... apply fix ...

git checkout main && git merge --no-ff hotfix/v1.0.1
git tag -a v1.0.1 -m "Hotfix: <description>"
git checkout development && git merge --no-ff hotfix/v1.0.1
git branch -d hotfix/v1.0.1
```

## Rollback

```bash
# Inspect a previous tag (read-only – detached HEAD)
git checkout v2.0.0

# Create a working branch from a tag if you need to commit from it
git checkout -b rollback/v2.0.0 v2.0.0

# Roll back Kubernetes deployment
kubectl rollout undo deployment/aceest-deployment -n aceest

# Roll back to specific revision
kubectl rollout undo deployment/aceest-deployment --to-revision=3 -n aceest
```
