# Kiểm toán kho mã và phục hồi nguồn — 01/08

Ngày kiểm toán 2026-11-25 (+07). Phạm vi gồm lịch sử Git và cây làm việc trước khi cập nhật tài liệu, dữ liệu cục bộ, mã thí nghiệm và kiểm thử hiện có. Các số liệu chất lượng segmentation bên dưới đến từ bằng chứng đã lưu. Phiên kiểm toán chạy lại bộ kiểm thử và kiểm chứng dữ liệu, hash, cấu hình cùng mã nguồn liên quan.

## Trạng thái Git và checkpoint

`main` là nhánh duy nhất, tại `4dd1f550b41c02a169ae98d52e807cbd38b46ddd`. Một worktree, chưa cấu hình remote, không stash, không có thay đổi staged. Bốn commit reachable gồm `d7720fb` (khởi tạo P01), `ef8fc99` (preprocessing), `1bd57db` (chuẩn hóa dữ liệu), `4dd1f55` (nghiệm thu P02). Reflog còn `f300701`, commit P01 trước khi amend, giải thích hash lịch sử trong log P01.

| Trạng thái trước kiểm toán | Kiểm kê |
| --- | --- |
| Tracked | 103 tệp, gồm bộ khung P01, preprocessing P02, tài liệu, test và bằng chứng P01/P02 |
| Modified | 7 tệp: `.gitignore`, `CHANGELOG.md`, `docs/roadmap.md`, `docs/status.md`, `scripts/create_visual_review.py`, `features/trunk.py`, `segmentation/trunk.py` (hai tệp Python cuối dưới `src/tree_cbir/`) |
| Untracked | 172 tệp: báo cáo môn học, `docs/logs/P03.md`, 6 script, 17 module nguồn, 6 tệp test và 141 tệp dưới `outputs/trunk/` |
| Ignored | 507 ảnh nguồn và 507 ảnh chuẩn hóa, `.env`, `.venv/`, cache, mẫu preprocessing, ảnh và ZIP AUTO, toàn bộ `outputs/trunk/p03_2_v2/` |

Không có metadata Git để xác nhận tác giả của từng thay đổi chưa commit. Bằng chứng AUTO/V2 và bộ chuẩn bị P03-FINAL là các nhóm công việc nhận diện được từ đường dẫn, script, nội dung và snapshot. Phần được gọi là Antigravity/V3 trong yêu cầu tương ứng với bộ chuẩn bị supervised learning P03-FINAL được tìm thấy tại workspace.

Checkpoint cục bộ tại [pre_audit_checkpoint.zip](../../outputs/evaluation/team_preparation_01/pre_audit_checkpoint.zip) chứa 170 tệp, gồm bản sao byte-for-byte của thay đổi tracked, nguồn/test chưa tracked, báo cáo tham chiếu, script V2 đang bị ignore, annotation, manifest, bằng chứng dạng văn bản và 14 ZIP lịch sử. Các ảnh, NPZ và cache lớn còn tại vị trí cũ. `.env` và venv nằm ngoài checkpoint. ZIP và 14 ZIP lịch sử đều qua kiểm tra CRC, 170 SHA-256 thành viên khớp bản gốc, và patch tracked qua `git apply --check --reverse` trên cây trước kiểm toán. SHA-256 ZIP là `4e11e8ea5fb9433a9b182cd942e702b5904c0e1f4693299ee566b08bf36697a8`. [Checksum](../../outputs/evaluation/team_preparation_01/checkpoint.sha256) · [Kiểm kê Git đầy đủ](../../outputs/evaluation/team_preparation_01/git_inventory.json)

Để phục hồi, dựng một thư mục riêng từ commit gốc ghi trong `checkpoint_manifest.json`, rồi chép nội dung `tree/` trong ZIP vào đúng đường dẫn tương đối. `tracked_changes.patch` là cách thay thế để khôi phục phần tracked. Các baseline theo thời điểm nằm trong ZIP lồng dưới `tree/outputs/trunk/`. Chỉ mở các archive trong thư mục phục hồi riêng. Đường dẫn `outputs/evaluation/team_preparation_01/` đã bị `.gitignore` loại trừ, nên checkpoint cần được sao lưu hoặc bàn giao qua kênh nội bộ nếu đổi máy.

## Ma trận P01–P12

| Pha | Phân loại | Mã nguồn và bằng chứng |
| --- | --- | --- |
| P01 | ACCEPTED | Kiến trúc modular monolith, cấu hình Python/Compose, dataclass và hợp đồng 38 chiều. Log ghi nghiệm thu AC01–AC15. Phiên này chạy lại pgvector round trip với bảng tạm. |
| P02 | ACCEPTED | `preprocessing.py`, `utils/`, audit/standardization và contact sheet. 507 ảnh được xác thực lại. Log ghi người dùng đã duyệt 22 cặp crop/resize. |
| P03 | PARTIAL | Candidate, localization và `hybrid` hoạt động. AUTO chưa đạt ngưỡng. `extract_trunk_features` tính được X0–X8 ở mức **IMPLEMENTED BUT NOT ACCEPTED**. V2 và dữ liệu chuẩn bị V3 là **EXPERIMENTAL**. Chưa có nghiệm thu công thức, chính sách validity theo độ tin cậy và chất lượng mask độc lập. |
| P04 | NOT IMPLEMENTED | `segmentation/canopy.py`, `features/canopy.py` là placeholder. X9–X16 mới có đặc tả. |
| P05 | NOT IMPLEMENTED | `segmentation/branch.py`, `features/branch.py` là placeholder. X17–X19 mới có đặc tả. |
| P06 | NOT IMPLEMENTED | `segmentation/root.py`, `features/root.py` là placeholder. X20–X25 mới có đặc tả. |
| P07 | NOT IMPLEMENTED | `segmentation/context.py`, `features/context.py` là placeholder. X26–X37 mới có đặc tả. |
| P08 | NOT IMPLEMENTED | `extractor.py` là placeholder. Dataclass `FeatureExtractionResult` đã kiểm tra shape/validity nhưng chưa có pipeline ghép nhóm. |
| P09 | NOT IMPLEMENTED | `database.py`, `normalization.py`, `services/dataset.py` và `scripts/build_dataset.py` chưa triển khai. `sql/01_init.sql` bật extension vector theo P01. Chưa có schema sản xuất, migration, Min–Max hoặc ingestion. |
| P10 | NOT IMPLEMENTED | `similarity.py` và `services/retrieval.py` là placeholder. Top-5 trên bảng tạm chỉ kiểm tra toán tử pgvector của P01. |
| P11 | NOT IMPLEMENTED | `app.py` hiển thị tiêu đề/thông báo khởi tạo. Chưa có query, kết quả hoặc visualization tích hợp. |
| P12 | PARTIAL | Có unit test, integration P01 và evidence theo pha. `scripts/evaluate.py` thoát với thông báo chưa triển khai. Chưa có bộ đánh giá retrieval end-to-end hoặc hồ sơ nghiệm thu cuối. |

## Backend đang hoạt động và nguyên mẫu P03

Điểm vào thực tế là `tree_cbir.segmentation.trunk.segment_trunk(rgb, *, method='hybrid')`. `DEFAULT_TRUNK_METHOD = 'hybrid'` trỏ tới phương pháp AUTO iteration 03. Nó ưu tiên trace hai biên có đủ hỗ trợ, sau đó dùng band tracking và GrabCut giới hạn trong corridor khi cần. Unit test xác nhận đường gọi mặc định khớp `method='hybrid'` trên ảnh tổng hợp. `method='v2'` chạy hybrid làm prior rồi gọi `trunk_v2.refine(..., 10)`. Không có wiring từ UI hay extractor tới backend thân cây ở trạng thái hiện tại.

### AUTO, các kiểm tra trước AUTO và baseline iteration 03

- `trunk_candidates`, `trunk_scoring`, `trunk_localization`, `trunk_bands`, `trunk_refinement` là nguồn proposal, scoring, localization, theo dõi band và refinement. `inspect_trunk_candidates.py`, `inspect_trunk_localization.py`, `inspect_trunk_refinement.py`, `compare_trunk_quality.py` tạo bằng chứng dưới `p03_1/`, `p03_2_localization/`, `p03_2/`, `p03_2_quality_fix/`.
- AUTO dùng sáu polygon tham chiếu xấp xỉ. Bảng dưới dùng cùng tập calibration. `baseline` là comparator ban đầu của AUTO. `iteration_03` là hybrid đã freeze và trở thành comparator của V2.

| AUTO | Phương pháp | Usable/6 | Mean IoU | Quyết định trong bằng chứng |
| --- | --- | --- | --- | --- |
| Baseline | `baseline` | 1 | 0.265 | So sánh |
| 01 | `base_priority` | 3 | 0.405 | Giữ làm một bước trong hybrid |
| 02 | `bands` | 0 | 0.381 | Loại backend độc lập |
| 03 | `hybrid` | 4 | 0.621 | Freeze, 0 mask không usable được gắn reliable |
| 04 | `hybrid_structural` | 4 | 0.659 | Loại do recall của `101.jpg` tụt dưới ngưỡng |

Mục tiêu calibration 5/6 chưa đạt. Bộ độc lập 12 ảnh sau freeze có 3 usable, 5 partial, 4 failed theo review contact sheet của agent, dưới mục tiêu 9/12. Bằng chứng này dùng nhãn xấp xỉ và chưa có owner nghiệm thu. `best_configuration.json` và `iteration_03/config.json` ghi phương pháp và lệnh. ZIP AUTO có sáu tệp. `trunk.py` trong ZIP khác bản hiện tại, còn năm tệp kia trùng byte. Khôi phục AUTO với ZIP và commit gốc cùng helper từ checkpoint trong thư mục riêng. [Tóm tắt AUTO](../../outputs/trunk/p03_2_auto/final_summary.md) · [Lịch sử AUTO](../../outputs/trunk/p03_2_auto/experiment_history.csv) · [Cấu hình iteration 03](../../outputs/trunk/p03_2_auto/iteration_03/config.json)

### P03.2-V2

Nguồn ở `trunk_v2.py` cùng `trunk_ground`, `trunk_components`, `trunk_corridor`, `trunk_profile`, `trunk_termination`, `trunk_measurements`. Các bản thử dùng ground cue, connected component, profile/corridor, termination và provenance đo đạc. V2 có baseline và 10 iteration, mỗi iteration có config, metrics, nguồn snapshot và kết quả test. Cặp 01/02, 03/04, 05/06, 07/08 có cùng hash ZIP trong từng cặp, với version riêng trong config. A/B là 6/12 ảnh development. C là 24 ảnh đã đánh giá sau freeze.

| V2 | A usable/6 | B usable/12 | V2 | A usable/6 | B usable/12 |
| --- | --- | --- | --- | --- | --- |
| Hybrid baseline | 4 | 1 | 06 | 4 | 4 |
| 01 | 3 | 1 | 07 | 4 | 4 |
| 02 | 3 | 1 | 08 | 4 | 5 |
| 03 | 4 | 2 | 09 | 5 | 4 |
| 04 | 4 | 3 | 10 | 5 | 5 |
| 05 | 4 | 2 | | | |

Trên C, hybrid đạt 4/24 usable và 1 incorrect reliable. V2 iteration 10 đạt 2/24 và 2 incorrect reliable, dù mean IoU tăng từ 0.322 lên 0.334. Ngưỡng V2 cho usable là IoU ≥ 0.50, precision ≥ 0.70 và recall ≥ 0.60. Con số B của V2 dùng ngưỡng định lượng nên khác review định tính AUTO trên nhóm 12 ảnh. 13 tệp `trunk*.py` hiện tại và ZIP `final` đều khớp hash trong cấu hình freeze V2. Backend V2 giữ trạng thái **EXPERIMENTAL**. `prepare.py`, `oracle.py`, `evaluate.py`, `freeze.py`, `contract.py`, `regression.py` nằm trong thư mục ignored. [Freeze V2](../../outputs/trunk/p03_2_v2/final/best_configuration.json) · [Hybrid trên C](../../outputs/trunk/p03_2_v2/independent_validation/baseline/summary.json) · [V2 trên C](../../outputs/trunk/p03_2_v2/independent_validation/iteration_10/summary.json)

### P03-FINAL / nền supervised-learning V3

`annotations.py` đọc strip polygon legacy/canonical, kiểm tra và rasterize bool mask. `superpixels.py` tạo SLIC. `superpixel_labels.py` tính oracle, overlap và nhãn dương/âm/ambiguous. `region_features.py` tạo 96 cột handcrafted từ RGB và superpixel, phục vụ segmentation. `services/trunk_dataset.py` và `scripts/prepare_trunk_dataset.py` kiểm tra split, chạy bốn cấu hình SLIC, ghi schema và export dữ liệu train/val. Đây là bộ 96 cột theo vùng, tách khỏi vector CBIR X0–X37. Đã thấy code và dữ liệu chuẩn bị. Trong lịch sử, mã và artifacts kiểm tra được, chưa thấy trainer, classifier đã fit, model weights, inference V3 hay kết quả nghiệm thu supervised trên holdout.

`outputs/trunk/p03_final/01_dataset_features/` có inventory 54 annotation (6 A, 12 B, 24 C của V2 và 12 mới), quality review (32 accepted, 12 accepted new, 8 cần hiệu chỉnh, 2 unusable), `corrected_annotations.json`, `new_dev_annotations.json`, split manifest, SLIC/oracle tables và `feature_schema.json`. Split 507 ảnh gồm 38 train, 14 val, 24 test niêm phong, 2 loại và 429 unused. SLIC chọn cấu hình 3000 segments, compactness 10, sigma 0.8, mean oracle IoU khoảng 0.818 trên 52 ảnh dev. Oracle dùng reference để đo giới hạn của phân vùng. `train_features.npz` có `X` 99.694×96, `validation_features.npz` 36.633×96, đều hữu hạn. Nhãn, overlap, id và trọng số nằm ở mảng riêng. Tỷ lệ âm/dương lần lượt khoảng 39:1 và 53:1.

Đối chiếu tên và hash xác nhận holdout V3 tách khỏi A/B/C của V2 và khỏi kết quả independent AUTO. Trong 24 ảnh C cũ của V2, 22 ảnh nằm ở train của V3 và 2 bị loại. Vì vậy C của V2 giữ vai trò bằng chứng lịch sử, còn manifest V3 là holdout mới. Phiên kiểm toán chỉ đọc manifest, file hash và định dạng ảnh, không chạy inference holdout. [Tóm tắt split](../../outputs/trunk/p03_final/01_dataset_features/dataset_split_summary.json) · [Holdout V3](../../outputs/trunk/p03_final/01_dataset_features/frozen_independent_test_set.json) · [Schema 96 cột](../../outputs/trunk/p03_final/01_dataset_features/feature_schema.json)

## Giao diện mã hiện có

| Module | Giao diện và ranh giới |
| --- | --- |
| `config`, `models` | `FEATURE_IDS`, `FEATURE_DIMENSION`, slice 9/8/3/6/12, `RGBImage`, `BinaryMask`, `ImageMetadata`, `PreprocessedImage`, `SegmentationResult`, `FeatureExtractionResult`, `RetrievalResult` |
| `preprocessing` | `preprocess_image(source, image_id='query') -> PreprocessedImage`. Nhận path, bytes hoặc Pillow, tạo RGB `uint8` H×W×3. `PreprocessingError` báo lỗi input. |
| `utils` | `rgb_to_hsv`, `rgb_to_gray`, RGB↔BGR, `hsv_mask`, mask/composition/components, hình học/contour, morphology/skeleton, Canny/Hough và overlay. NumPy dùng `[y, x]`, mask H×W bool. |
| `segmentation.trunk` | `segment_trunk` trả `TrunkSegmentation(mask, bbox, base, upper, expected_height, confidence, diagnostics)`. `bbox` là `(x, y, w, h)`, base/upper là `(x, y)` hoặc `None`. Các status hiện ghi trong `diagnostics` và confidence chưa được hiệu chuẩn. |
| `segmentation.trunk_measurements` | `measurements(result) -> TrunkMeasurements` trả centerline, width, vùng dự kiến và trạng thái nguồn đo như `measured`, `estimated`, `unreliable`. |
| `features.trunk` | `extract_trunk_features(rgb, mask, expected_height) -> (values, valid, diagnostics)` với hai mảng 9 phần tử. X0 dựa vào tỉ lệ chiều cao, X1–X3 median HSV, X4–X8 là hình học/skeleton. |
| `segmentation.annotations`, `superpixels`, `region_features`, `superpixel_labels` | `TrunkAnnotation`, các loader/rasterizer, `SlicConfig`, `SuperpixelMap`, `generate_superpixels`, `RegionFeatureMatrix`, `extract_region_features`, `LabelPolicy`, `SuperpixelLabels`, `label_superpixels`, `compute_mask_metrics`, `compute_boundary_metrics`. Giao diện thí nghiệm. |
| `services.trunk_dataset` | `DatasetSplitRecord`, `load_curated_annotations`, `build_split_manifest`, `validate_split_disjointness`, `run_slic_experiments`, `export_split_features`. Export chỉ hỗ trợ train/val. |

## Kết quả kiểm tra hiện tại

| Kiểm tra | Kết quả |
| --- | --- |
| `./.venv/Scripts/python.exe --version` | PASS · CPython 3.14.3 |
| `./.venv/Scripts/python.exe -m pip check` | PASS · no broken requirements, khoảng 0.80 s |
| `./.venv/Scripts/python.exe -m pytest -v` tương đương `pytest.main(['-v', '--tb=line'])` | PASS · **44 passed, 0 skipped**, 17.34 s. PostgreSQL Compose `tree-cbir-postgres-1` healthy, pgvector test dùng bảng tạm. |
| `./.venv/Scripts/python.exe -m ruff check .` | PASS · khoảng 0.12 s |
| `./.venv/Scripts/python.exe -m ruff format --check .` | PASS · 104 tệp, khoảng 0.13 s |
| Ruff chạy trực tiếp trên 6 script V2 ignored | FAIL · 185 lỗi lint và cả 6 cần format. Git ignore giải thích vì sao hai lệnh mặc định qua. |
| `git diff --check HEAD` | PASS · khoảng 0.07 s sau khi cập nhật `status.md`. Tệp audit mới cũng qua kiểm tra whitespace riêng. |

Lần chạy pytest đầu tiên khi chưa dựng `DATABASE_URL` có 43 pass/1 skip. Lần chạy đầy đủ đọc `POSTGRES_*` từ `.env` bằng `dotenv_values`, dựng conninfo cục bộ bằng `psycopg.conninfo.make_conninfo` và đặt `DATABASE_URL` chỉ trong tiến trình test. [Pytest](../../outputs/evaluation/team_preparation_01/pytest.txt) · [Dependency versions](../../outputs/evaluation/team_preparation_01/dependency_versions.txt) · [Ruff mặc định](../../outputs/evaluation/team_preparation_01/ruff_check.txt) · [Ruff V2](../../outputs/evaluation/team_preparation_01/ruff_ignored_v2_check.txt) · [Diff check](../../outputs/evaluation/team_preparation_01/diff_check.txt)

## Tài liệu, mâu thuẫn và tệp dùng chung

| Hiện có | Mục đích và khoảng trống |
| --- | --- |
| `README.md`, `GUIDE.md`, `CONTRIBUTING.md`, `AGENTS.md`, `.agents/skills/`, `docs/instructions.md` | Điểm vào, quy trình cục bộ, quy tắc cho agent. `AGENTS.md` vẫn báo current phase P01. `GUIDE.md` mô tả P01, còn hướng dẫn test cần bổ sung cách dựng `DATABASE_URL` từ cấu hình Compose. Đã đọc cả 5 skill repository. |
| `docs/architecture.md`, `docs/adr/0001–0003` | Kiến trúc, stack và DB đã quyết định. Sơ đồ retrieval/ingestion thể hiện thiết kế đích. Chưa có các entry point end-to-end. |
| `docs/requirements.md`, `docs/feature_spec.md`, báo cáo môn học ở root | Yêu cầu 500 ảnh, Top-5, danh mục X0–X37 và tham chiếu công thức. Ghi chú “no local report” trong spec đã cũ. Bản báo cáo hiện untracked, có khác biệt cần đối chiếu trước khi chốt công thức/validity. |
| `docs/preprocessing.md`, `docs/database.md`, `docs/testing.md` | Contract RGB/mask, thiết kế DB dự kiến, yêu cầu kiểm thử. Cần recipe phục hồi dataset/fixtures và quy trình đánh giá độc lập. |
| `docs/status.md`, `docs/roadmap.md`, `CHANGELOG.md`, `docs/logs/P01–P03.md` | Trạng thái và nhật ký. P01/P02 có nghiệm thu. Log P03 ghi AUTO và 26 test cũ; hồ sơ 01/08 bổ sung V2/V3 và 44 test hiện tại. Các kết quả cũ vẫn là bằng chứng đúng thời điểm. |
| `outputs/environment/`, `outputs/preprocessing/`, `outputs/trunk/` | Evidence môi trường, data fix/review và thí nghiệm. Cần chỉ mục có provenance, phân biệt kết quả lịch sử với test hiện tại, và quy tắc đóng băng holdout. |

Các tệp có nguy cơ xung đột khi nhiều nhánh cùng làm là `config.py`, `models.py`, package exports, `extractor.py`, `services/`, `app.py`, `pyproject.toml`, requirements, `compose.yaml`, `sql/`, `.gitignore` và bộ tài liệu trạng thái/đặc tả. Cần quy trình duyệt thay đổi contract và thứ tự tích hợp trước khi bắt đầu công việc song song. Chưa có sơ đồ ranh giới edit, hướng dẫn phục hồi clean clone, dataset card/quyền sử dụng, quy tắc artifact/holdout, bảng tiêu chí acceptance theo pha hoặc chỉ mục tái lập thí nghiệm.

## Dữ liệu, tái lập và bảo vệ trước khi công bố

- Đã giải mã cả 507 ảnh chuẩn hóa thành công, tất cả là JPEG RGB 768×1024. Mỗi bộ nguồn/chuẩn hóa có 507 hash duy nhất. Tất cả 507 hash nguồn và 507 hash đầu ra khớp manifest P02 (470 copy nguyên byte, 15 resize, 22 crop/resize). Hash 507 ảnh V3 và 24 ảnh holdout khớp. Manifest P02 dùng tên tương đối với hai thư mục dữ liệu, V2/V3 dùng filename + hash. [Manifest P02](../../outputs/preprocessing/standardization/standardization_manifest.csv) · [Kiểm chứng hash](../../outputs/evaluation/team_preparation_01/manifest_hashes.txt)
- Clean clone hiện thiếu `data/processed/`, `data/standardized/`, V2 `references/A.json` và các fixture/split V3 mà `test_trunk_annotations_and_splits.py` đọc. Cần một cách nhận bộ dữ liệu nội bộ đúng hash và cung cấp fixture cần thiết. `scripts/standardize_dataset.py` từ chối tên đầu ra trùng, nên tái lập P02 trong workspace riêng có đích trống. Dùng hash P02 để kiểm chứng bản tái lập.
- AUTO có lệnh `./.venv/Scripts/python.exe scripts/experiment_trunk.py iteration_03 --method hybrid`. V2 có `./.venv/Scripts/python.exe outputs/trunk/p03_2_v2/evaluate.py 0 10`, và `--hold` tái chạy bộ C lịch sử khi được phép. V3 có `./.venv/Scripts/python.exe scripts/prepare_trunk_dataset.py`. Các script ghi vào thư mục evidence và có thể thay thế kết quả đã lưu. Chạy trong bản phục hồi riêng khi cần tái lập. V2 đọc pickle cache bằng tên ảnh và cache chứa prior/timing, nên chỉ dùng cache đáng tin cậy hoặc để workspace riêng tái tạo. Requirements hiện chưa pin đủ phiên bản.
- Giữ `.env`, thông tin kết nối và trạng thái PostgreSQL ở máy cục bộ. Chỉ chia sẻ `.env.example` sau khi xác nhận các giá trị là mẫu. `.env` không có trong tree hoặc lịch sử reachable. Quét theo mẫu các tệp văn bản hiện có không thấy dấu hiệu private key, token thông dụng hoặc URL PostgreSQL chứa user/password. Phạm vi kiểm tra này không thay một lượt rà soát nội dung đã staging và tài liệu/ZIP lồng trước khi công bố.
- Bảo vệ `data/processed/` (~174 MB), `data/standardized/` (~185 MB), ảnh/overlay/report, bộ nhãn và manifest holdout. Kiểm tra quyền phân phối ảnh, dữ liệu và báo cáo môn học (có ảnh nhúng). Các tệp untracked lớn nhất là `train_features.npz` (46.49 MB) và `validation_features.npz` (17.42 MB). Toàn bộ `outputs/trunk/` khoảng 176 MB, gồm V2 khoảng 63 MB. Blob reachable lớn nhất khoảng 2.30 MB. `.gitignore` hiện chặn toàn bộ V2 nhưng bỏ lọt NPZ và nhiều ZIP/ảnh ở các thư mục trunk khác. Chỉ stage theo danh sách cần công bố sau khi thống nhất kênh artifact.
- Các đường dẫn máy cá nhân xuất hiện trong `docs/logs/P01.md`, `outputs/trunk/p03_2_auto/pytest_results.txt`, `annotation_inventory.csv` và `annotation_quality_review.csv` của V3, cũng như log chạy pytest cục bộ của lượt kiểm toán. Giữ bản evidence gốc nội bộ và chuẩn hóa đường dẫn trong bản dùng để bàn giao/công bố. [Kiểm tra dữ liệu và đường dẫn](../../outputs/evaluation/team_preparation_01/data_and_publication_checks.txt)

## Vướng mắc và các bước chuẩn bị tiếp theo

1. Chốt bộ nguồn có thể đưa vào Git, chính sách artifact, bản sao nội bộ của checkpoint và dữ liệu, sau đó thử dựng lại một clean clone bằng đúng manifest. Sửa cách cung cấp fixture bị ignore trước khi dùng test suite làm gate cho nhóm.
2. Đồng bộ hướng dẫn agent và chỉ mục bằng chứng. Ghi rõ backend thân cây `hybrid`, version V2 có thể phục hồi, phạm vi chuẩn bị V3 và giới hạn của các chỉ số hiện có. Định phiên bản môi trường và cách chạy PostgreSQL integration tái lập.
3. Xác nhận công thức/đơn vị/validity X0–X37 với báo cáo. Ví dụ, báo cáo mô tả đếm điểm giao nhánh skeleton ở nửa dưới cho X8, còn code rút kết quả về 0/1 theo việc có điểm giao hay không. `extract_trunk_features` không nhận diagnostics segmentation nên `valid=True` có thể chỉ có nghĩa “tính được” cho mask uncertain. Chưa có bộ test công thức riêng đầy đủ.
4. Ghi tiêu chí nghiệm thu chất lượng thân cây và quyền truy cập holdout trước khi chọn baseline bàn giao. V2 đã thử trên C cũ, V3 hiện dừng ở chuẩn bị dữ liệu và chưa có bằng chứng chạy classifier. Ảnh rộng, thân rất ngắn và nền/tán phức tạp vẫn là các lỗi trên ảnh thật ghi trong AUTO.
5. Chuẩn bị bản đồ contract, tệp dùng chung, thứ tự merge và gate kiểm thử cho các bước 02–08. Các pha P04–P11 cần đặc tả đầu vào/đầu ra và dependency rõ ràng. P12 cần tiêu chí và bộ đánh giá retrieval end-to-end. Chưa phân công hoặc tạo nhánh nhóm trong 01/08.
