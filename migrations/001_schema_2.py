"""001: the contracts as files (schemas/, step 1 of the gully port).

Brings a file from schemaVersion 1 to 2. The provenance word `engine` is retired for `simulated`
(docs/facts-contract.md), wherever a `provenance` field holds it. Nothing else in today's fixtures changes
mechanically: the corner, street and town bundles stay bundles until each kind's port turns them into records.
"""
FROM = 1
TO = 2


def _retire_engine(o):
    if isinstance(o, dict):
        return {k: ("simulated" if k == "provenance" and v == "engine" else _retire_engine(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [_retire_engine(v) for v in o]
    return o


def migrate(doc, path):
    doc = _retire_engine(doc)
    doc["schemaVersion"] = TO
    return doc
