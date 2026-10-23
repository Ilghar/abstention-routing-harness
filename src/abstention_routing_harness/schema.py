"""Minimal stdlib JSON-Schema subset validator (draft 2020-12 keywords used in this repo's schemas/).
Supported: type, enum, const, required, properties, additionalProperties(false), items, minItems, maxItems,
minLength, maxLength, pattern, minimum, maximum, $ref (#/$defs/...), not, anyOf. Unknown keywords are ignored
and reported by `unsupported_keywords` so silent gaps are visible."""
import json, math, pathlib, re
SUPPORTED = {"$schema", "title", "description", "type", "enum", "const", "required", "properties", "additionalProperties",
             "items", "minItems", "maxItems", "minLength", "maxLength", "pattern", "minimum", "maximum", "$ref", "$defs", "not", "anyOf"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
def _is(t, v):
    if t == "integer": return isinstance(v, int) and not isinstance(v, bool)
    if t == "number": return isinstance(v, (int, float)) and not isinstance(v, bool) and not (isinstance(v, float) and math.isnan(v))
    return isinstance(v, TYPES[t]) and not (t != "boolean" and isinstance(v, bool) and TYPES[t] is not bool)
def unsupported_keywords(s, acc=None):
    acc = set() if acc is None else acc
    if isinstance(s, dict):
        for k in s:
            if k not in SUPPORTED: acc.add(k)
        for k in ("properties", "$defs"):
            for sub in (s.get(k) or {}).values(): unsupported_keywords(sub, acc)
        for k in ("items", "not"):
            if isinstance(s.get(k), dict): unsupported_keywords(s[k], acc)
        for sub in s.get("anyOf", []): unsupported_keywords(sub, acc)
    return acc
def validate(inst, schema, root=None, path="$"):
    root = root or schema; e = []
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].lstrip("#/").split("/"): node = node[part]
        return validate(inst, node, root, path)
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is(t, inst) for t in ts): return [f"{path}: expected {ts}, got {type(inst).__name__}"]
    if "enum" in schema and inst not in schema["enum"]: e.append(f"{path}: {inst!r} not in enum")
    if "const" in schema and inst != schema["const"]: e.append(f"{path}: must equal {schema['const']!r}")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst: e.append(f"{path}: missing required '{k}'")
        props = schema.get("properties", {})
        for k, v in inst.items():
            if k in props: e += validate(v, props[k], root, f"{path}.{k}")
            elif schema.get("additionalProperties") is False: e.append(f"{path}: unexpected property '{k}'")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]: e.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(inst) > schema["maxItems"]: e.append(f"{path}: more than {schema['maxItems']} items")
        if isinstance(schema.get("items"), dict):
            for i, v in enumerate(inst): e += validate(v, schema["items"], root, f"{path}[{i}]")
    if isinstance(inst, str):
        if "minLength" in schema and len(inst) < schema["minLength"]: e.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(inst) > schema["maxLength"]: e.append(f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], inst): e.append(f"{path}: does not match {schema['pattern']}")
    if _is("number", inst):
        if "minimum" in schema and inst < schema["minimum"]: e.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and inst > schema["maximum"]: e.append(f"{path}: above maximum {schema['maximum']}")
    if "not" in schema and not validate(inst, schema["not"], root, path): e.append(f"{path}: matches forbidden 'not' schema")
    if "anyOf" in schema and all(validate(inst, s, root, path) for s in schema["anyOf"]): e.append(f"{path}: matches none of anyOf")
    return e
def load_schema(root, name): return json.loads((pathlib.Path(root) / "schemas" / name).read_text(encoding="utf-8"))
