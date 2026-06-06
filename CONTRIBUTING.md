# 🤝 Contributing to GitForge-CLI

Thank you for your interest in contributing to GitForge-CLI! We welcome contributions from the community.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Provide a clear description of the issue
- Include steps to reproduce (for bugs)
- Mention your environment (OS, Python version, Git version)

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest tests/`)
5. Commit with clear messages following Conventional Commits
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Commit Message Format

We follow the Conventional Commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build/tooling changes

## Development Setup

```bash
git clone https://github.com/gitstq/GitForge-CLI.git
cd GitForge-CLI
pip install -e ".[dev]"
pytest tests/
```

## Questions?

Feel free to open an issue for any questions!
