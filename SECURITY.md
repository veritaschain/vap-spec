# Security Policy

## Supported Versions

The following versions of the VAP Framework are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x (Draft 3) | :white_check_mark: |
| 1.1.x   | :white_check_mark: (superseded for new work) |
| < 1.1   | :x:                |

## Reporting a Vulnerability

We take the security of the Verifiable AI Provenance Framework seriously. If you believe you have found a security vulnerability in the specification or reference implementations, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

For this repository, use [GitHub private vulnerability reporting](https://github.com/veritaschain/vap-spec/security/advisories/new). The feature was enabled on 24 October 2026. Reports are not public issues. Please remove production credentials, personal data and unrelated customer information before submitting.

You can also contact us via email:

📧 **security@veritaschain.org**

If you need an encrypted exchange outside GitHub, send a non-sensitive initial message so we can agree on a suitable channel before you send confidential details. This repository does not currently publish a verified PGP contact key; availability of a key must not be assumed. Ordinary email is not represented as end-to-end encrypted.

If you receive no acknowledgment within the target below, follow up through the other private channel with the original date and a short non-sensitive summary. Do not post the vulnerability details in a public issue.

### What to Include

Please include the following information in your report:

- **Type of vulnerability** (e.g., cryptographic weakness, protocol flaw, implementation bug)
- **Affected component(s)** (e.g., VAP specification, specific profile, reference code)
- **Detailed description** of the vulnerability
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept** (if available)
- **Impact assessment** of the vulnerability
- **Any potential mitigations** you have identified

### Response Targets

These are operational targets, not a guaranteed service level or a claim of round-the-clock staffing. Coverage during absence or holidays has not been validated. Business days mean Monday–Friday, excluding Japanese public holidays (Asia/Tokyo). We will state the next update date when acknowledging a report and explain material delays.

| Action | Target |
| ------ | -------- |
| Initial response | Within 2 business days of receipt |
| Status update | Aim for 7 calendar days after acknowledgment; confirm the next update date in the acknowledgment |
| Initial vulnerability assessment | Aim for 14 calendar days after acknowledgment, subject to sufficient information and complexity |
| Specification revision | Depends on severity |
| Public disclosure | Coordinate timing and scope with the reporter, considering risk and remediation |

### What to Expect

1. **Acknowledgment**: We aim to acknowledge receipt within the target above. An automated receipt alone does not establish that a maintainer has reviewed the report.

2. **Communication**: We will keep you informed about the progress of addressing the vulnerability.

3. **Assessment**: The maintainer will investigate and assess the reported issue. Receipt is not confirmation that a vulnerability exists.

4. **Resolution**: We will work on a specification revision and coordinate the release timeline with you.

5. **Credit**: Publication of the report, raw evidence, your name and your organization requires separate agreement. We will confirm the proposed wording and attribution before publication.

A controlled email exercise on 24 October 2026 checked delivery to the business mailbox and delivery of an AI-assisted acknowledgment to the sender. It did not establish independent notification awareness, holiday/absence coverage, PGP key readiness, or the handling of a real vulnerability. Enabling GitHub private reporting likewise does not by itself prove that its notifications have reached a human.

Reports concerning the research experiments are welcome, but the extensions remain **unadopted**, separate from current VAP v1.2 requirements. Independent third-party reproduction has **not been established**. This contact-policy update does not change the fixed research ZIPs, source revisions, existing verifier, gate, OS experiment or K3 conditions.

## Security Best Practices

When implementing VAP profiles in your systems, please follow these security best practices:

### Cryptographic Requirements

- **Ed25519 Signatures**: Use only compliant Ed25519 implementations (RFC 8032)
- **SHA-256 Hash Chains**: Ensure proper hash chain validation
- **Merkle Proofs**: Verify RFC 6962 compliance for all Merkle tree operations
- **Key Management**: Store private keys securely, never in source code or public repositories
- **Crypto Agility**: Design systems to support future algorithm migration (e.g., post-quantum)

### Implementation Security

- Use well-tested cryptographic libraries
- Validate all data before signing
- Implement proper timestamp synchronization (NTP/PTP)
- Ensure hash chain continuity checking
- Verify external anchoring proofs

### Data Protection

- Encrypt sensitive data at rest and in transit
- Implement proper access controls for audit logs
- Support GDPR crypto-shredding requirements where applicable
- Maintain separation between provenance data and sensitive content

## Security Updates

Security updates are released as needed. To stay informed:

- Use GitHub **Watch → Custom → Security alerts** for this repository, with email delivery enabled in your GitHub notification settings. A star alone does not subscribe you to security notifications.
- 🌐 Visit https://veritaschain.org for the latest updates

## Scope

This policy is maintained for [vap-spec](https://github.com/veritaschain/vap-spec). The private-reporting enablement and intake exercise described above were checked for this repository only. Related profile repositories have their own reporting settings and security policies:

- [vcp-spec](https://github.com/veritaschain/vcp-spec) - Finance Profile (VCP)
- [cap-spec](https://github.com/veritaschain/cap-spec) - Content / Creative AI Profile (CAP)
- [cpp-spec](https://github.com/veritaschain/cpp-spec) - Capture Provenance Profile (CPP)

## Acknowledgments

We appreciate the security research community's efforts in helping us maintain the security of the VAP Framework. Responsible disclosure helps protect the integrity of AI auditability systems worldwide.

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
