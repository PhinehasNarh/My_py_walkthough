# 04. File Magic-Byte Type Identifier

## Problem
Find files whose real type does not match their extension, a classic sign of something hidden.

## What you will build
- Read the first bytes (magic numbers) of each file.
- Map signatures to real file types.
- Compare the real type against the extension.
- Flag mismatches, such as a .jpg that is really an executable.

## Concepts practiced
- Binary file reading
- Magic numbers
- Mismatch detection

## Libraries
- pathlib

## Stretch goals
- Scan a folder recursively and report all mismatches.
- Grow the signature table from a reference list.

## Status
- [ ] Not started

## Authorized use
Run this only against systems, accounts, or data you own or have explicit written permission to test. This is for learning and defensive use.
