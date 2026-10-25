# Dependencies (M08)

- **Runtime:** none. Python standard library only. `requires-python = ">=3.11"`, verified on CPython 3.11.17 and 3.13.5 (`tests/receipts/m08_run.json`).
- **Build:** none. `pyproject.toml` uses the in-tree stdlib backend `_build/backend.py` with `requires = []`, so `pip install --no-index .` works offline. The wheel is byte-reproducible (tested).
- **Lock:** with zero third-party packages there is nothing to lock. The empty lists are pinned by `tests/test_package.py`.
- **Install:** `python3 -m pip install --no-index .` installs the `abstention-routing-harness` console script. Inputs and fixtures stay in the repo, and schemas ship inside the wheel.
- **Reproducible example:** `sh examples/run.sh` installs into a throwaway venv, reruns the README commands with the installed script, and checks the outputs against `examples/expected.sha256`.
- **CI:** not enabled. See `docs/ci-proposed/` and `handoff/REPORT.md`.
