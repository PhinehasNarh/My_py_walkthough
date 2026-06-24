"""
28 - Versioned Encrypted Backup Tool
Project: Back up a folder incrementally and keep encrypted, restorable versions.

How it works:
  - Each file's content is identified by its SHA-256 hash and stored once, encrypted,
    in the backup repo. Unchanged files are not copied again (incremental + dedup).
  - Every backup writes a timestamped manifest mapping file paths to content hashes,
    so you can restore the exact state of any past version.
  - Files are encrypted with a key derived from your password (PBKDF2 + Fernet), so the
    backup repo holds no readable data.

Usage:
  python main.py backup ./my-folder ./backup-repo
  python main.py list ./backup-repo
  python main.py restore ./backup-repo <version> ./restore-here

Authorized use: back up your own data. Keep the password safe; it cannot be recovered.
"""

import argparse
import base64
import getpass
import hashlib
import json
from datetime import datetime
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=200_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def get_fernet(repo: Path, password: str) -> Fernet:
    salt_file = repo / "salt.bin"
    if salt_file.exists():
        salt = salt_file.read_bytes()
    else:
        salt = hashlib.sha256(str(datetime.now()).encode()).digest()[:16]
        salt_file.write_bytes(salt)
    return Fernet(derive_key(password, salt))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def backup(source: Path, repo: Path, password: str) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "blobs").mkdir(exist_ok=True)
    (repo / "versions").mkdir(exist_ok=True)
    fernet = get_fernet(repo, password)

    manifest = {}
    new_blobs = 0
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        digest = sha256_bytes(data)
        rel = str(path.relative_to(source)).replace("\\", "/")
        manifest[rel] = digest

        blob = repo / "blobs" / digest
        if not blob.exists():                      # store each unique content once
            blob.write_bytes(fernet.encrypt(data))
            new_blobs += 1

    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    (repo / "versions" / f"{version}.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Backed up {len(manifest)} file(s) as version {version} "
          f"({new_blobs} new encrypted blob(s), the rest were unchanged).")


def list_versions(repo: Path) -> None:
    versions = sorted((repo / "versions").glob("*.json"))
    if not versions:
        print("No versions in this repo.")
        return
    print("Versions:")
    for v in versions:
        manifest = json.loads(v.read_text(encoding="utf-8"))
        print(f"  {v.stem}  ({len(manifest)} files)")


def restore(repo: Path, version: str, dest: Path, password: str) -> None:
    manifest_file = repo / "versions" / f"{version}.json"
    if not manifest_file.exists():
        print(f"No such version: {version}")
        return
    fernet = get_fernet(repo, password)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    for rel, digest in manifest.items():
        blob = repo / "blobs" / digest
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(fernet.decrypt(blob.read_bytes()))
    print(f"Restored {len(manifest)} file(s) from version {version} into {dest}")


def main():
    parser = argparse.ArgumentParser(description="Incremental encrypted backups.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_b = sub.add_parser("backup", help="Back up a folder.")
    p_b.add_argument("source", type=Path)
    p_b.add_argument("repo", type=Path)

    p_l = sub.add_parser("list", help="List versions.")
    p_l.add_argument("repo", type=Path)

    p_r = sub.add_parser("restore", help="Restore a version.")
    p_r.add_argument("repo", type=Path)
    p_r.add_argument("version")
    p_r.add_argument("dest", type=Path)

    args = parser.parse_args()
    if args.command == "list":
        list_versions(args.repo)
    elif args.command == "backup":
        backup(args.source, args.repo, getpass.getpass("Backup password: "))
    elif args.command == "restore":
        restore(args.repo, args.version, args.dest, getpass.getpass("Backup password: "))


if __name__ == "__main__":
    main()
