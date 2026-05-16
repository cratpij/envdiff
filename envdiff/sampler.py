"""Sample a subset of keys from an env dict, useful for previews and testing."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SampleResult:
    source: str
    sampled: Dict[str, str]
    total_keys: int
    sample_size: int
    seed: Optional[int] = None
    strategy: str = "random"

    def coverage(self) -> float:
        """Return fraction of keys included in the sample."""
        if self.total_keys == 0:
            return 1.0
        return self.sample_size / self.total_keys

    def summary(self) -> str:
        pct = f"{self.coverage() * 100:.1f}%"
        return (
            f"Sampled {self.sample_size}/{self.total_keys} keys "
            f"({pct}) from '{self.source}' using strategy='{self.strategy}'."
        )


def sample_env(
    env: Dict[str, str],
    n: int,
    *,
    strategy: str = "random",
    seed: Optional[int] = None,
    source: str = "<env>",
) -> SampleResult:
    """Return a SampleResult containing *n* keys chosen from *env*.

    Strategies:
      - ``random``  – uniformly random selection (default)
      - ``first``   – first *n* keys in insertion order
      - ``last``    – last *n* keys in insertion order
    """
    keys: List[str] = list(env.keys())
    total = len(keys)
    n = min(max(n, 0), total)

    if strategy == "first":
        chosen = keys[:n]
    elif strategy == "last":
        chosen = keys[total - n :]
    else:  # random
        rng = random.Random(seed)
        chosen = rng.sample(keys, n)

    sampled = {k: env[k] for k in chosen}
    return SampleResult(
        source=source,
        sampled=sampled,
        total_keys=total,
        sample_size=n,
        seed=seed,
        strategy=strategy,
    )


def sample_env_file(
    path: str,
    n: int,
    *,
    strategy: str = "random",
    seed: Optional[int] = None,
) -> SampleResult:
    """Parse *path* and return a sample of its keys."""
    from envdiff.parser import parse_env_file

    env = parse_env_file(path)
    return sample_env(env, n, strategy=strategy, seed=seed, source=path)
