# Component Evaluation of Hybrid A2C–APF Guidance in Wind-Perturbed UAV Simulation

Kho lưu trữ công khai cho paper nộp **FAIR 2026** (IEEE conference template, 7/8 trang) cùng gói tái lập kết quả
và tài liệu giảng dạy hệ thống hóa toàn bộ kiến thức của paper.

Tác giả: **Hieu Ta Chi** (Thuyloi University) · **Huy Nguyen Anh** (Thuyloi University) · **Hoa Vu Minh** (Foreign Trade University)

## Có gì trong repo này

| Đường dẫn | Nội dung |
|---|---|
| `paper/latex/vnict_hybrid_main.tex` | Nguồn LaTeX canonical của paper (IEEEtran conference) |
| `paper/latex/references.bib` | 20 tài liệu tham khảo |
| `paper/pdf/Component-Evaluation-of-Hybrid-A2C-APF.pdf` | PDF đã build (7 trang) |
| `paper/latex/figures/` | 5 figure gốc của paper (PDF + PNG + SVG) |
| `reproducibility/` | Gói tái lập: ledger, phân tích 01→04, docs, reports, tests, Dockerfile, CITATION.cff |
| `reproducibility/tables/generated/` | 5 bảng số liệu sinh từ ledger — nguồn của mọi biểu đồ trong trang web |
| `site/index.html` | Trang HTML tự chứa (không phụ thuộc CDN) hệ thống hóa 16 phần / 32 công thức của paper |
| `site/assets/` | 9 biểu đồ (matplotlib) + 5 sơ đồ (SVG) + figure của paper |
| `site/tools/build_assets.py` | Script sinh lại toàn bộ biểu đồ và sơ đồ từ bảng số liệu |
| `teaching/canvas/` | Bản Canvas tương tác của cùng nội dung (mở trong Qoder IDE) |

## Tóm tắt khoa học

Paper đặt một câu hỏi hẹp và đo được: *một kênh dẫn hướng APF thêm được giá trị gì vào một implementation A2C cố
định?* Trên 4 map 300 m có gió tương quan, mỗi cấu hình học được huấn luyện 5 triệu bước × 5 training run độc lập
mỗi map, đánh giá 50 rollout tất định mỗi run (1000 rollout/cấu hình):

- **H0 Hybrid**: 1000/1000 hoàn thành (Wilson 95% CI 0.996–1.000)
- **H1 chỉ A2C** (khớp ngân sách và giao thức): 830/1000 (58 va chạm, 112 hết giờ)
- **H2 chỉ APF**: 55/1000 (905 va chạm)

Suy luận ghép cặp trên 20 đơn vị (map × training run): H1 kém hơn H0 về tỉ lệ hoàn thành
(d_z = −0.509, Wilcoxon p = 0.027) và có jitter/acceleration lấy mẫu cao hơn (d_z = 1.78, p < 0.001;
d_z = 1.07, p = 0.006). Khác biệt về efficiency, clearance và số bước **không** được dữ liệu ủng hộ.

Giới hạn chi phối: observation của A2C không chứa hình học vật cản, nên H0−H1 đo giá trị của cả kênh APF
**cùng với đầu vào hình học đặc quyền của nó**, không cô lập được phép tính trường thế năng.

## Đọc tài liệu giảng dạy

Mở `site/index.html` trong trình duyệt (hoạt động offline, không cần mạng). Trang gồm 16 phần, 32 công thức kèm
giải thích, 17 hình/biểu đồ/sơ đồ, 23 bảng, glossary 17 thuật ngữ và 18 câu hỏi ôn tập ba mức.

Sinh lại biểu đồ và sơ đồ sau khi chỉnh số liệu:

```bash
python site/tools/build_assets.py
```

## Tái lập các con số

Từ thư mục `reproducibility/`:

```bash
conda env create -f environment.yml && conda activate uav-a2c-apf-repro   # hoặc pip install -r requirements.txt
make smoke      # kiểm tra pipeline
make analysis   # tái sinh bảng + thống kê + đối soát 69 claim với paper (< 30 s, không GPU)
make figures    # sinh bảng/biểu đồ vào tables/generated và figures/generated
```

Trạng thái đối soát: **69/69 claim** (29 EXACT_MATCH, 40 ROUNDING_MATCH, 0 MISMATCH, 0 UNREPRODUCIBLE);
25/25 test PASS; quyết định release **CONDITIONAL PASS** (xem `reproducibility/reports/result_lock_certificate.md`).

## Trích dẫn

Xem `reproducibility/CITATION.cff`. Giấy phép: mã nguồn và script theo MIT (`reproducibility/LICENSE`);
văn bản paper và figure gốc thuộc về các tác giả.
