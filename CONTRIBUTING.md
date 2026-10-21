# Contributing to Yunmail Python SDK

Thanks for helping improve the SDK!

## Getting started

```bash
git clone https://github.com/tanxi281-sketch/yunmail-sdk.git
cd yunmail-sdk
pip install -e .
python -m unittest discover -s tests -v
```

## Guidelines

- Keep the SDK **dependency-free** (standard library only) unless a change
  is discussed in an issue first.
- Add or update tests for every behavior change; the transport is
  injectable, so tests never need network access or a real API key.
- Match the existing style: type hints on public methods, docstrings that
  state the channel and the failure modes.
- For bugs, open an issue with a minimal reproduction before sending a PR.

## Pull requests

1. Fork the repo and create a topic branch.
2. Make your change with tests.
3. Run the full test suite and make sure CI passes.
4. Describe *what* changed and *why* in the PR body.
