# Security Policy

## Supported Versions

The following versions of the VAP Framework are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| < 1.1   | :x:                |

## Reporting a Vulnerability

We take the security of the Verifiable AI Provenance Framework seriously. If you believe you have found a security vulnerability in the specification or reference implementations, please report it to us as described below.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to:

📧 **security@veritaschain.org**

If you prefer encrypted communication, please contact us first to obtain our PGP key.

### What to Include

Please include the following information in your report:

- **Type of vulnerability** (e.g., cryptographic weakness, protocol flaw, implementation bug)
- **Affected component(s)** (e.g., VAP specification, specific profile, reference code)
- **Detailed description** of the vulnerability
- **Step-by-step instructions** to reproduce the issue
- **Proof-of-concept** (if available)
- **Impact assessment** of the vulnerability
- **Any potential mitigations** you have identified

### Response Timeline

| Action | Timeline |
| ------ | -------- |
| Initial response | Within 48 hours |
| Status update | Within 7 days |
| Vulnerability assessment | Within 14 days |
| Specification revision | Depends on severity |
| Public disclosure | After revision is published |

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your vulnerability report within 48 hours.

2. **Communication**: We will keep you informed about the progress of addressing the vulnerability.

3. **Assessment**: Our security team will investigate and assess the impact of the reported vulnerability.

4. **Resolution**: We will work on a specification revision and coordinate the release timeline with you.

5. **Credit**: If you wish, we will publicly acknowledge your responsible disclosure in our release notes.

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

- ⭐ **Star** and **Watch** our repositories on GitHub
- 📧 Subscribe to security announcements at security@veritaschain.org
- 🌐 Visit https://veritaschain.org for the latest updates

## Scope

This security policy applies to the following VAP-related repositories:

- [vap-spec](https://github.com/veritaschain/vap-spec) - VAP Framework Specification
- [vcp-spec](https://github.com/veritaschain/vcp-spec) - Finance Profile (VCP)
- [cap-spec](https://github.com/veritaschain/cap-spec) - Content/Creative Profile (CAP)

## Acknowledgments

We appreciate the security research community's efforts in helping us maintain the security of the VAP Framework. Responsible disclosure helps protect the integrity of AI auditability systems worldwide.

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
