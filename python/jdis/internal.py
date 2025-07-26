import json

# dataclasses-like with recursive to/from_json and extensible (unions)

def internal_isinstance(o, cls):
    if isinstance(cls, type) and isinstance(o, cls):
        return True
    if hasattr(cls, "isinstance") and cls.isinstance(o):
        return True
    return False

def from_jsonable_or_init(cls, o):
    if o is None: return None
    if internal_isinstance(o, cls): return o
    return cls.from_jsonable(o) if hasattr(cls, "from_jsonable") else cls(o)

def to_jsonable_or_id(o):
    return o.to_jsonable() if hasattr(o, "to_jsonable") else o

def serde(cls):
    fields = cls.__annotations__
    order = [k for k in fields]

    def init(self, *args, **kwargs):
        for field, arg in zip(order, args):
            setattr(self, field, from_jsonable_or_init(fields[field], arg))
        for field, arg in kwargs.items():
            if (t := fields.get(field)) is not None:
                setattr(self, field, from_jsonable_or_init(t, arg))
        for field in order:
            if not hasattr(self, field):
                setattr(self, field, None)

    def _key(self):
        return tuple(getattr(self, field) for field in order)

    def __hash(self):
        return hash(_key(self))

    def __eq(self, other):
        if not isinstance(other, cls): return False
        return _key(self) == _key(other)

    # ser
    def to_jsonable(self):
        d = dict()
        for k, t in fields.items():
            v = getattr(self, k)
            d[k] = t.to_jsonable(v) if hasattr(t, "to_jsonable") else to_jsonable_or_id(v)
        if hasattr(cls, "_"): d.update(cls._)
        return d

    def to_json(self):
        return json.dumps(self.to_jsonable())

    # deser
    def from_jsonable(o):
        return cls(**o)

    def from_json(s):
        return from_jsonable(cls, json.loads(s))

    setattr(cls, "__init__", init)
    setattr(cls, "__hash__", __hash)
    setattr(cls, "__eq__", __eq)
    setattr(cls, "to_jsonable", to_jsonable)
    setattr(cls, "to_json", to_json)
    setattr(cls, "from_jsonable", from_jsonable)
    setattr(cls, "from_json", from_json)
    return cls

class Union:
    def __init__(self, field, *classes):
        self.field = field
        self.classes = classes
        self.parsers = {cls._[field]: cls.from_jsonable for cls in classes}

    def from_jsonable(self, o):
        return self.parsers[o[self.field]](o)

    def from_json(self, s):
        return self.from_jsonable(json.loads(s))

    def isinstance(self, o):
        return any(isinstance(o, t) for t in self.classes)

class List:
    def __init__(self, cls):
        self.cls = cls

    def from_jsonable(self, o):
        return [from_jsonable_or_init(self.cls, x) for x in o]

    def from_json(self, s):
        return self.from_jsonable(json.loads(s))

    def isinstance(self, o):
        return isinstance(o, list) and all(internal_isinstance(x, self.cls) for x in o)

class Enum:
    def __init__(self, elems: dict):
        if not isinstance(elems, dict):
            elems = {v: v for v in elems}

        self._reverse = {v: k for k,v in elems.items()}
        self._elems = elems

        for k, v in elems.items():
            setattr(self, k, v)

    def from_jsonable(self, o):
        return self._elems[o]

    def from_json(self, s):
        return self.from_jsonable(json.loads(s))

    def isinstance(self, o):
        return o in self._reverse

    def to_jsonable(self, o):
        return self._reverse.get(o)
