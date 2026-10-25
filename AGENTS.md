# AGENTS.md — Vietnamese Medical Raw Corpus v2

## 1. Mission

You are a data-acquisition agent for a university research project on trustworthy, Vietnamese-language medical Agentic RAG. **Your only task is to build a new, auditable raw-document collection from legitimate public sources.** Do not implement chunking, create KB metadata schemas, build indexes, change retrieval code, or modify the existing corpus.

The user will decide parsing, chunking, and KB metadata **after** reviewing the raw files.

## 2. Absolute destination (Windows)

```text
D:\1_TaiLieuHocTap\2627\DuAn_KhoaLuan\Demo_Khang\DACNTT\data\raw_v2
```

All newly acquired files and acquisition records must stay **inside `raw_v2`**. Use the project root only to locate the existing code; do not save files under other projects (including `Demo_Nhan`). If the destination does not exist, create it. Do not delete, overwrite, rename, or edit files outside `raw_v2`.

Suggested structure (organize only raw source material and a simple acquisition log):

```text
raw_v2/
├── diabetes/
├── kidney/
├── cardiovascular/
├── hypertension/
├── _records/
│   ├── sources.csv
│   ├── acquisition_report.md
│   └── unresolved_sources.md
└── README.md
```

Documents may overlap specialties; store **one authoritative copy** in the most appropriate folder, not multiple duplicates. Folder placement is for acquisition convenience only, not a final taxonomy. Keep original PDFs unaltered and retain their native language.

## 3. Collection scope and priority

Prioritize **Vietnamese, official clinical guidelines** published by the Vietnam Ministry of Health (Bộ Y tế), the Administration of Medical Services (Cục Quản lý Khám, chữa bệnh, `kcb.vn`), or provincial health authorities hosting identifiable official releases. Focus on:

1. Diabetes (especially type 2 diabetes and related complications)
2. Chronic kidney disease and kidney-related diseases
3. Cardiovascular disease, including heart failure and coronary disease
4. Hypertension

Prefer primary Ministry/authority PDFs rather than reposted or modified copies. Avoid blogs, general health articles, anonymous documents, promotional content, paywalled material, copyrighted mirrors without permission, and machine-generated summaries.

### Starter discovery targets

Treat these as **leads to verify, not proof that a file is current, downloadable, or licensed for redistribution**. Confirm exact document title, decision number, signing/publication date, download URL, and relationship to amendments or replacement decisions on an authoritative site **before accepting** any file.

| Priority | Topic | Candidate | Candidate source |
|---|---|---|---|
| P0 | Kidney | Quyết định **2388/QĐ-BYT (12/08/2024)** — *Hướng dẫn chẩn đoán và điều trị bệnh thận mạn và một số bệnh lý thận* | `https://kcb.vn/phac-do/quyet-dinh-so-2388-qd-byt-ngay-12-8-2024-ve-viec-ban-hanh-tai-lieu-chuyen-mon-huong-dan-chan-doan-va-dieu-tri-benh-than-.html` |
| P0 | Cardiovascular | Quyết định **1857/QĐ-BYT (05/07/2022)** — *Hướng dẫn chẩn đoán và điều trị suy tim cấp và mạn* | `https://kcb.vn/phac-do/quyet-dinh-1857-qd-byt-ngay-05-07-2022-ve-viec-ban-hanh-tai-lieu-chuyen-mon-huong-dan-chan-doan-va-dieu-tri-suy-tim-cap-.html` |
| P0 | Cardiovascular | Quyết định **2248/QĐ-BYT (2023)** — *Hướng dẫn chẩn đoán và điều trị hội chứng mạch vành mạn* | Search `kcb.vn`, `moh.gov.vn`, and authoritative Department of Health sites; independently confirm date |
| P1 | Diabetes | Quyết định **3510/QĐ-BYT (2025)** — *Hướng dẫn chẩn đoán và điều trị bệnh thần kinh đái tháo đường* | `https://emohbackup.moh.gov.vn/publish/attach/getfile/413412` |
| P1 | Diabetes | Quyết định **1530/QĐ-BYT (24/03/2023)** — *Hướng dẫn chẩn đoán và điều trị loét bàn chân do đái tháo đường* | `https://kcb.vn/tai-lieu/huong-dan-chan-doan-dieu-tri/quyet-dinh-so-1530-qd-byt-ngay-24-3-2023-ve-viec-ban-hanh-tai-lieu-chuyen-mon-huong-dan-chan-doan-dieu-tri-loet-ban-chan.html` |
| P1 | Cardiovascular | Quyết định **5333/QĐ-BYT (2020)** — *Dự phòng tiên phát bệnh tim mạch* | Search authoritative Ministry/Department of Health portal |
| P1 | Diabetes amendment | Quyết định **1353/QĐ-BYT (23/02/2021)** — amendment to **5481/QĐ-BYT (2020)** type 2 diabetes guideline | Verify on official sites and acquire amendment if permitted |
| P2 | Hypertension | Seek the **most recent verifiable authoritative Vietnamese** guideline covering hypertension | Verify status carefully; do not automatically treat **3192/QĐ-BYT (2010)** as current |

The user's original PDF *Hướng dẫn chẩn đoán và điều trị đái tháo đường típ 2*, **5481/QĐ-BYT (2020)**, is already part of the previous corpus. Do **not** overwrite or alter it. You may download a separately verified public copy into `raw_v2` only if needed for a self-contained source set; record the overlap and separate any redistribution-rights uncertainty. Avoid unnecessary duplication.

### Sourcing safeguards

- Verify the existence and exact identification of every candidate; do not fabricate or infer a direct PDF link from a landing-page URL.
- Search for correction, amendment, withdrawal, and replacement notices using the decision number, title, and authoritative website; record what was checked and the date checked.
- A source is **not guaranteed clinically current or error-free**. Flag uncertainty instead of making a definitive claim of medical validity. If a newer replacement exists, prioritize the replacement and label the older file as superseded; download the older file only if justified for comparative research and clearly segregated.
- Prefer accessible, official documents with unambiguous provenance; mark inaccessible, unverifiable, or ambiguous documents as `unresolved` and **do not silently substitute** a third-party copy.
- Check website terms, robots.txt where applicable, and reproduction/download restrictions. Respect rate limits, use moderate request pacing, and never bypass authentication, CAPTCHA, or access restrictions. An accessible file does not automatically confer redistribution rights.
- Collect **public source documents only**. Do not collect patient records, identifying health data, or confidential hospital files.

## 4. Acquisition procedure

For each candidate:

1. Find the official publication/decision page and original PDF attachment.
2. Confirm title, issuing authority, decision number/date, and whether it appears amended, revoked, or replaced. Resolve inconsistencies between PDF cover and publication page; record them as notes.
3. Check **access/download restrictions separately from redistribution rights**. For this task, the user wants private research copies of publicly provided official documents, not public redistribution. When the official publisher directly exposes a PDF for normal public download, and no clear prohibition on downloading applies, **attempt to download it** even if permission to redistribute the corpus has not been established. Record redistribution permission as `unknown` in the notes, and do not upload, share, republish, or distribute the PDFs. If downloading itself is explicitly prohibited, requires evading login/CAPTCHA/paywall, or violates a clear site restriction, skip and document the restriction. Respect robots.txt where relevant for automated requests; if access cannot be established safely, mark unresolved with the actual technical reason. Do not equate a copyright footer or absence of a reuse license with an automatic prohibition on retrieving a public PDF for internal review.
4. Download the **original bytes** to a descriptive `.pdf` filename (e.g., `BYT_2388_2024_benh_than_man.pdf`). Do not alter, translate, rewrite, compress, concatenate, or OCR the raw PDF.
5. Validate that the download is an actual readable PDF (not an HTML error page); inspect page count, at least first and last pages, and any obvious corruption/truncation. Sample any significant tables/figures for legibility. Scanned PDFs are allowed as raw source material; merely flag them for later parsing decisions.
6. Compute file SHA-256 **for duplicate detection and acquisition auditing only**. Compare file hashes with other files downloaded in this run, and avoid duplicate raw copies. Do not implement runtime provenance or chunk-level hashes.
7. Enter one acquisition record in `_records/sources.csv` and summarize any issues in `_records/acquisition_report.md`.

Use normal download tooling available to the coding agent. Do not require a particular crawler library. Do not launch broad website crawls; operate from a verified, bounded source list.

## 5. Minimal acquisition log (NOT a KB metadata schema)

Create `_records/sources.csv` with one row per candidate using only these practical collection fields:

```csv
filename,title,decision_number,document_date,issuer,source_page_url,pdf_url,language,topic,download_status,version_status,sha256,page_count,notes
```

Rules:

- `download_status`: `downloaded`, `skipped`, `failed`, or `unresolved`.
- `version_status`: `checked_no_replacement_found`, `amended`, `superseded`, or `unknown` (do not imply legal/clinical currency beyond evidence).
- Leave unavailable fields blank; **do not invent values**.
- `source_page_url` and `pdf_url` are the actual verified URLs, not placeholders or search-result URLs.
- This CSV is a download audit trail only. **Do not design chunk IDs, document-level KB schemas, embedding fields, section taxonomy, or a canonical `chunks.jsonl`.**

## 6. Strict exclusions

Do **not**:

- Modify the existing 621-chunk KB, its source files, or any existing benchmark.
- Generate `chunks.jsonl`, embeddings, FAISS, BM25 or RRF indexes.
- Run OCR, automatic translation, summarization, semantic extraction, or section-aware chunking.
- Generate synthetic Q&A, gold labels, or a benchmark dataset.
- Train or fine-tune any model.
- Change `planner/`, `models/`, `evaluator/`, `generator/`, `verifier/`, or retrieval pipeline code.
- Claim official approval, current clinical validity, or permission to redistribute without verified evidence.

If the source PDF is scanned or contains complex tables, **record the concern**, and leave parsing strategy to the user.

## 7. Acceptance criteria

The task is complete when:

- At least one publicly downloadable, technically accessible official P0/P1 PDF has actually been saved and validated; otherwise explicitly report the verified download-specific blockers and do **not** present a metadata-only report as the intended deliverable.
- Every priority P0 candidate has been attempted and has an explicit status; continue through P1/P2 where feasible.
- Every successfully acquired PDF opens and has a plausible page count.
- All downloaded PDFs reside under the specified `raw_v2` directory and are unchanged original files.
- Acquisition records give traceable official URLs, decision identifiers, audit timestamps/notes (when checked), SHA-256 checksums, and observed issues.
- Duplicates, replacement notices, rights restrictions, and download failures are documented rather than hidden.
- No existing dataset, code, index, or benchmark was modified.
- No chunking or KB metadata design has been performed.

## 8. Final handoff report to user

Report concisely in Vietnamese:

1. Number of downloaded PDF files, their filenames, topic, authority, decision numbers, and page counts.
2. Which official source URLs were verified and which remain unresolved.
3. Relevant amendments, replacements, version ambiguity, usage restrictions, scanned pages, or corrupted PDFs.
4. Exact location of all outputs under `D:\1_TaiLieuHocTap\2627\DuAn_KhoaLuan\Demo_Khang\DACNTT\data\raw_v2`.
5. Explicit statement: **"Chưa thực hiện chunking, metadata cho KB hay indexing; chờ người dùng quyết định."**

Do not claim success for any file unless it was actually downloaded and checked on the user's machine.

## 9. Retry instructions based on the first acquisition report (2026-10-22)

Previous run downloaded **zero PDFs** because the acquisition rule above was interpreted as requiring a clearly licensed right to *redistribute* the corpus before downloading even a public file for local research. That is not the intended criterion. **Perform downloads in this run; do not stop after URL discovery and rights research.**

Start with these direct official PDF URLs already logged in `sources.csv` (still verify response and bytes; do not assume success):

1. `2388/QĐ-BYT`: `https://kcb.vn/upload/2005611/20240826/QD_ban_hanh_HD_chan_doan__dieu_tri_benh_than_man_va_mot_so_benh_ly_than__2024_08_12_f0584.pdf`
2. `1857/QĐ-BYT`: `https://kcb.vn/upload/2005611/20220722/1857_Huong_dan_suy_tim_signed_8e519ed3f9.pdf`
3. `1530/QĐ-BYT`: `https://kcb.vn/upload/2005611/20230421/QD_2023_1530_Quyet_dinh_ban_hanh_tai_lieu_chuyen_mon__Huong_dan_chan_doan_va_dieu_tri_Loet_ban_chan_do_dai_thao_duong__25013.pdf`

For each: fetch over HTTPS with certificate verification enabled, save the original bytes under the correct topic folder, verify PDF signature/parsability/page count and first/last pages, compute SHA-256, then update `_records/sources.csv` status to `downloaded`. If a fetch fails, record HTTP status, TLS error or timeout and try only reasonable official alternative sources. Do not use unofficial mirrors, circumvent restrictions, or turn off certificate checks. Continue through 2248, 3510, 5333, 1353, and other candidates as feasible.

Do not attempt to conclusively certify medical currency. Record `version_status=unknown` when needed, with sources checked. Version uncertainty **does not itself prohibit downloading** a clearly identified historical official document into a research raw folder; the document can be evaluated for KB inclusion later.

This task ends at **raw PDF acquisition**. Do not perform parsing, OCR, sectioning, chunking, embedding, or KB metadata design.
