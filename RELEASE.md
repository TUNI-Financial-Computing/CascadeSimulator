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
- `1.0.0` - Initial release
- `1.1.0` - Added new cascade model
- `1.1.1` - Fixed bug in cutoff calculation
- `2.0.0` - Redesigned API (breaking changes)

## Release Steps

### 1. Update Version Number

Update version in `pyproject.toml`:

```toml
[project]
name = "cascadesimulator"
version = "1.0.0"  # Update this
```

### 2. Update CHANGELOG.md

Move changes from `[Unreleased]` to a new version section:

```markdown
## [Unreleased]

(Empty - ready for next development cycle)

## [1.0.0] - 2026-02-05

### Added
- Initial release of CascadeSimulator
- High-performance C++ cascade generator
...
```

### 3. Commit Version Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.0.0"
git push origin main
```

### 4. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to GitHub
git push origin v1.0.0
```

### 5. Create GitHub Release

1. Go to: https://github.com/TUNI-Financial-Computing/CascadeSimulator/releases/new
2. Select the tag you just created: `v1.0.0`
3. Title: `CascadeSimulator v1.0.0`
4. Description: Copy relevant section from CHANGELOG.md
5. Attach any binary distributions (optional)
6. Click "Publish release"

### 6. Build Distribution Packages

```bash
# Install build tools
pip install --upgrade build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Verify the build
ls -lh dist/
# Should see: cascadesimulator-1.0.0.tar.gz and cascadesimulator-1.0.0-*.whl
```

### 7. Test the Distribution

Test in a clean environment:

```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from dist
pip install dist/cascadesimulator-1.0.0-*.whl

# Run quick test
python -c "from cascadesimulator import PyCascadeGenerator; print('Success!')"

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

### 8. Upload to TestPyPI (Optional but Recommended)

Test the upload process first:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ cascadesimulator

# Verify it works
python -c "from cascadesimulator import PyCascadeGenerator; print('TestPyPI success!')"
```

### 9. Upload to PyPI

**Warning:** This step is permanent - you cannot replace or delete releases.

```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: pypi-... (your API token)
```

**Set up PyPI API token** (first time only):

1. Create account at https://pypi.org/account/register/
2. Enable 2FA for security
3. Go to Account Settings → API tokens
4. Create token for "cascadesimulator" project
5. Save token securely (you won't see it again)

**Configure credentials** (recommended):

```bash
# Create or edit ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

### 10. Verify PyPI Release

1. Check package page: https://pypi.org/project/cascadesimulator/
2. Test installation:

```bash
# Clean environment
python -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install cascadesimulator

# Run verification
python -c "from cascadesimulator import PyCascadeGenerator; print('PyPI release verified!')"
pytest --pyargs cascadesimulator  # If tests are included

# Cleanup
deactivate
rm -rf verify_env
```

### 11. Announce the Release

- Update project website (if applicable)
- Post to relevant communities/forums
- Tweet or blog about major releases
- Update README badges if needed

## Post-Release

### Start Next Development Cycle

```bash
# Update CHANGELOG.md
echo "## [Unreleased]\n\n### Added\n\n### Changed\n\n### Fixed\n" | cat - CHANGELOG.md > temp && mv temp CHANGELOG.md

# Create development branch if needed
git checkout -b dev
git push -u origin dev

# Optionally bump to next dev version in pyproject.toml
# version = "1.1.0-dev"
```

### Monitor for Issues

- Watch GitHub issues for bug reports
- Monitor PyPI download stats
- Check CI/CD status
- Respond to user questions

## Hotfix Process

For critical bugs requiring immediate release:

```bash
# Create hotfix branch from latest release tag
git checkout -b hotfix/1.0.1 v1.0.0

# Make the fix
# ... edit files ...

# Update CHANGELOG.md
# Add section: ## [1.0.1] - 2026-02-06

# Commit and tag
git commit -am "Fix critical bug in cascade generation"
git tag -a v1.0.1 -m "Hotfix release 1.0.1"

# Merge back to main and dev
git checkout main
git merge hotfix/1.0.1
git checkout dev
git merge hotfix/1.0.1

# Push everything
git push origin main dev v1.0.1

# Follow steps 6-10 for PyPI release
```

## Troubleshooting Releases

### Build Fails on Different Platforms

- Test locally with Docker for each platform
- Check GitHub Actions logs for specific errors
- Ensure C++ code is platform-independent

### PyPI Upload Rejected

Common issues:
- **Version already exists**: Cannot reuse version numbers, bump to next version
- **Invalid credentials**: Check `~/.pypirc` or API token
- **Package name taken**: Choose different name in `pyproject.toml`
- **Missing metadata**: Ensure `pyproject.toml` has all required fields

### Installation Fails from PyPI

- Verify platform-specific wheels built correctly
- Check if source distribution includes all necessary files
- Test installation on clean system matching user's environment

## Rollback

If critical issue discovered after PyPI release:

1. **Cannot delete PyPI release**, but can:
   - Release new version immediately (e.g., 1.0.1) with fix
   - Mark version as "yanked" on PyPI (hides from default pip install)
   
2. **To yank a release:**
   ```bash
   # Requires PyPI web interface or twine
   # Go to PyPI → Manage Project → Options → Yank release
   ```

3. **Delete Git tag** (if not yet widely used):
   ```bash
   git tag -d v1.0.0
   git push origin :refs/tags/v1.0.0
   ```

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [PyPI Documentation](https://pypi.org/help/)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)
