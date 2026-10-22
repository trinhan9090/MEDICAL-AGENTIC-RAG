'''
Điều phối quá trình indexing
'''

"""
Module: build_indexes.py
Chức năng: Điều phối xây dựng BM25 và BGE-M3 indexes.
Input: dataset/chunks.jsonl
Output:
    dataset/index/parse/
    dataset/index/dense/
"""
import argparse
import time
from pathlib import Path
from .common import load_chunks
from .sparse import SparseRetriever
from .dense import DenseRetriever

class IndexBuilder:
    # Khởi tạo đường dẫn, tham số indexing và các retriever
    def __init__(
        self,
        dataset_path: str | Path = "dataset/chunk/chunks.jsonl",
        index_root: str | Path = "dataset/index",
        batch_size: int = 2,
        max_length: int = 1024
    ):
        self.dataset_path = Path(dataset_path)
        self.index_root = Path(index_root)
        self.sparse_dir = self.index_root / "parse"
        self.dense_dir = self.index_root / "dense"
        self.chunks = []
        self.sparse = SparseRetriever()
        self.dense = DenseRetriever(
            model_name="BAAI/bge-m3",
            batch_size=batch_size,
            max_length=max_length,
            use_fp16=True
        )

    # Đọc dataset duy nhất một lần cho cả BM25 và BGE-M3
    def load_dataset(self) -> None:
        self.chunks = load_chunks(self.dataset_path)
        print(f"[DATASET] Loaded {len(self.chunks)} chunks.")

    # Xây dựng và lưu BM25 index
    def build_sparse(self) -> None:
        start = time.perf_counter()
        print("\n[BM25] Building sparse index...")
        self.sparse.build(self.chunks)
        self.sparse.save(self.sparse_dir)
        elapsed = time.perf_counter() - start
        print(f"[BM25] Indexed: {self.sparse.bm25.corpus_size}")
        print(f"[BM25] Saved: {self.sparse_dir}")
        print(f"[BM25] Time: {elapsed:.2f}s")

    # Xây dựng và lưu FAISS index bằng BGE-M3
    def build_dense(self) -> None:
        start = time.perf_counter()
        print("\n[BGE-M3] Building dense index...")
        self.dense.build(self.chunks)
        self.dense.save(self.dense_dir)
        elapsed = time.perf_counter() - start
        print(f"[BGE-M3] Indexed: {self.dense.index.ntotal}")
        print(f"[BGE-M3] Dimension: {self.dense.dimension}")
        print(f"[BGE-M3] Saved: {self.dense_dir}")
        print(f"[BGE-M3] Time: {elapsed:.2f}s")

    # Kiểm tra số lượng và chunk ID mapping sau khi indexing
    def validate(self, mode: str) -> None:
        expected = len(self.chunks)
        if mode in ("both", "sparse"):
            assert self.sparse.bm25.corpus_size == expected
            assert len(self.sparse.chunk_ids) == expected
        if mode in ("both", "dense"):
            assert self.dense.index.ntotal == expected
            assert len(self.dense.chunk_ids) == expected
        if mode == "both":
            assert self.sparse.chunk_ids == self.dense.chunk_ids
        print("\n[VALIDATION] All checks passed.")

    # Điều phối toàn bộ quá trình indexing
    def run(self, mode: str = "both") -> None:
        if mode not in ("both", "sparse", "dense"):
            raise ValueError(f"Invalid mode: {mode}")
        start = time.perf_counter()
        self.load_dataset()
        if mode in ("both", "sparse"):
            self.build_sparse()
        if mode in ("both", "dense"):
            self.build_dense()
        self.validate(mode)
        print(f"\n[DONE] Total time: {time.perf_counter() - start:.2f}s")


# Entry point khi chạy trực tiếp bằng python -m
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build BM25 and BGE-M3 indexes."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="dataset/chunk/chunks.jsonl"
    )
    parser.add_argument(
        "--index-root",
        type=str,
        default="dataset/index"
    )
    parser.add_argument(
        "--mode",
        choices=["both", "sparse", "dense"],
        default="both"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=1024
    )
    args = parser.parse_args()
    builder = IndexBuilder(
        dataset_path=args.dataset,
        index_root=args.index_root,
        batch_size=args.batch_size,
        max_length=args.max_length
    )
    builder.run(mode=args.mode)
