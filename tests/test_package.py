"""M08: the in-tree backend builds a deterministic, dependency-free wheel that ships schemas and a console script."""
import hashlib, importlib.util, pathlib, tempfile, tomllib, unittest, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("backend", ROOT / "_build/backend.py"); backend = importlib.util.module_from_spec(spec); spec.loader.exec_module(backend)
class Package(unittest.TestCase):
    def test_no_dependencies_declared(self):
        t = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertEqual(t["build-system"]["requires"], []); self.assertEqual(t["project"]["dependencies"], [])
        self.assertEqual(backend.get_requires_for_build_wheel(), [])
    def test_wheel_contents_and_determinism(self):
        digests = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                w = pathlib.Path(d) / backend.build_wheel(d); digests.append(hashlib.sha256(w.read_bytes()).hexdigest())
                names = zipfile.ZipFile(w).namelist()
                ep = zipfile.ZipFile(w).read([n for n in names if n.endswith("entry_points.txt")][0]).decode()
        self.assertEqual(digests[0], digests[1])
        self.assertIn("abstention_routing_harness/cli.py", names); self.assertIn("abstention-routing-harness = abstention_routing_harness.cli:main", ep)
        self.assertEqual(sorted(n.split("/")[-1] for n in names if "/schemas/" in n), sorted(p.name for p in (ROOT / "schemas").glob("*.json")))
        self.assertFalse(any("__pycache__" in n or n.startswith(("tests/", "fixtures/")) for n in names))
    def test_sdist_builds(self):
        with tempfile.TemporaryDirectory() as d: self.assertTrue((pathlib.Path(d) / backend.build_sdist(d)).stat().st_size > 0)
if __name__ == "__main__": unittest.main()
