from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cluster:
    cluster_id: int
    indices: tuple[int, ...]


def multisect_kmeans(
    embeddings,
    *,
    max_cluster_size: int = 30,
    k_split: int = 10,
    max_iter: int = 100,
    seed: int = 42,
    threads: int | None = None,
) -> list[Cluster]:
    """Iteratively split FAISS K-means clusters until each has <= max_cluster_size.

    This is a clean implementation of the method described in PlantConnectome; it avoids
    W&B and hard-coded 128-thread assumptions in the public research script.
    """
    try:
        import faiss
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install forestconnectome[resolution] for FAISS clustering") from exc

    x = np.asarray(embeddings, dtype="float32")
    if x.ndim != 2:
        raise ValueError("embeddings must be a 2D array")
    if max_cluster_size < 1 or k_split < 2:
        raise ValueError("invalid clustering parameters")
    if threads is not None:
        faiss.omp_set_num_threads(threads)

    all_indices = np.arange(x.shape[0], dtype=np.int64)
    stack = [(all_indices, x)]
    final: list[Cluster] = []

    while stack:
        indices, sub = stack.pop()
        if len(indices) <= max_cluster_size:
            final.append(Cluster(len(final), tuple(int(i) for i in indices)))
            continue

        k = min(k_split, len(indices))
        km = faiss.Kmeans(sub.shape[1], k, niter=max_iter, seed=seed, verbose=False)
        km.train(sub)
        _, labels = km.index.search(sub, 1)
        labels = labels.reshape(-1)
        for label in range(k):
            mask = labels == label
            if mask.any():
                stack.append((indices[mask], sub[mask]))

    return final
