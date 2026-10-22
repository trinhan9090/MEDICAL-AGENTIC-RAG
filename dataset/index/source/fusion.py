'''
Lớp này thực hiện việc nhận vào các evidence và tính điểm RRF.
Nó sẽ nhận vào top-k evidence của cả 2 thuật toán. 
Sau đó thực hiện tính toán và trả về điểm RRF

Module: fusion.py
Chức năng: Kết hợp các danh sách retrieval bằng Standard RRF.
Input: Các danh sách đã xếp hạng từ BM25 và BGE-M3.
Output: Danh sách chunk_id được xếp hạng theo RRF score.

Method chính của class này là fuse, được dùng để tính điểm RRF
'''

class RRFFusion:
    # Khởi tạo hằng số RRF, mặc định k=60
    def __init__(self, k: int = 60):
        if k < 0:
            raise ValueError("RRF k phải >= 0.")
        self.k = k

    # Tính điểm và kết hợp thứ hạng của các retriever
    def fuse(self, result_lists: list[list[dict]], top_k: int = 7) -> list[dict]:
        """
        Input:
            result_lists: Danh sách các ranked result lists.
            top_k: Số chunks lấy sau fusion.
        Output:
            list[dict]: chunk_id, rrf_score, rank, retrieval_sources.
        """
        if top_k <= 0:
            raise ValueError("top_k phải > 0.")
        rrf_scores = {}
        retrieval_sources = {}

        # Duyệt từng retriever và cộng điểm theo thứ hạng
        for results in result_lists:
            seen_ids = set()
            for result in results:
                chunk_id = result["chunk_id"]
                rank = result["rank"]
                retriever = result["retriever"]
                if not isinstance(rank, int) or rank < 1:
                    raise ValueError(f"Rank không hợp lệ: {rank}")
                if chunk_id in seen_ids:
                    raise ValueError(f"Trùng chunk_id trong một retriever: {chunk_id}")
                seen_ids.add(chunk_id)
                rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + 1.0 / (self.k + rank)
                retrieval_sources.setdefault(chunk_id, []).append(retriever)

        # Sắp xếp giảm dần theo RRF score, dùng chunk_id để xử lý trường hợp bằng điểm
        ranked_items = sorted(
            rrf_scores.items(),
            key=lambda item: (-item[1], item[0])
        )[:top_k]

        # Tạo danh sách kết quả cuối cùng
        return [
            {
                "chunk_id": chunk_id,
                "rrf_score": score,
                "rank": rank,
                "retrieval_sources": retrieval_sources[chunk_id]
            }
            for rank, (chunk_id, score) in enumerate(ranked_items, start=1)
        ]
