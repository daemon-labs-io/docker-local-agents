# Security Policy

This document defines the security policy for the local AI workshop system.

## Password management

All passwords for local services must meet the following requirements:

- Minimum 12 characters
- Mix of uppercase, lowercase, digits, and symbols
- Not reused across services
- Stored in a reputable password manager, never in plain text files

Default passwords must be changed on first login. Shared passwords are prohibited.

## Access management

- User accounts are local to each workshop attendee's machine
- No external authentication, such as SSO or OAuth, because the system is air-gapped
- Admin-equivalent actions require explicit user confirmation

## Data handling

- All workshop data stays on the attendee's local machine
- No telemetry is sent to external services; ChromaDB's anonymised telemetry is disabled
- Workshop sample documents are not sensitive and may be shared freely
- Attendees should not ingest confidential or regulated data into the workshop stack without reviewing their organisation's policies

## Incident response

If an attendee suspects a security issue, such as an unexpected network connection or an unknown process, they should:

1. Stop all running containers with `docker compose down`
2. Report the issue to the workshop facilitator
3. Avoid running the system further until the issue is triaged
