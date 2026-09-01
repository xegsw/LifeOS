# Contributing to LifeOS

LifeOS uses GitHub as the engineering execution surface and the files under `lifeos/` as the product-governance system. GitHub does not replace the authoritative ledgers.

## 1. Source-of-truth order

When records conflict, follow the hierarchy already defined by the project:

1. `lifeos/DECISION_LOG.md`, `lifeos/FREEZE_STATUS.md`, and `lifeos/TASK_REGISTRY.md`
2. `lifeos/CURRENT_STATUS.md`
3. Issues, pull requests, comments, and chat context

Stop and reconcile the authoritative files before proceeding when the first layer conflicts internally.

## 2. Branch model

Use trunk-based development with short-lived branches. `main` is the integration and release branch.

Preferred branch names:

```text
feat/LIFEOS-P3-135-stable-product-root
fix/LIFEOS-P3-136-runtime-boundary
research/LIFEOS-P3-137-packaging-spike
chore/github-engineering-foundation
```

Do not create a permanent `develop` branch. A branch should represent one bounded outcome or one repository-maintenance change.

## 3. Issue and task mapping

A product, architecture, or governance change should map to one canonical LifeOS task ID.

```text
LifeOS task ID
  ↕
GitHub Issue
  ↕
short-lived branch
  ↕
Pull Request
  ↕
CI and evidence
  ↕
PM decision / ledger update
```

Repository-maintenance work may omit a new P-task only when it does not change product scope, acceptance, frozen assets, runtime behavior, or a governed decision. Mark that explicitly in the pull request.

## 4. Commits

Use clear, imperative commits. Conventional prefixes are encouraged:

```text
feat: ...
fix: ...
test: ...
docs: ...
refactor: ...
chore: ...
```

Do not mix unrelated formatting, generated evidence, governance changes, and runtime behavior in one commit unless the task contract requires them together.

## 5. Pull requests

Every pull request must:

- state its LifeOS task or maintenance classification;
- describe the observable outcome;
- identify fixed inputs and non-goals;
- provide exact verification commands and evidence paths;
- disclose risk, fail-closed behavior, and rollback;
- avoid declaring `Accepted`, `Frozen`, stage entry, or product release solely from the PR;
- pass required CI before merge.

Use squash merge by default so one merged PR maps cleanly to one outcome. Preserve merge commits only when retaining branch topology is itself useful evidence.

## 6. CI baseline

The initial CI is deliberately narrow:

- Python syntax checks for tracked helper scripts;
- JSON parsing for the current candidate;
- checks for authoritative entry-point files;
- `cargo fmt`, `cargo check`, and `cargo test` for the current P3-134 candidate.

The current candidate path is a temporary binding. It must be changed when the code is promoted to a stable product root.

## 7. Product code location

Until a separate promotion task is accepted, the current runnable candidate remains:

```text
lifeos/engineering/LIFEOS-P3-134/candidate
```

Do not silently treat this task-scoped directory as a permanent application root. The intended next structural step is to promote an accepted baseline into a stable path such as `apps/desktop/`, while retaining task evidence and historical candidates as read-only records.

## 8. Versions and releases

Use Semantic Versioning for product releases:

- `MAJOR`: incompatible product or contract change;
- `MINOR`: backward-compatible user capability;
- `PATCH`: backward-compatible correction.

Stage labels, P-task numbers, architecture versions, and Git tags are different dimensions. A task becoming Complete does not automatically create a product release.

A release requires:

1. an accepted stable product baseline;
2. a version decision;
3. passing release checks;
4. release notes;
5. a Git tag such as `v0.1.0`;
6. a GitHub Release linked to the tag.

## 9. Sensitive and generated material

Never commit credentials, personal source data, local databases, runtime roots, build caches, signing keys, or machine-specific secrets. Evidence should be minimized, redacted where needed, and traceable to its governing task.
