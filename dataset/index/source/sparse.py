'''
BM25 index + mapping
Cung cấp các method như
build: xây dựng index
save: lưu kết quả
load: đọc index đã lưu
search: trả về kết quả xếp hạng (khi có query)

Đối với tiếng Việt sẽ dùng underthesea.word_tokenize()
Tiếng Anh thì dùng regex
'''


"""
Module: sparse.py
Chức năng: Xây dựng, lưu, đọc và truy vấn BM25 Index.
Input: Danh sách chunks từ common.py.
Output: BM25 index và danh sách kết quả gồm chunk_id, score, rank.
"""
import json
import pickle
import re
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from underthesea import word_tokenize
from .common import extract_texts, extract_chunk_ids
from tqdm.auto import tqdm

# Tokenizer dùng chung cho indexing và searching
def tokenize(text: str, language: str | None = None) -> list[str]:
    """
    Input:
        text: Nội dung cần tách từ.
        language: "vi", "en" hoặc None.
    Output:
        Danh sách tokens đã chuẩn hóa.
    """
    text = text.lower().strip()
    # Tự xác định tiếng Việt nếu chưa cung cấp language
    if language is None:
        language = "vi" if re.search(
            r"[ăâđêôơưàáạảãằắặẳẵầấậẩẫèéẹẻẽềếệểễìíịỉĩòóọỏõồốộổỗờớợởỡùúụủũừứựửữỳýỵỷỹ]",
            text
        ) else "en"
    # Tách từ tiếng Việt, giữ từ ghép như "đái tháo đường"
    if language == "vi":
        tokens = word_tokenize(text)
    elif language == "en":
        tokens = re.findall(r"\w+(?:[.-]\w+)*", text, flags=re.UNICODE)
    else:
        raise ValueError(f"Ngôn ngữ không được hỗ trợ: {language}")
    return [token.strip() for token in tokens if token.strip()]

class SparseRetriever:
    """
    Các biến trạng thái quan trọng:
        self.bm25: BM25 index đã xây dựng hoặc load từ file.
        self.chunk_ids: Danh sách ID theo đúng thứ tự trong index.
        self.languages: Ngôn ngữ của từng chunk, dùng lúc indexing.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.bm25 = None
        self.chunk_ids = []
        self.languages = []

    # Tạo BM25 index từ nội dung và ngôn ngữ của từng chunk
    def build(self, chunks: list[dict]) -> None:
        """
        Input: list[dict] từ load_chunks().
        Output: Cập nhật self.bm25, self.chunk_ids, self.languages.
        """
        texts = extract_texts(chunks)
        self.chunk_ids = extract_chunk_ids(chunks)
        self.languages = [chunk.get("language") for chunk in chunks]
        # Tokenize từng chunk và hiển thị tiến trình
        tokenized_corpus = [
            tokenize(text, language)
            for text, language in tqdm(
                zip(texts, self.languages),
                total=len(texts),
                desc="BM25 Tokenizing",
                unit="chunk"
            )
        ]
        if any(len(tokens) == 0 for tokens in tokenized_corpus):
            raise ValueError("Có chunk không tạo được token.")
        self.bm25 = BM25Okapi(
            tokenized_corpus,
            k1=self.k1,
            b=self.b
        )

    # Lưu BM25 object và ID mapping xuống thư mục parse
    def save(self, output_dir: str | Path) -> None:
        """
        Input: Đường dẫn output_dir.
        Output: bm25.pkl, chunk_ids.json, config.json.
        """
        if self.bm25 is None:
            raise RuntimeError("Chưa xây dựng BM25 index.")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        with (output_dir / "bm25.pkl").open("wb") as f:
            pickle.dump(self.bm25, f)
        with (output_dir / "chunk_ids.json").open("w", encoding="utf-8") as f:
            json.dump(self.chunk_ids, f, ensure_ascii=False, indent=2)
        config = {"k1": self.k1, "b": self.b, "tokenizer": "underthesea_regex_v1"}
        with (output_dir / "config.json").open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    # Đọc lại BM25 index để không phải index lại trong mỗi lần chạy
    def load(self, output_dir: str | Path) -> None:
        """
        Input: Thư mục chứa các file BM25.
        Output: Khôi phục self.bm25 và self.chunk_ids.
        """
        output_dir = Path(output_dir)
        with (output_dir / "bm25.pkl").open("rb") as f:
            self.bm25 = pickle.load(f)
        with (output_dir / "chunk_ids.json").open("r", encoding="utf-8") as f:
            self.chunk_ids = json.load(f)
        with (output_dir / "config.json").open("r", encoding="utf-8") as f:
            config = json.load(f)
        if config["tokenizer"] != "underthesea_regex_v1":
            raise ValueError("Tokenizer version không tương thích.")
        self.k1 = config["k1"]
        self.b = config["b"]
        if self.bm25.corpus_size != len(self.chunk_ids):
            raise ValueError("BM25 index và chunk_ids không đồng bộ.")
        
    # Tính BM25 score, sắp xếp giảm dần và trả về Top-K
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Input:
            query: Câu hỏi tiếng Việt hoặc tiếng Anh.
            top_k: Số chunks cần lấy.
        Output:
            list[dict] gồm chunk_id, score, rank, retriever.
        """
        if self.bm25 is None:
            raise RuntimeError("Chưa load hoặc build BM25 index.")
        if not query.strip() or top_k <= 0:
            raise ValueError("Query phải có nội dung và top_k > 0.")
        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        # Bỏ các chunks có score bằng 0 hoặc âm, tránh kết quả không khớp từ vựng
        indices = np.argsort(-scores, kind="stable")
        indices = [int(i) for i in indices if scores[i] > 0][:top_k]
        return [
            {
                "chunk_id": self.chunk_ids[i],
                "score": float(scores[i]),
                "rank": rank,
                "retriever": "bm25"
            }
            for rank, i in enumerate(indices, start=1)
        ]
