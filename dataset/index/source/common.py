'''
Load danh sách chunks đã validate
Nhiệm vụ:
1. Đọc file jsonl
2. Kiểm tra cấu trúc record
3. Kiểm tra các chunk_id trùng lặp
4. Trả về danh sách chunks theo đúng thứ tự ban đầu

Output của file này là list của một dictionary gồm chunk_id, text, document_id, version_id
Cung cấp các method cần thiết cho sparse và dense phục vụ nhu cầu trích xuất text và chunk id trong để làm định danh
'''

import json
from pathlib import Path


# Fields required for indexing and record lookup.
REQUIRED_FIELDS = (
    "chunk_id",
    "text",
    "document_id",
    "version_id",
)


def load_chunks(
    file_path: str | Path,
    eligible_only: bool = True
) -> list[dict]:
    """
    Read and validate records from a JSONL file.
    Args:
        file_path:
            Path to the JSONL dataset.
        eligible_only:
            If True, load only records with
            index_eligible == True. 
        --> Đây là điều kiện của file chunks.jsonl
    Returns:
        List of validated chunk dictionaries.
    Raises:
        FileNotFoundError:
            Dataset file does not exist.
        ValueError:
            Invalid JSON, missing required fields,
            empty values, or duplicate chunk IDs.
    """

    # Chuyển đầu vào thành đối tượng Path
    path = Path(file_path)

    # kiểm tra tồn tại
    if not path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    # Lưu lại các chunks hợp lệ
    chunks = []

    # Track IDs to detect duplicates.
    seen_ids = set()

    # Open the JSONL file using UTF-8.
    with path.open(
        mode="r",
        encoding="utf-8"
    ) as file:

        # Read one JSON object per line.
        for line_number, line in enumerate(
            file,
            start=1
        ):

            # Ignore blank lines.
            if not line.strip():
                continue

            # Convert JSON text into a dictionary.
            try:
                chunk = json.loads(line)

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON at line {line_number}"
                ) from error

            # Each record must be a JSON object.
            if not isinstance(chunk, dict):
                raise ValueError(
                    f"Expected JSON object at line "
                    f"{line_number}"
                )

            # Validate required fields.
            for field in REQUIRED_FIELDS:

                if field not in chunk:
                    raise ValueError(
                        f"Missing '{field}' at line "
                        f"{line_number}"
                    )

                # Required fields must be strings.
                value = chunk[field]

                if (
                    not isinstance(value, str)
                    or not value.strip()
                ):
                    raise ValueError(
                        f"Invalid '{field}' at line "
                        f"{line_number}"
                    )

            # Validate indexing eligibility.
            eligible = chunk.get(
                "index_eligible",
                False
            )

            if not isinstance(eligible, bool):
                raise ValueError(
                    f"Invalid index_eligible at line "
                    f"{line_number}"
                )

            # Reject duplicate IDs before filtering.
            chunk_id = chunk["chunk_id"]

            if chunk_id in seen_ids:
                raise ValueError(
                    f"Duplicate chunk_id: {chunk_id}"
                )

            seen_ids.add(chunk_id)

            # Skip records excluded from indexing.
            if eligible_only and not eligible:
                continue

            # Keep the entire original record.
            chunks.append(chunk)

    # Prevent building an index with zero chunks.
    if not chunks:
        raise ValueError(
            "No valid chunks available for indexing."
        )

    return chunks


def extract_texts(chunks: list[dict]) -> list[str]:
    """
    Extract texts while preserving chunk order.

    Input:
        List of chunk records.

    Output:
        List of text strings.
    """

    return [
        chunk["text"]
        for chunk in chunks
    ]


def extract_chunk_ids(
    chunks: list[dict]
) -> list[str]:
    """
    Extract chunk IDs while preserving chunk order.

    Input:
        List of chunk records.

    Output:
        List of chunk ID strings.
    """

    return [
        chunk["chunk_id"]
        for chunk in chunks
    ]
