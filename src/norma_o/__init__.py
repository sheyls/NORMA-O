"""NORMA-O 2.0 as a Python package.

Ships the ontology, the derivation module (normad), the reference rule set
(deriv/) and the `norma` engine, so that a project can depend on an exact
release of NORMA-O instead of copying its files:

    pip install "norma-o @ git+https://github.com/sheyls/NORMA-O@v2.0.0"
    norma annotation.ttl            # check, derive, bundle, report

Annotations import NORMA-O by its published IRI
(owl:imports <https://w3id.org/def/norma-o/2.0>). `load()` resolves that IRI,
and the derivation module's, to the copies in this package, so nothing is
fetched from the network and the version is always the installed one.

Part of NORMA-O, https://github.com/sheyls/NORMA-O (CC BY 4.0).
"""
from __future__ import annotations

from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import OWL

__version__ = "2.0.0"
ONTOLOGY_VERSION = "2.0"
RULE_SET_VERSION = "norma-derivation/1.0"

_HERE = Path(__file__).resolve().parent
# Installed: the release files sit next to this file. From a source checkout:
# they are read from release/2.0.0.
HOME = _HERE if (_HERE / "norma-ontology-v2.ttl").is_file() else _HERE.parent.parent / "release" / "2.0.0"
ONTOLOGY = HOME / "norma-ontology-v2.ttl"
MODULE = HOME / "norma-o-deriv.ttl"

#: Published IRIs (ontology and version IRIs) and the local file each resolves to.
IRIS: dict[str, Path] = {
    "https://w3id.org/def/norma-o": ONTOLOGY,
    "https://w3id.org/def/norma-o/2.0": ONTOLOGY,
    "https://w3id.org/def/norma-o/deriv": MODULE,
    "https://w3id.org/def/norma-o/deriv/1.0": MODULE,
}


def path(iri: str) -> Path:
    """Local file of a NORMA-O IRI, e.g. path("https://w3id.org/def/norma-o/2.0")."""
    key = str(iri).rstrip("#/")
    if key not in IRIS:
        raise KeyError(f"not a NORMA-O {ONTOLOGY_VERSION} IRI: {iri}")
    return IRIS[key]


def load(*sources, imports: bool = True) -> Graph:
    """Parses the given files and, by default, the NORMA-O ontologies they import.

    owl:imports of NORMA-O IRIs are followed (transitively) to the files of this
    package; any other import is left as it is, unresolved, so nothing is
    fetched from the network.
    """
    g = Graph()
    for s in sources:
        g.parse(s)
    if imports:
        done: set[Path] = set()
        while True:
            todo = {IRIS[k] for k in (str(o).rstrip("#/") for o in g.objects(None, OWL.imports))
                    if k in IRIS} - done
            if not todo:
                break
            for f in sorted(todo):
                g.parse(f, format="turtle")
                done.add(f)
    return g


__all__ = ["__version__", "ONTOLOGY_VERSION", "RULE_SET_VERSION", "HOME", "ONTOLOGY", "MODULE",
           "IRIS", "path", "load"]
