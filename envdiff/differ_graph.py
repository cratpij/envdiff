"""Build a dependency graph of key relationships across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class GraphNode:
    key: str
    sources: List[str] = field(default_factory=list)
    values: Dict[str, str] = field(default_factory=dict)  # source -> value

    @property
    def is_consistent(self) -> bool:
        unique = set(self.values.values())
        return len(unique) <= 1

    @property
    def is_universal(self) -> bool:
        return len(self.sources) > 0 and len(set(self.sources)) == len(self.sources)


@dataclass
class DiffGraph:
    nodes: Dict[str, GraphNode] = field(default_factory=dict)
    source_names: List[str] = field(default_factory=list)

    def all_keys(self) -> List[str]:
        return sorted(self.nodes.keys())

    def inconsistent_keys(self) -> List[str]:
        return sorted(k for k, n in self.nodes.items() if not n.is_consistent)

    def missing_in(self, source: str) -> List[str]:
        return sorted(
            k for k, n in self.nodes.items() if source not in n.values
        )

    def summary(self) -> str:
        total = len(self.nodes)
        inconsistent = len(self.inconsistent_keys())
        if inconsistent == 0:
            return f"{total} key(s) across {len(self.source_names)} source(s) — all consistent"
        return (
            f"{total} key(s) across {len(self.source_names)} source(s) — "
            f"{inconsistent} inconsistent"
        )


def build_diff_graph(envs: Dict[str, Dict[str, str]]) -> DiffGraph:
    """Build a DiffGraph from a mapping of source-name -> env dict."""
    graph = DiffGraph(source_names=list(envs.keys()))
    for source, env in envs.items():
        for key, value in env.items():
            if key not in graph.nodes:
                graph.nodes[key] = GraphNode(key=key)
            node = graph.nodes[key]
            if source not in node.sources:
                node.sources.append(source)
            node.values[source] = value
    return graph
