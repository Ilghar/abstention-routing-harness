#!/bin/sh
# Reproducible example: install the package offline into a throwaway venv, then rerun the README commands
# with the installed console script and compare outputs with the committed expected hashes.
# Needs only python3 >= 3.11 (venv + bundled pip). No network: pip runs with --no-index.
set -eu
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"; V="$(mktemp -d)/venv"; OUT="$(mktemp -d)"
"$PY" -m venv "$V"
"$V/bin/python" -m pip install --quiet --no-index --disable-pip-version-check .
BIN="$V/bin/abstention-routing-harness"
"$BIN" run fixtures/synthetic_cases_m03.json --out "$OUT"/
"$BIN" slice inputs/synthetic_queue_fixture.json --probes fixtures/ood_probes_m04.json --out "$OUT"/m04
cd "$OUT" && find . -type f | LC_ALL=C sort | xargs sha256sum > "$OUT.sha256"; cd - >/dev/null
if diff -u examples/expected.sha256 "$OUT.sha256"; then echo "examples: outputs match examples/expected.sha256"; else echo "examples: MISMATCH" >&2; exit 1; fi
