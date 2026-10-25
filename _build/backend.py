"""Minimal in-tree PEP 517 build backend (stdlib only, no network, no build dependencies).
Builds a pure-Python wheel from src/<package>/ plus schemas/ as package data, and a source sdist.
It is deliberately small; it supports neither editable installs nor C extensions."""
import base64, hashlib, io, pathlib, tarfile, tomllib, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def _meta():
    p = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    return p, p["name"].replace("-", "_"), p["version"]
def get_requires_for_build_wheel(config_settings=None): return []
def get_requires_for_build_sdist(config_settings=None): return []
def _files():
    p, pkg, _ = _meta(); src = ROOT / "src" / pkg
    for f in sorted(src.rglob("*.py")):
        if "__pycache__" not in f.parts: yield f.relative_to(ROOT / "src").as_posix(), f.read_bytes()
    for f in sorted((ROOT / "schemas").glob("*.json")): yield f"{pkg}/schemas/{f.name}", f.read_bytes()
def _metadata(p):
    lines = ["Metadata-Version: 2.1", f"Name: {p['name']}", f"Version: {p['version']}", f"Summary: {p.get('description', '')}",
             f"Requires-Python: {p['requires-python']}"]
    return ("\n".join(lines) + "\n").encode()
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    p, pkg, ver = _meta(); di = f"{pkg}-{ver}.dist-info"; name = f"{pkg}-{ver}-py3-none-any.whl"
    entries = list(_files()) + [(f"{di}/METADATA", _metadata(p)),
        (f"{di}/WHEEL", b"Wheel-Version: 1.0\nGenerator: in-tree _build/backend.py\nRoot-Is-Purelib: true\nTag: py3-none-any\n"),
        (f"{di}/entry_points.txt", ("[console_scripts]\n" + "".join(f"{k} = {v}\n" for k, v in p.get("scripts", {}).items())).encode())]
    record = []
    with zipfile.ZipFile(pathlib.Path(wheel_directory) / name, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, data in entries:
            zi = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0)); zi.external_attr = 0o644 << 16; z.writestr(zi, data)
            h = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode(); record.append(f"{arc},sha256={h},{len(data)}")
        record.append(f"{di}/RECORD,,"); zi = zipfile.ZipInfo(f"{di}/RECORD", date_time=(1980, 1, 1, 0, 0, 0)); zi.external_attr = 0o644 << 16
        z.writestr(zi, "\n".join(record) + "\n")
    return name
def build_sdist(sdist_directory, config_settings=None):
    p, pkg, ver = _meta(); base = f"{pkg}-{ver}"; name = f"{base}.tar.gz"
    with tarfile.open(pathlib.Path(sdist_directory) / name, "w:gz") as t:
        for rel in ["pyproject.toml", "README.md", "_build/backend.py"] + [f.relative_to(ROOT).as_posix() for d in ("src", "schemas") for f in sorted((ROOT / d).rglob("*")) if f.is_file() and "__pycache__" not in f.parts]:
            data = (ROOT / rel).read_bytes(); ti = tarfile.TarInfo(f"{base}/{rel}"); ti.size = len(data); ti.mtime = 0; t.addfile(ti, io.BytesIO(data))
        meta = _metadata(p); ti = tarfile.TarInfo(f"{base}/PKG-INFO"); ti.size = len(meta); t.addfile(ti, io.BytesIO(meta))
    return name
