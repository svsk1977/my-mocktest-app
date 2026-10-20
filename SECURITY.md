# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.1.x   | ✅ Current release |
| < 1.1   | ❌ Not supported   |

## Reporting a Vulnerability

We take the security of this exam portal seriously — it handles student
credentials and assessment data.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them privately via
[GitHub Security Advisories](https://github.com/svsk1977/my-mocktest-app/security/advisories/new)
("Report a vulnerability" button on the Security tab).

Please include as much of the following information as possible:

- The type of issue (e.g., authentication bypass, credential leakage, XSS)
- Full paths of source files related to the issue
- The location of the affected source code (tag/commit/branch)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact assessment, including how an attacker might exploit the issue

You should receive a response within 72 hours. If for some reason you do not,
please follow up via the same channel.

## Scope & Known Limitations

- The portal currently uses a **shared student password** (configurable via
  Streamlit secrets) by design — it is a practice portal, not a
  high-stakes proctored exam. Per-student hashed credentials are on the
  roadmap.
- The sample `students.csv` in this repository contains **dummy data only**.
  Real deployments should never commit real rosters to a public repo.
- Google service-account credentials must live only in
  `.streamlit/secrets.toml` (git-ignored). Never hard-code them.

## Preferred Languages

We prefer all communication in English.
