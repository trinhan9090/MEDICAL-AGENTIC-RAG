'''
gọi BM25, BGE-M3, thực hiện fusion và trả kết quả.

Module: hybrid.py
Chức năng: Kết hợp BM25 và BGE-M3 bằng Standard RRF.
Input: Query và các retriever đã load index.
Output: Top-K kết quả sau RRF.

Qui trình:
Query → BM25 Top-20 + BGE-M3 Top-20 → RRF → Top-7

method chính của calss này là search(), nhận vào query và top-k sau đó gọi đến sparse (BM25), dense(BGE-M3) và fusion (RRF score)
'''
from .fusion import RRFFusion

class HybridRetriever:
    # Khởi tạo các retriever và cấu hình RRF
    def __init__(
        self,
        sparse,
        dense,
        rrf_k: int = 60,
        retriever_top_k: int = 20,
        fusion_top_k: int = 7
    ):
        if retriever_top_k <= 0 or fusion_top_k <= 0:
            raise ValueError("Các giá trị top_k phải > 0.")
        self.sparse = sparse
        self.dense = dense
        self.fusion = RRFFusion(k=rrf_k)
        self.retriever_top_k = retriever_top_k
        self.fusion_top_k = fusion_top_k

    # Thực hiện tìm kiếm song song về mặt logic và kết hợp bằng RRF
    def search(self, query: str, top_k: int | None = None) -> dict:
        """
        Input:
            query: Câu hỏi cần retrieval.
            top_k: Số chunks sau RRF, mặc định dùng fusion_top_k.
        Output:
            dict chứa kết quả BM25, BGE-M3 và RRF.
        """
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query không được để trống.")
        final_k = self.fusion_top_k if top_k is None else top_k
        if final_k <= 0:
            raise ValueError("top_k phải > 0.")

        # Truy xuất tối đa 20 chunks từ mỗi phương pháp
        sparse_results = self.sparse.search(
            query,
            top_k=self.retriever_top_k
        )
        dense_results = self.dense.search(
            query,
            top_k=self.retriever_top_k
        )

        # Kết hợp hai danh sách bằng Standard RRF
        fused_results = self.fusion.fuse(
            result_lists=[sparse_results, dense_results],
            top_k=final_k
        )

        # Giữ cả ba danh sách phục vụ kiểm thử và đánh giá
        return {
            "query": query,
            "sparse_results": sparse_results,
            "dense_results": dense_results,
            "fused_results": fused_results
        }
