# 18. Auth-Attempt GeoIP Mapper

## Problem
See where login attempts against your server are coming from.

## What you will build
- Parse failed-login lines from auth or web logs.
- Extract the source IPs.
- Look up the country and city for each IP.
- Summarize attempts by location.

## Concepts practiced
- Log parsing
- GeoIP lookups
- Aggregation

## Libraries
- re
- geoip2
- collections

## Stretch goals
- Plot the attempts on a map.
- Flag IPs that exceed a threshold.

## Status
- [ ] Not started

## Authorized use
Run this only against systems, accounts, or data you own or have explicit written permission to test. This is for learning and defensive use.
