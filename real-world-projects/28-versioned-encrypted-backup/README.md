# 28. Versioned Encrypted Backup Tool

## Problem
Back up a folder incrementally and keep encrypted, restorable versions.

## What you will build
- Detect changed files by hashing against the last run.
- Copy only new or changed files.
- Encrypt each backup and keep a timestamped version.
- Restore any version on demand.

## Concepts practiced
- Change detection
- Encryption
- Versioning

## Libraries
- hashlib
- cryptography
- shutil

## Stretch goals
- Prune old versions on a retention policy.
- Compress each backup.

## Status
- [ ] Not started
