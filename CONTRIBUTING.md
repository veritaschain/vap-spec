# Contributing to VAP Framework

Thank you for your interest in contributing to the Verifiable AI Provenance (VAP) Framework! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Style Guidelines](#style-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to info@veritaschain.org.

## How Can I Contribute?

### Reporting Issues

Before creating reports, please check existing issues to avoid duplicates. When creating a report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the issue in detail**
- **Provide specific examples** where applicable
- **Reference relevant sections** of the specification

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **A clear and descriptive title**
- **A detailed description of the proposed enhancement**
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**
- **Regulatory or industry context** if applicable

### Contributing to Specifications

We welcome specification contributions! Areas where you can help:

- **Clarifications** - Improve clarity of existing text
- **Examples** - Add illustrative examples
- **Translations** - Translate specifications (EN, JA, ZH supported)
- **New Profiles** - Propose new domain profiles

### Proposing New Domain Profiles

If you want to propose a new VAP domain profile:

1. **Open a Discussion** - Start with a GitHub Discussion to gather feedback
2. **Draft RFC** - Create a Request for Comments document
3. **Technical Review** - Engage with the Technical Committee
4. **Public Comment** - 30-day public review period
5. **Vote** - Technical Committee vote (2/3 majority required)

## Getting Started

### Prerequisites

For working with VAP specifications:

- **Git** for version control
- **Markdown editor** (VS Code recommended)
- Familiarity with cryptographic concepts
- Understanding of relevant regulatory frameworks

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/vap-spec.git
   cd vap-spec
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/veritaschain/vap-spec.git
   ```

## Development Workflow

### Creating a Branch

Create a branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Branch naming conventions:
- `feature/` - New features or profiles
- `fix/` - Corrections to specifications
- `docs/` - Documentation changes
- `rfc/` - Request for Comments drafts

### Making Changes

1. Make your changes in your branch
2. Ensure consistency with existing specifications
3. Update related documents if necessary
4. Add yourself to CONTRIBUTORS if this is your first contribution

## Style Guidelines

### Specification Documents

- Use **Markdown** for all specifications
- Follow [RFC 2119](https://www.ietf.org/rfc/rfc2119.txt) for requirement keywords (MUST, SHOULD, MAY)
- Keep line length reasonable (≤120 characters)
- Use headers to organize content hierarchically
- Include code examples in JSON format

### Diagrams

- Use ASCII art for simple diagrams (for portability)
- Use Mermaid for complex diagrams when necessary
- Always include text descriptions alongside diagrams

### Terminology

- Define terms in glossaries
- Use consistent terminology across all documents
- Reference existing standards (RFC, ISO) where applicable

### Multilingual Support

- Primary language: English
- Supported translations: Japanese (JA), Chinese (ZH)
- Maintain sync between language versions

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat` - New feature or profile section
- `fix` - Correction to specification
- `docs` - Documentation changes
- `style` - Formatting changes
- `refactor` - Restructuring without changing meaning
- `chore` - Maintenance tasks

### Examples

```
feat(spec): add Crypto Agility requirements section

fix(provenance): clarify actor identifier requirements

docs(readme): add link to CAP profile repository

feat(profiles): propose DVP automotive profile RFC
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Ensure consistency**:
   - Specification follows style guidelines
   - Cross-references are valid
   - No broken links

3. **Write a clear PR description**:
   - What changes were made
   - Why these changes were made
   - Any related issues (use `Fixes #123` to auto-close)

### Review Process

1. A maintainer will review your PR
2. Address any requested changes
3. For specification changes, Technical Committee review may be required
4. Once approved, a maintainer will merge your PR

### After Merge

- Delete your feature branch
- Pull the latest changes from upstream

## Community

### Getting Help

- **GitHub Issues** - For specification issues
- **GitHub Discussions** - For questions and proposals
- **Email** - standards@veritaschain.org

### Stay Connected

- **Website**: https://veritaschain.org
- **GitHub**: https://github.com/veritaschain

### Related Repositories

| Repository | Description |
|------------|-------------|
| [vcp-spec](https://github.com/veritaschain/vcp-spec) | Finance Profile (VCP) |
| [cap-spec](https://github.com/veritaschain/cap-spec) | Content/Creative Profile (CAP) |

---

## Recognition

Contributors will be recognized in our release notes and on our website. Thank you for helping advance AI auditability standards!

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
