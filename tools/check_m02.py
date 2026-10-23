"""M02 bookkeeping check: schemas parse and required planning docs exist. Not a test of behaviour."""
import json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1];errs=[]
for p in sorted((root/"schemas").glob("*.json")):
    try:json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:errs.append(f"{p.name}: {e}")
for d in ["docs/SOURCES.md","docs/PRODUCT_CONTRACT.md","docs/ARCHITECTURE.md","docs/adr/0001-scope-and-boundaries.md","docs/architecture.mmd","inputs/source_register.jsonl"]:
    if not (root/d).is_file():errs.append("missing "+d)
for i,l in enumerate((root/"inputs/source_register.jsonl").read_text(encoding="utf-8").splitlines()):
    try:json.loads(l)
    except Exception as e:errs.append(f"register line {i+1}: {e}")
print(json.dumps({"valid":not errs,"errors":errs,"schemas":len(list((root/'schemas').glob('*.json')))}));sys.exit(bool(errs))
