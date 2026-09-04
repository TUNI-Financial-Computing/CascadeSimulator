# Release Process

This document outlines the steps for releasing a new version of CascadeSimulator.

## Pre-Release Checklist

Before creating a release, ensure:

- [ ] All tests pass locally: `pytest tests/python/ -v`
- [ ] GitHub Actions CI passes on all platforms
- [ ] Documentation is up to date (README, CONTRIBUTING, API docs)
- [ ] CHANGELOG.md has entry for this version
- [ ] Version number updated in relevant files
- [ ] All planned features for this version are complete
- [ ] Code review completed for major changes

## Version Numbering

CascadeSimulator follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
  - **MAJOR**: Incompatible API changes
  - **MINOR**: New features, backward compatible
  - **PATCH**: Bug fixes, backward compatible

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Added new cascade model
- `0.1.2` - Fixed bug in cutoff calculation
- `1.0.0` - Redesigned API (breaking changes)


## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PyPI Documentation](https://pypi.org/help/)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)
