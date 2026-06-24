# Action Items: Python Real-World Projects

The working shortlist. Pick one per week, in order, and check it off when it runs.

## Status legend
- [ ] not started
- [~] in progress (write `[~]` while working on it)
- [x] done

Currently building: all four tiers complete (01-35). Every project is built and tested.

Tag meaning: (sec) marks a security or networking project. Run those only against systems, accounts, or data you own or are authorized to test.

## Tier 1: Approachable but genuinely useful

- [x] 01. Pwned Password Checker (sec): Check whether a password has appeared in known breaches, without sending the password anywhere. [hashlib, requests]
- [x] 02. Subnet & IP Toolkit (sec): Do the IP and subnet maths you constantly need in networking, from one tool. [ipaddress]
- [x] 03. Bulk File Renamer: Rename a whole folder of files consistently instead of one by one. [pathlib, re]
- [x] 04. File Magic-Byte Type Identifier (sec): Find files whose real type does not match their extension, a classic sign of something hidden. [pathlib]
- [x] 05. Duplicate File Finder: Reclaim disk space by finding exact duplicate files across folders. [hashlib, pathlib]
- [x] 06. Disk Space Analyzer: See what is actually eating your disk space instead of guessing. [pathlib, os]

## Tier 2: Files, parsing, real API work

- [x] 07. File Metadata Scrubber (sec): Strip hidden metadata (EXIF, author, GPS) from files before you share them. [Pillow, pypdf]
- [x] 08. Smart Downloads Organizer: Keep a messy Downloads folder tidy automatically by type and rules. [pathlib, shutil, watchdog]
- [x] 09. Website Change Monitor: Get told when a web page changes instead of refreshing it yourself. [requests, difflib, schedule]
- [x] 10. Web Scraper to Dataset: Turn a website's listings into a clean, deduplicated dataset you can analyze. [requests, beautifulsoup4]
- [x] 11. Broken Link Checker: Find dead links on a website before your visitors do. [requests, beautifulsoup4]
- [x] 12. Email Header Analyzer (sec): Investigate a suspicious email by reading what its headers reveal. [email, re]
- [x] 13. JWT Inspector & Weakness Checker (sec): Understand and test JSON Web Tokens used by web apps you are allowed to test. [pyjwt, hashlib]
- [x] 14. Spaced-Repetition Flashcards: Study and retain material efficiently with a real spaced-repetition algorithm. [json, datetime]
- [x] 15. Screenshot OCR Tool: Pull text out of screenshots and images instead of retyping it. [pytesseract, Pillow, pyperclip] (needs the Tesseract engine installed to run OCR)

## Tier 3: Networking, databases, security tooling

- [x] 16. WHOIS & DNS Recon Tool (sec): Gather public registration and DNS information about a domain for recon. [dnspython, python-whois]
- [x] 17. Secret / API-Key Scanner (sec): Catch API keys and secrets accidentally left in your code. [re, math]
- [x] 18. Auth-Attempt GeoIP Mapper (sec): See where login attempts against your server are coming from. [re, geoip2, collections]
- [x] 19. HTTP Security Headers + TLS Grader (sec): Grade how well a site is configured for transport and header security. [requests, ssl, socket]
- [x] 20. OSINT Username Hunter (sec): Check whether a username exists across many sites during an OSINT investigation. [requests, concurrent.futures]
- [x] 21. Typosquatting Domain Checker (sec): Find lookalike domains that could be used to impersonate a brand. [dnspython, python-whois]
- [x] 22. Malware Hash Reputation Checker (sec): Decide quickly whether a file is known-bad using threat intelligence. [hashlib, requests]
- [x] 23. TLS / Cipher Suite Scanner (sec): See which TLS versions and ciphers a server accepts, on hosts you are allowed to test. [ssl, socket]
- [x] 24. Steganography Tool (sec): Learn how data can be hidden inside images by building hide and extract tools. [Pillow]
- [x] 25. Expense Splitter: Work out who owes whom after a group shares costs. [json]
- [x] 26. Stock / Crypto Portfolio Tracker: Track your holdings' value and get alerted on big moves. [requests]
- [x] 27. Resume vs Job-Description ATS Matcher: See how well your resume matches a job description before you apply. [re, collections]

## Tier 4: Apps, forensics, larger builds

- [x] 28. Versioned Encrypted Backup Tool: Back up a folder incrementally and keep encrypted, restorable versions. [hashlib, cryptography, shutil]
- [x] 29. ETL Pipeline: Pull data from an API, clean it, store it, and report on a schedule. [requests, sqlite3, schedule]
- [x] 30. Browser History Forensics (sec): Reconstruct browsing activity from a browser's own database, on a machine you own. [sqlite3, datetime]
- [x] 31. YARA Malware Triage Scanner (sec): Triage suspicious files by scanning them against pattern-based detection rules. [yara-python]
- [x] 32. Certificate Transparency Monitor (sec): Detect rogue or unexpected certificates issued for your domain. [requests]
- [x] 33. Wordlist / Breach Corpus Analyzer (sec): Understand how people actually pick passwords by analyzing a public breach wordlist. [collections, matplotlib]
- [x] 34. Invoice / Receipt PDF Generator: Generate clean, consistent invoices from data instead of editing documents by hand. [fpdf2]
- [x] 35. Personal Knowledge Base / Note Search CLI: Make all your scattered notes instantly searchable from the terminal. [whoosh, pathlib]
