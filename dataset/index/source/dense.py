'''
FAISS index + mapping
Cung cấp các method như
build: xây dựng index
save: lưu kết quả
load: đọc index đã lưu
search: trả về kết quả xếp hạng (khi có query)
'''


"""
Module: dense.py
Chức năng: Tạo Dense Embedding bằng BGE-M3 và xây dựng FAISS Index.
Input: Danh sách chunks từ common.py.
Output: FAISS index và danh sách kết quả gồm chunk_id, score, rank.
"""
import json
from pathlib import Path
import faiss
import numpy as np
import torch
from FlagEmbedding import BGEM3FlagModel
from .common import extract_texts, extract_chunk_ids

class DenseRetriever:
    """
    Các biến trạng thái quan trọng:
        self.model: BGE-M3 embedding model.
        self.index: FAISS index.
        self.chunk_ids: Ánh xạ vị trí vector về chunk gốc.
        self.dimension: Số chiều của mỗi embedding.
    """
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        batch_size: int = 8,
        max_length: int = 1024,
        use_fp16: bool = True
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        self.use_fp16 = use_fp16
        self.model = None
        self.index = None
        self.chunk_ids = []
        self.dimension = None

    # Load embedding model một lần và tái sử dụng khi indexing/search
    def load_model(self) -> None:
        if self.model is not None:
            return
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        print(f"Loading BGE-M3 on {device}")
        self.model = BGEM3FlagModel(
            self.model_name,
            use_fp16=self.use_fp16 and device != "cpu",
            devices=[device]
        )

    # Chuyển danh sách văn bản thành ma trận vector float32
    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Input: Danh sách strings.
        Output: NumPy matrix shape (N, 1024), dtype float32.
        """
        self.load_model()
        # Tạo embedding theo batch và hiển thị tiến trình
        outputs = self.model.encode(
            texts,
            batch_size=self.batch_size,
            max_length=self.max_length,
            return_dense=True,
            return_sparse=False,
            return_colbert_vecs=False,
        )
        embeddings = np.asarray(
            outputs["dense_vecs"],
            dtype=np.float32
        )
        if embeddings.ndim != 2:
            raise ValueError("Embeddings phải là ma trận 2 chiều.")
        if embeddings.shape[0] != len(texts):
            raise ValueError("Số embeddings không khớp số văn bản.")
        if not np.isfinite(embeddings).all():
            raise ValueError("Embedding chứa NaN hoặc Infinity.")
        return np.ascontiguousarray(embeddings)
    
    # Tạo FAISS IndexFlatIP từ tất cả chunk embeddings
    def build(self, chunks: list[dict]) -> None:
        """
        Input: Danh sách chunk records.
        Output: Cập nhật self.index, self.dimension và self.chunk_ids.
        """
        texts = extract_texts(chunks)
        self.chunk_ids = extract_chunk_ids(chunks)
        embeddings = self.encode(texts)
        # Chuẩn hóa L2 trước khi thêm vào FAISS
        faiss.normalize_L2(embeddings)
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        if self.index.ntotal != len(self.chunk_ids):
            raise ValueError("FAISS index và chunk IDs không đồng bộ.")
        
    # Lưu index và chunk ID mapping để tái sử dụng
    def save(self, output_dir: str | Path) -> None:
        """
        Input: Thư mục output.
        Output: bge_m3.faiss, chunk_ids.json, config.json.
        """
        if self.index is None:
            raise RuntimeError("Chưa xây dựng FAISS index.")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(
            self.index,
            str(output_dir / "bge_m3.faiss")
        )
        with (output_dir / "chunk_ids.json").open("w", encoding="utf-8") as f:
            json.dump(self.chunk_ids, f, ensure_ascii=False, indent=2)
        config = {
            "model_name": self.model_name,
            "batch_size": self.batch_size,
            "max_length": self.max_length,
            "use_fp16": self.use_fp16,
            "dimension": self.dimension
        }
        with (output_dir / "config.json").open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    # Đọc lại FAISS index và khôi phục cấu hình embedding
    def load(self, output_dir: str | Path) -> None:
        """
        Input: Thư mục chứa index đã xây dựng.
        Output: Khôi phục FAISS index, mapping và config.
        """
        output_dir = Path(output_dir)
        self.index = faiss.read_index(
            str(output_dir / "bge_m3.faiss")
        )
        with (output_dir / "chunk_ids.json").open("r", encoding="utf-8") as f:
            self.chunk_ids = json.load(f)
        with (output_dir / "config.json").open("r", encoding="utf-8") as f:
            config = json.load(f)
        self.model_name = config["model_name"]
        self.batch_size = config["batch_size"]
        self.max_length = config["max_length"]
        self.use_fp16 = config["use_fp16"]
        self.dimension = config["dimension"]
        # Model sẽ được load khi thực hiện search, không cần load lúc đọc index
        self.model = None
        if self.index.ntotal != len(self.chunk_ids):
            raise ValueError("FAISS index và chunk IDs không đồng bộ.")
        if self.index.d != self.dimension:
            raise ValueError("Số chiều của FAISS index không khớp config.")
        
    # Encode query rồi tìm Top-K vectors tương đồng nhất
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Input: Query và số chunks cần truy xuất.
        Output: list[dict] gồm chunk_id, score, rank, retriever.
        """
        if self.index is None:
            raise RuntimeError("Chưa load hoặc build FAISS index.")
        if not query.strip() or top_k <= 0:
            raise ValueError("Query phải có nội dung và top_k > 0.")
        query_embedding = self.encode([query])
        faiss.normalize_L2(query_embedding)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, k)
        results = []
        for rank, (score, idx) in enumerate(
            zip(scores[0], indices[0]),
            start=1
        ):
            if idx < 0:
                continue
            results.append({
                "chunk_id": self.chunk_ids[int(idx)],
                "score": float(score),
                "rank": rank,
                "retriever": "dense"
            })
        return results
