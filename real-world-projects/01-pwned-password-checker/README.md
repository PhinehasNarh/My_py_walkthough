# 01. Pwned Password Checker

## Problem
Check whether a password has appeared in known breaches, without sending the password anywhere.

## What you will build
- Hash the password with SHA-1.
- Send only the first 5 hash characters to the HaveIBeenPwned range API.
- Search the returned suffixes for the rest of your hash.
- Report how many times it was seen in breaches.

## Concepts practiced
- Hashing
- k-anonymity
- HTTP APIs

## Libraries
- hashlib
- requests

## Stretch goals
- Check a whole password list and flag the bad ones.
- Suggest a strong replacement when one is breached.

## Status
- [ ] Not started

## Authorized use
Run this only against systems, accounts, or data you own or have explicit written permission to test. This is for learning and defensive use.
