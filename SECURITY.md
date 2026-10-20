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

- The portal currently uses a **shared student password** configured via
  Streamlit secrets (`portal_password`). There is deliberately **no
  hard-coded default**: if the secret is missing, logins are disabled with
  an on-screen setup message rather than silently accepting a known
  password. Per-student hashed credentials are on the roadmap.
- The repository ships only a **dummy example roster**
  (`students.example.csv`); the live roster file (`students.csv`) is
  git-ignored so real student data cannot be committed. A historical roster
  containing real student records was purged from the Git record in
  October 2026 — deployments must keep real rosters out of version control.
- Google service-account credentials must live only in
  `.streamlit/secrets.toml` (git-ignored) or Streamlit Cloud secrets.
  Never hard-code them.

## Preferred Languages

We prefer all communication in English.
