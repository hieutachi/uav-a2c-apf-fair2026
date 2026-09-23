import {
  BarChart,
  Callout,
  ChartContainer,
  Code,
  CollapsibleSection,
  Divider,
  DocsSection,
  Grid,
  H1,
  H3,
  MetricsGrid,
  Pill,
  ReferencePanel,
  ReportSection,
  ReportShell,
  Row,
  SendToChatButton,
  Stack,
  Table,
  Tag,
  Text,
  useHostTheme,
} from "qoder/canvas";
import type { MetricItem, ReferenceItem } from "qoder/canvas";

type AnyNode = any;

/* ------------------------------------------------------------------ */
/* Helper components                                                   */
/* ------------------------------------------------------------------ */

function Formula(props: { tag: string; title?: string; code: string; note?: AnyNode }) {
  const { tokens } = useHostTheme();
  return (
    <Stack gap="micro">
      <Row gap="inline" align="center" wrap>
        <Pill tone="info" size="sm">
          {props.tag}
        </Pill>
        {props.title ? (
          <Text weight="semibold" size="small">
            {props.title}
          </Text>
        ) : null}
      </Row>
      <div
        style={{
          background: tokens.fill.tertiary,
          border: `1px solid ${tokens.stroke.tertiary}`,
          borderRadius: tokens.radius.md,
          padding: "10px 12px",
          overflowX: "auto",
        }}
      >
        <pre
          style={{
            margin: 0,
            fontFamily: "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
            fontSize: 13,
            lineHeight: 1.85,
            color: tokens.text.primary,
            whiteSpace: "pre",
          }}
        >
          {props.code}
        </pre>
      </div>
      {props.note ? (
        <Text size="small" tone="secondary">
          {props.note}
        </Text>
      ) : null}
    </Stack>
  );
}

function Bullets(props: { items: AnyNode[]; size?: "small" | "body" }) {
  return (
    <Stack gap="micro">
      {props.items.map((item: AnyNode, i: number) => (
        <Row key={i} gap="inline" align="start">
          <Text size={props.size ?? "small"} tone="tertiary">
            {"•"}
          </Text>
          <Text size={props.size ?? "small"}>{item}</Text>
        </Row>
      ))}
    </Stack>
  );
}

function KeyIdea(props: { term: string; children: AnyNode }) {
  const { tokens } = useHostTheme();
  return (
    <div
      style={{
        borderLeft: `3px solid ${tokens.accent.control}`,
        background: tokens.bg.elevated,
        padding: "10px 14px",
        borderRadius: tokens.radius.sm,
      }}
    >
      <Stack gap="micro">
        <Text size="small" weight="semibold">
          {props.term}
        </Text>
        <Text size="small" tone="secondary">
          {props.children}
        </Text>
      </Stack>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/* Static data                                                         */
/* ------------------------------------------------------------------ */

const headlineMetrics: MetricItem[] = [
  { label: "H0 Hybrid (A2C + APF)", value: "1000/1000", description: "SR = 1.000 (CI 0.996–1.000)", tone: "success" },
  { label: "H1 Chỉ A2C", value: "830/1000", description: "58 va chạm · 112 hết giờ", tone: "warning" },
  { label: "H2 Chỉ APF", value: "55/1000", description: "905 va chạm · 40 hết giờ", tone: "danger" },
  { label: "Đơn vị suy luận", value: "20", unit: "cặp", description: "(map × training run) ghép cặp H0–H1", tone: "info" },
  { label: "Số liệu đối soát", value: "69/69", description: "0 MISMATCH · 0 UNREPRODUCIBLE", tone: "success" },
];

const tocRows: AnyNode[][] = [
  ["1", "Vấn đề & câu hỏi nghiên cứu", "Vì sao lai A2C + APF; paper tuyên bố và KHÔNG tuyên bố điều gì", "§I Introduction"],
  ["2", "Kiến thức nền & bảng ký hiệu", "RL, APF, động lực học, gió, AABB, thống kê — cần biết gì trước khi đọc", "§II Related Work"],
  ["3", "MDP: quan sát & hành động", "Observation 12 chiều; hành động là LỰC chuẩn hóa, không phải gia tốc", "§III-A"],
  ["4", "Động lực học point-mass", "Lực, drag tương đối, Euler bán ẩn, clamp độ cao, chân trời H = 1507", "§III-B, III-C"],
  ["5", "APF & blending thích ứng", "Lực hút, lực đẩy theo tâm AABB, chuẩn hóa rồi clip, λ theo khoảng cách", "§III-D"],
  ["6", "Hàm thưởng", "6 số hạng; vì sao phạt độ cao là code chết; hai quy ước khoảng cách", "§III-E"],
  ["7", "Mô hình gió AR(1)", "Nhiễu màu, hệ số √(1−φ²), ma trận tương quan, giới hạn Dryden-lite", "§III-F"],
  ["8", "A2C: nền thuật toán & huấn luyện", "Actor–critic, GAE, entropy; siêu tham số; 5M bước; seed không bitwise", "§III-G"],
  ["9", "Thiết kế thực nghiệm H0–H4", "Cấu trúc lồng nhau, 1000 rollout, 50 slot → 32 seed thật, ghép cặp", "§IV-A"],
  ["10", "Chỉ số đo & công thức thống kê", "Wilson, efficiency, clearance, jerk/accel, Wilcoxon, Cohen's d_z", "§IV-B"],
  ["11", "Kết quả", "3 bảng số liệu + 3 biểu đồ; mean vs median; H2 jitter thấp ≠ tốt", "§V"],
  ["12", "Diễn giải cơ chế", "Lịch λ, vì sao barrier = timeout còn corridor = collision, vì sao H2 chết", "§V-D, §VI"],
  ["13", "Threats to validity", "Internal / measurement / statistical / external", "§VII"],
  ["14", "Kết luận & hướng tương lai", "6 việc cần làm tiếp", "§VIII"],
  ["15", "Reproducibility & audit trail", "Ledger, SHA-256, traceability code↔paper, vì sao CONDITIONAL PASS", "gói reproducibility/"],
  ["16", "Thuật ngữ & câu hỏi ôn tập", "Glossary Anh–Việt; 18 câu hỏi theo 3 mức", "—"],
];

const prereqRows: AnyNode[][] = [
  [
    "MDP / RL cơ bản",
    "Trạng thái, hành động, phần thưởng, γ; policy π(a|s); mục tiêu tối đa E[Σ γᵗ rₜ]",
    "Nền của toàn bộ §III-A và §III-E",
  ],
  [
    "Policy gradient & actor–critic",
    "∇J ≈ E[∇log π(a|s)·A(s,a)]; critic V(s) dùng để giảm phương sai của advantage",
    "Vì sao chọn A2C; §III-G",
  ],
  [
    "GAE(γ, λ)",
    "Ưu thế ước lượng bằng tổng có chiết khấu của TD-error; λ = 0.95 cân bằng bias/variance",
    "Siêu tham số huấn luyện A2C",
  ],
  [
    "Artificial Potential Field (Khatib 1986)",
    "Trường hút kéo về đích + trường đẩy quanh vật cản; điểm yếu: local minima, dao động, nhạy gain",
    "§III-D và lý do H2 thất bại",
  ],
  [
    "Động lực học point-mass",
    "F = m·a; lực cản tỉ lệ vận tốc tương đối; tích phân Euler bán ẩn",
    "§III-B",
  ],
  [
    "Quá trình ngẫu nhiên AR(1)",
    "Nhiễu có màu (tương quan thời gian) thay vì nhiễu trắng; phương sai dừng",
    "§III-F mô hình gió",
  ],
  [
    "Hình học AABB & swept collision",
    "Hộp chữ nhật trục aligned; phép thử slab trên đoạn p_t → p_{t+1} để chống tunneling",
    "§III-C ngữ nghĩa va chạm",
  ],
  [
    "Nội suy cubic spline",
    "Đa thức bậc 3 từng khúc, liên tục C²; dùng để làm mượt quỹ đạo rời rạc",
    "H4 — chẩn đoán hậu xử lý",
  ],
  [
    "Thống kê suy luận",
    "Khoảng tin cậy Wilson; kiểm định Wilcoxon signed-rank ghép cặp; cỡ hiệu ứng Cohen's d_z; p-value khám phá & đa bội",
    "§IV-B và toàn bộ §V",
  ],
  [
    "Đơn vị suy luận & pseudoreplication",
    "Phân biệt rollout (mô tả) với (map × training run) (suy luận); lặp lại seed làm phồng n",
    "Điểm phương pháp luận quan trọng nhất của paper",
  ],
];

const notationRows: AnyNode[][] = [
  ["pₜ, vₜ ∈ ℝ³", "vị trí và vận tốc UAV tại bước t (m; m/s)"],
  ["g ∈ ℝ³", "vị trí đích (goal); g − pₜ là vector dịch chuyển tới đích"],
  ["wₜ ∈ ℝ³", "vận tốc gió tại bước t (m/s) — là vận tốc KHÔNG KHÍ, không phải lực"],
  ["sₜ ∈ ℝ¹²", "quan sát của A2C: [pₜ, vₜ, g − pₜ, wₜ]"],
  ["aₜᴬ²ᶜ ∈ [−1,1]³", "hành động policy: lệnh LỰC chuẩn hóa theo từng trục"],
  ["uₜ ∈ [−1,1]³", "lệnh chuẩn hóa sau khi trộn (hybrid) — đầu vào của động lực học"],
  ["λₜ ∈ [0.15, 0.55]", "trọng số trộn APF, phụ thuộc khoảng cách tới đích"],
  ["cᵢ ∈ ℝ³", "tâm của vật cản AABB thứ i"],
  ["dᵢ", "khoảng cách từ UAV tới TÂM vật cản i (khác với clearance bề mặt)"],
  ["δₜ", "clearance có dấu tới BỀ MẶT AABB gần nhất (dùng trong reward và metric)"],
  ["d₀ = 6 m", "bán kính ảnh hưởng của lực đẩy APF"],
  ["k_att = 0.04, k_rep = 18", "hệ số gain hút / đẩy của APF"],
  ["m = 0.5 kg, k_d = 0.12", "khối lượng và hệ số cản tuyến tính"],
  ["g₀ = 9.81 m/s², Δt = 0.1 s", "gia tốc trọng trường và bước tích phân"],
  ["F_max = 12 N", "giới hạn lực THEO TỪNG TRỤC (không phải theo chuẩn vector)"],
  ["H = 1507", "số transition tối đa của một episode (chân trời)"],
  ["nₜ", "số transition đã dùng tới thời điểm t"],
  ["φ = exp(−Δt/τ)", "hệ số suy giảm của quá trình AR(1) mô hình gió"],
  ["τ = 0.9 s", "hằng số thời gian tương quan của gió"],
  ["σ_gust = 1.2 m/s", "độ lệch chuẩn dừng của thành phần gió giật ngang"],
  ["γ = 0.99, λ_GAE = 0.95", "chiết khấu RL và tham số GAE"],
  ["E", "hiệu suất đường bay thành công ∈ (0, 1]"],
  ["d_z = Δ̄ / s_Δ", "cỡ hiệu ứng ghép cặp (Cohen's d_z)"],
  ["z = 1.96", "phân vị chuẩn cho khoảng tin cậy 95% (Wilson)"],
];

const designRows: AnyNode[][] = [
  [<Code key="h0">H0</Code>, "Hybrid: A2C + APF blend", "4 map / 20 unit", "5M bước × 20", "1000", "Có học", "Cấu hình chính được đề xuất"],
  [<Code key="h1">H1</Code>, "Chỉ A2C (tắt blend APF)", "4 map / 20 unit", "5M bước × 20", "1000", "Có học", "Đối chứng GHÉP CẶP; khớp ngân sách, map, realization đánh giá — nhưng KHÔNG khớp thông tin vật cản"],
  [<Code key="h2">H2</Code>, "Chỉ APF (không học)", "4 map / nhãn 5 seed", "0", "1000", "Không học", "5 nhãn seed chỉ là bookkeeping — không phải 5 bộ điều khiển độc lập"],
  [<Code key="h4">H4</Code>, "Chẩn đoán hậu xử lý spline", "dùng lại 1000 quỹ đạo H0", "0", "1000", "Không can thiệp", "Resample cùng lưới → gần như no-op; KHÔNG phải ablation làm mượt"],
];

const outcomeRows: AnyNode[][] = [
  [<b key="0">H0 Hybrid</b>, "1000", "1.000 (0.996–1.000)", "0", "0", "0.883 ± 0.075"],
  [<b key="1">H1 A2C-only</b>, "830", "0.830 (0.805–0.852)", "58", "112", "0.892 ± 0.099"],
  [<b key="2">H2 APF-only</b>, "55", "0.055 (0.042–0.071)", "905", "40", "0.882 ± 0.041"],
];

const continuousRows: AnyNode[][] = [
  ["H0 Hybrid", "7.24 ± 5.24", "104.4 ± 22.7", "99", "28.53 ± 9.03", "16.08 ± 1.67"],
  ["H1 A2C-only", "7.77 ± 6.28", "237.8 ± 451.3", "78", "55.33 ± 14.68", "22.85 ± 7.00"],
  ["H2 APF-only", "0.76 ± 3.70", "408.0 ± 339.0", "—", "2.21 ± 0.82", "0.45 ± 0.10"],
];

const pairedRows: AnyNode[][] = [
  ["Tỉ lệ thành công", "−0.17 (−17 điểm %)", "−0.509", "0.0273", "20", "Có bằng chứng: H1 kém tin cậy hơn"],
  ["Jitter (m/s³)", "+26.80", "1.78", "< 0.001", "20", "Có bằng chứng: H1 biến thiên mạnh hơn (cỡ hiệu ứng lớn)"],
  ["Acceleration (m/s²)", "+6.77", "1.07", "0.006", "20", "Có bằng chứng: H1 gia tốc lấy mẫu lớn hơn"],
  ["Efficiency (chỉ episode thành công)", "+0.0142", "0.156", "0.417", "18", "KHÔNG được ủng hộ"],
  ["Clearance nhỏ nhất (m)", "+0.533", "0.063", "0.956", "20", "KHÔNG được ủng hộ"],
  ["Số bước (steps)", "+133.37", "0.300", "0.123", "20", "KHÔNG được ủng hộ (SD 451.3 do trộn timeout dài)"],
];

const failureRows: AnyNode[][] = [
  ["Random", "140", "48", "62", "Cả hai cơ chế: vừa đâm vừa quẩn"],
  ["Corridor", "240", "10", "0", "Ràng buộc ngang lặp lại → dao động/kém giảm chấn → va chạm"],
  ["Barrier", "200", "0", "50", "Có khe hở hình học → không đủ tiến bộ về đích → hết giờ"],
  ["Mixed", "250", "0", "0", "APF không cần thiết cho layout này"],
];

const h2Rows: AnyNode[][] = [
  ["Random", "50", "190", "10 *"],
  ["Corridor", "0", "250", "0 *"],
  ["Barrier", "5", "225", "20 *"],
  ["Mixed", "0", "240", "10 *"],
];

const threatRows: AnyNode[][] = [
  [
    "Internal — quy kết nguyên nhân",
    "H0 nhận hình học vật cản qua APF, observation của A2C thì không → H0−H1 đo cả kênh APF LẪN đầu vào thông tin đặc quyền",
    "Không kết luận 'APF tính toán tốt hơn'; cần H1b có obstacle feature tương xứng",
  ],
  [
    "Internal — cơ chế",
    "Không log tách lệnh aᴬ²ᶜ và aᴬᴾᶜ nên không chứng minh được vì sao jitter giảm",
    "Giải thích theo lịch λ chỉ là giả thuyết chẩn đoán",
  ],
  [
    "Measurement — độ đo",
    "Accel/jerk là sai phân hữu hạn của vị trí lấy mẫu, không phải tải khí động, công suất motor, độ mượt tư thế hay comfort",
    "Không suy ra 'bay được thật' (flyability)",
  ],
  [
    "Measurement — khoảng cách",
    "APF dùng khoảng cách tới TÂM AABB; reward và clearance dùng khoảng cách BỀ MẶT có dấu",
    "Hai đại lượng khác nhau, không hoán đổi; APF under-repel với khối rộng",
  ],
  [
    "Measurement — code chết",
    "Độ cao bị clamp về [5, 6] trước khi tính reward → số hạng phạt r_z không bao giờ kích hoạt",
    "Khai báo rõ thay vì âm thầm bỏ",
  ],
  [
    "Statistical — n",
    "n = 20 cặp (18 với efficiency); 6 kiểm định không hiệu chỉnh đa bội",
    "p-value là khám phá; nhấn mạnh p chính xác + cỡ hiệu ứng, không dán nhãn significant",
  ],
  [
    "Statistical — pseudoreplication",
    "50 slot đánh giá/unit chỉ có 32 numerical seed phân biệt → 18 slot lặp y hệt (1080 instance trùng đã kiểm chứng)",
    "Tỉ lệ vẫn báo cáo trên 50 slot; rollout KHÔNG được coi là đơn vị độc lập",
  ],
  [
    "Statistical — survivorship",
    "Efficiency và clearance chỉ tính trên episode thành công → loại bỏ 170 failure của H1",
    "Không so sánh 'đường bay đẹp hơn' giữa H0 và tập con được chọn lọc của H1",
  ],
  [
    "Reproducibility",
    "PyTorch không được seed tường minh, không có cờ determinism → huấn luyện lại không bitwise",
    "Tái lập từ ledger là chính xác; retrain chỉ 'so sánh được về phân phối'",
  ],
  [
    "External",
    "4 map AABB 300 m cố định, một quá trình gió duy nhất, không có điều kiện no-wind hay mức gió khác, không held-out map",
    "Không kết luận robustness theo gió; không tổng quát hóa layout",
  ],
  [
    "External — mô hình",
    "Point-mass, không tư thế/rotor/tốc độ cơ cấu chấp hành; dải độ cao chỉ 1 m; trạng thái quan sát sạch (không nhiễu cảm biến/ước lượng)",
    "Lệnh lực có thể đổi nhanh hơn nhiều so với multirotor thật",
  ],
  [
    "Scope",
    "Chỉ có bằng chứng cho H0/H1 (A2C) và H2 (không học); H3 (no-wind), H5 (strong-wind), map-random-02 đã định nghĩa nhưng loại khỏi tập bằng chứng",
    "Không xếp hạng với PPO, SAC, RRT",
  ],
];

const glossaryRows: AnyNode[][] = [
  ["Advantage Actor–Critic (A2C)", "A2C", "Biến thể actor–critic đồng bộ của A3C: dùng advantage Â = Q − V để giảm phương sai gradient chính sách"],
  ["Artificial Potential Field", "APF / trường thế năng nhân tạo", "Điều khiển phản xạ: lực hút về đích + lực đẩy quanh vật cản, tính online, chi phí thấp"],
  ["Axis-Aligned Bounding Box", "AABB", "Hộp bao chữ nhật có các cạnh song song trục tọa độ — biểu diễn vật cản trong mô phỏng"],
  ["Component evaluation", "Đánh giá theo thành phần", "Đo đóng góp của MỘT thành phần trong một implementation cố định, thay vì đề xuất hệ thống mới"],
  ["Deterministic rollout", "Lượt chạy tất định", "Đánh giá dùng model.predict(deterministic=True) — lấy mode của phân phối thay vì lấy mẫu"],
  ["Finite difference", "Sai phân hữu hạn", "Xấp xỉ đạo hàm bằng hiệu các mẫu liền kề: Δp/Δt, Δ²p/Δt², Δ³p/Δt³"],
  ["Information asymmetry", "Bất đối xứng thông tin", "Hai cấu hình so sánh không nhận cùng một đầu vào (ở đây: hình học vật cản)"],
  ["Jitter", "Chỉ số biến thiên bậc 3", "mean‖Δ³p/Δt³‖ (m/s³) — độ 'gằn' của quỹ đạo lấy mẫu"],
  ["Matched pair", "Cặp ghép", "Hai đơn vị chia sẻ map, ngân sách huấn luyện và realization đánh giá → so sánh ghép cặp"],
  ["Pseudoreplication", "Lặp giả", "Đếm nhiều lần quan sát không độc lập như thể chúng độc lập, làm phồng n và thu nhỏ p"],
  ["Slab test", "Phép thử lát cắt", "Giao đoạn thẳng với AABB bằng cách cắt 3 dải trục — phát hiện va chạm kể cả khi bước nhảy dài"],
  ["Stationary variance", "Phương sai dừng", "Phương sai không đổi theo thời gian của quá trình AR(1) khi hệ số nhiễu được chuẩn đúng"],
  ["Success rate (SR)", "Tỉ lệ hoàn thành", "Số episode về đích (cách đích < 3 m và không va chạm) / tổng số episode"],
  ["Swept collision", "Va chạm quét", "Kiểm tra cả đoạn p_t → p_{t+1} thay vì chỉ điểm cuối, chống hiện tượng 'xuyên hầm' vật cản"],
  ["Wilson score interval", "Khoảng tin cậy Wilson", "Khoảng tin cậy cho tỉ lệ nhị phân, bền khi p gần 0/1 hoặc n nhỏ — dùng làm mô tả, không dùng để suy luận"],
  ["Wilcoxon signed-rank", "Kiểm định hạng có dấu", "Kiểm định phi tham số cho hiệu ghép cặp, không giả định phân phối chuẩn"],
  ["Cohen's d_z", "Cỡ hiệu ứng ghép cặp", "Δ̄/s_Δ: hiệu trung bình chia cho độ lệch chuẩn của hiệu — cho biết độ LỚN, không chỉ độ hiếm"],
];

const refs: ReferenceItem[] = [
  { id: "khatib", label: "Khatib (1986) — Real-Time Obstacle Avoidance for Manipulators and Mobile Robots", description: "Nguồn gốc của APF: trường hút/đẩy, và các điểm yếu kinh điển (local minima, dao động, nhạy gain).", kind: "paper", meta: "IJRR 5(1):90–98", href: "https://doi.org/10.1177/027836498600500106" },
  { id: "mnih", label: "Mnih và cs. (2016) — Asynchronous Methods for Deep RL (A3C)", description: "Nền của họ advantage actor–critic mà A2C là biến thể đồng bộ.", kind: "paper", meta: "ICML 2016, 1928–1937" },
  { id: "henderson", label: "Henderson và cs. (2018) — Deep Reinforcement Learning That Matters", description: "Lý do paper nhấn mạnh implementation alignment: kết quả deep-RL thay đổi mạnh theo chi tiết cài đặt.", kind: "paper", meta: "AAAI 32(1)", href: "https://doi.org/10.1609/aaai.v32i1.11694" },
  { id: "wilson", label: "Wilson (1927) — Probable Inference, the Law of Succession", description: "Khoảng tin cậy Wilson dùng cho success/collision rate.", kind: "paper", meta: "JASA 22(158):209–212", href: "https://doi.org/10.1080/01621459.1927.10502953" },
  { id: "lavalle", label: "LaValle (1998) — Rapidly-Exploring Random Trees", description: "Họ quy hoạch lấy mẫu; paper dùng làm mốc đối chiếu về cấu trúc thông tin khác nhau.", kind: "paper", meta: "Iowa State Univ. TR" },
  { id: "karaman", label: "Karaman & Frazzoli (2011) — Sampling-Based Algorithms for Optimal Motion Planning", description: "RRT* và hội tụ tiệm cận tối ưu.", kind: "paper", meta: "IJRR 30(7):846–894", href: "https://doi.org/10.1109/9.676161" },
  { id: "ppo", label: "Schulman và cs. (2017) — Proximal Policy Optimization", description: "Đối chiếu thuật toán: paper nói rõ KHÔNG xếp hạng với PPO.", kind: "paper", meta: "arXiv:1707.06347", href: "https://doi.org/10.48550/arXiv.1707.06347" },
  { id: "sac", label: "Haarnoja và cs. (2018) — Soft Actor-Critic", description: "Đối chiếu thuật toán off-policy maximum entropy.", kind: "paper", meta: "ICML 2018, 1861–1870" },
  { id: "ddpg", label: "Lillicrap và cs. (2016) — Continuous Control with Deep RL (DDPG)", description: "Đối chiếu điều khiển liên tục replay-based.", kind: "paper", meta: "ICLR 2016" },
  { id: "jin", label: "Jin và cs. (2025) — Hybrid RL với APF cho UAV target search", description: "Bằng chứng rằng ghép APF với RL đã phổ biến → paper định vị lại thành đánh giá thành phần.", kind: "paper", meta: "Sensors 25(9):2796", href: "https://doi.org/10.3390/s25092796" },
  { id: "xiao", label: "Xiao và cs. (2025) — RL-based Vortex APF chống local minima", description: "Cách tiếp cận vortex field cho drone.", kind: "paper", meta: "Machines 13(7):600", href: "https://doi.org/10.3390/machines13070600" },
  { id: "lee", label: "Lee và cs. (2025) — APF-enhanced PPO cho multi-UAV", description: "Ví dụ APF đi vào planner học được ở mức đa UAV.", kind: "paper", meta: "AIAA SciTech 2025", href: "https://doi.org/10.2514/6.2025-1613" },
  { id: "wu", label: "Ma và cs. (2024) — DRL wind disturbance rejection cho UAV", description: "Dòng nghiên cứu điều khiển bền vững với gió.", kind: "paper", meta: "Drones 8(11):632", href: "https://doi.org/10.3390/drones8110632" },
  { id: "neuralfly", label: "O'Connell và cs. (2022) — Neural-Fly", description: "Học nhanh để bay linh hoạt trong gió mạnh — mốc tham chiếu về gió thật.", kind: "paper", meta: "Science Robotics 7(66)", href: "https://doi.org/10.1126/scirobotics.abm6597" },
  { id: "datt", label: "Shi và cs. (2021) — Disturbance-Aware Trajectory Tracking", description: "Bám quỹ đạo có xét nhiễu cho quadrotor.", kind: "paper", meta: "IEEE RA-L 6(2):2739–2746", href: "https://doi.org/10.1109/LRA.2021.3061303" },
  { id: "mellinger", label: "Mellinger & Kumar (2011) — Minimum Snap Trajectory Generation", description: "Chuẩn tham chiếu về 'độ mượt' thực sự (snap) cho quadrotor — khác với jerk sai phân của paper.", kind: "paper", meta: "ICRA 2011, 2520–2525", href: "https://doi.org/10.1109/ICRA.2011.5980409" },
  { id: "zheng", label: "Zheng và cs. (2025) — UAV Path Planning in Complex Urban Environments: Review", description: "Tổng quan đánh đổi tìm kiếm toàn cục / phản xạ online / chi phí tính toán.", kind: "paper", meta: "Sensors 25(13):4142", href: "https://doi.org/10.3390/s25134142" },
  { id: "gapf", label: "Li và cs. (2024) — G-APF: RRT-Guided APF cho UAV", description: "Planner lai RRT + APF.", kind: "paper", meta: "Drones, 2024" },
  { id: "dulac", label: "Dulac-Arnold và cs. (2021) — Challenges of Real-World RL", description: "Khoảng cách mô phỏng → thực tế; vì sao paper không tuyên bố bay thật.", kind: "paper", meta: "Machine Learning 110:2419–2468", href: "https://doi.org/10.1007/s10994-021-05961-4" },
  { id: "tobin", label: "Tobin và cs. (2017) — Domain Randomization", description: "Kỹ thuật chuyển giao sim-to-real.", kind: "paper", meta: "IROS 2017, 23–30", href: "https://doi.org/10.1109/IROS.2017.8202133" },
];

const repoRefs: ReferenceItem[] = [
  { id: "tex", label: "latex/vnict_hybrid_main.tex", description: "Nguồn LaTeX canonical của paper (IEEEtran conference, 300 dòng).", kind: "file", source: "FAIR2026/ReviewPackage/Paper_Final/", meta: "bản duy nhất nên sửa" },
  { id: "pdf", label: "Component Evaluation of Hybrid A2C–APF.pdf", description: "PDF đã build, 7 trang (giới hạn 8 trang), metadata Title khớp tiêu đề.", kind: "file", source: "FAIR2026/ReviewPackage/Paper_Final/latex/", meta: "7 trang" },
  { id: "manifest", label: "rigorous_manifest.json", description: "Giao thức đông cứng: H0–H5, tham số APF/lực/gió/động lực học/độ đo.", kind: "doc", source: "experiments/", meta: "protocol vnict-rigorous-2026" },
  { id: "ledger", label: "episode_audit.csv + aggregate.json", description: "Sổ cái kết quả canonical (904 KB): mỗi rollout một dòng, đúng một trạng thái kết thúc.", kind: "dataset", source: "results/rigorous/canonical/", meta: "nguồn của mọi con số" },
  { id: "repro", label: "reproducibility/ (README, CITATION.cff, Dockerfile, Makefile)", description: "Gói tái lập: ledger + SHA-256, analysis 01→04, 25 test, đối soát 69 claim.", kind: "runbook", source: "reproducibility/", meta: "make smoke · make analysis · make figures" },
  { id: "trace", label: "implementation_traceability.md", description: "Bảng 21 tuyên bố trong paper ↔ bằng chứng code (dòng/hàm cụ thể).", kind: "doc", source: "reproducibility/docs/", meta: "21/21 CONFIRMED" },
  { id: "seeds", label: "seed_provenance.md", description: "Truy vết mọi nguồn ngẫu nhiên; giải thích 50 slot → 32 seed và 1080 instance trùng.", kind: "doc", source: "reproducibility/docs/", meta: "PyTorch KHÔNG seed" },
  { id: "limits", label: "limitations.md", description: "Danh sách giới hạn đầy đủ hơn cả mục Threats trong paper.", kind: "doc", source: "reproducibility/docs/", meta: "6 nhóm" },
  { id: "code", label: "a2c_new.py · vnict_hybrid_experiments.py", description: "Vật lý/APF/va chạm/reward nằm ở a2c_new.py; env đánh giá VNICTDroneEnv kế thừa DroneEnv3D, không đổi vật lý.", kind: "file", source: "scripts/", meta: "nguồn implementation" },
];

const exercises: AnyNode[] = [
  ["Mức 1 — Hiểu", "Observation của A2C gồm những khối 3 chiều nào? Vì sao dùng (g − pₜ) thay vì g?"],
  ["Mức 1 — Hiểu", "Hành động của policy là gia tốc hay lực? Giới hạn 12 N áp dụng theo trục hay theo chuẩn vector?"],
  ["Mức 1 — Hiểu", "Viết lại công thức tính gia tốc và giải thích vì sao gió xuất hiện trong số hạng drag chứ không phải cộng thẳng vào vị trí."],
  ["Mức 1 — Hiểu", "Tính H cho map 300 m và cho biết một episode kéo dài bao nhiêu giây mô phỏng khi dùng hết chân trời."],
  ["Mức 1 — Hiểu", "λₜ bằng bao nhiêu khi UAV cách đích 335.4 m, 255 m, 180 m và 135 m? Ý nghĩa điều khiển của lịch này?"],
  ["Mức 2 — Vận dụng", "Một khối AABB cạnh 20 m có tâm cách UAV 12 m. Tính lực đẩy APF và giải thích vì sao kết quả này nguy hiểm."],
  ["Mức 2 — Vận dụng", "Chứng minh rằng với hệ số 1.2·√(1−φ²) thì phương sai dừng của quá trình gió giật bằng 1.2²."],
  ["Mức 2 — Vận dụng", "Vì sao số hạng phạt độ cao r_z không bao giờ kích hoạt? Muốn nó hoạt động thì phải đổi gì trong thứ tự tính toán?"],
  ["Mức 2 — Vận dụng", "Vì sao efficiency chỉ có 18 cặp ghép thay vì 20? Điều này tạo ra thiên lệch gì?"],
  ["Mức 2 — Vận dụng", "Jitter của H2 (2.21 m/s³) thấp hơn H0 (28.53 m/s³). Vì sao KHÔNG được kết luận H2 bay mượt hơn?"],
  ["Mức 2 — Vận dụng", "Mean steps của H1 là 237.8 còn median là 78. Giải thích khoảng cách này bằng cấu trúc kết quả."],
  ["Mức 3 — Phản biện", "H0 thắng H1 có chứng minh được 'APF tốt hơn học thuần túy' không? Chỉ ra đúng một thí nghiệm bổ sung sẽ trả lời được câu hỏi đó."],
  ["Mức 3 — Phản biện", "Vì sao paper không hiệu chỉnh đa bội cho 6 kiểm định? Lập luận bảo vệ và lập luận phản đối cách làm này."],
  ["Mức 3 — Phản biện", "Tiêu đề có 'Wind-Perturbed' nhưng không có điều kiện no-wind. Nếu bạn là reviewer, bạn sẽ yêu cầu gì?"],
  ["Mức 3 — Phản biện", "H2 thua thảm hại (905/1000 va chạm). Điều này nói lên giới hạn của APF hay giới hạn của CÀI ĐẶT APF? Phân biệt hai khả năng."],
  ["Mức 3 — Phản biện", "50 slot đánh giá chỉ có 32 seed phân biệt. Nếu sửa giao thức, bạn chọn 5 base seed cách nhau bao nhiêu để loại trùng lặp mà vẫn giữ 50 slot?"],
  ["Mức 3 — Phản biện", "Vì sao H4 (spline) được giữ lại trong paper dù nó gần như không tạo bằng chứng? Giá trị khoa học của việc công bố một kết quả 'no-op' là gì?"],
  ["Mức 3 — Phản biện", "Xếp 4 cấu hình H0, H1, H2 và một PPO giả định theo độ tin cậy của bằng chứng hiện có. Giải thích vì sao PPO không được xếp hạng."],
];

const lessonRows: AnyNode[][] = [
  ["Nên học theo", "Khai báo bất đối xứng thông tin ngay trong abstract", "Biến điểm yếu thành phạm vi diễn giải rõ ràng → reviewer khó bắt bẻ quá mức"],
  ["Nên học theo", "Báo cáo cả kết quả KHÔNG có ý nghĩa (efficiency, clearance, steps)", "Chống lại thiên lệch công bố; tăng độ tin cậy của các kết quả có ý nghĩa"],
  ["Nên học theo", "Chọn đúng đơn vị suy luận (20 cặp) thay vì 1000 rollout", "Tránh pseudoreplication — lỗi phổ biến nhất trong paper RL ứng dụng"],
  ["Nên học theo", "Accounting đầy đủ: mỗi episode đúng một trạng thái, collision ưu tiên trước success", "Không có rollout nào 'mất tích' khỏi mẫu số"],
  ["Nên học theo", "Tách bạch mô tả (Wilson CI) và suy luận (Wilcoxon ghép cặp)", "Khoảng tin cậy không bị hiểu nhầm thành kiểm định"],
  ["Nên học theo", "Công bố số hiệu ứng d_z kèm p", "Người đọc đánh giá được độ lớn, không chỉ độ hiếm"],
  ["Nên học theo", "Đối soát từng con số trong paper với ledger (69 claim)", "Chuẩn FAIR: mọi số đều tái sinh được, không copy"],
  ["Nên học theo", "Tự chỉ ra code chết (r_z) và no-op (H4)", "Trung thực implementation-level — đúng tinh thần Henderson 2018"],
  ["Nên tránh", "Để tài liệu trạng thái cũ mâu thuẫn với kết quả mới (README 'results pending')", "Người đọc/reviewer vào repo sẽ mất niềm tin trước khi đọc paper"],
  ["Nên tránh", "APF dùng khoảng cách tới tâm nhưng mô tả như thể là clearance bề mặt", "Hai đại lượng khác nhau; nhầm lẫn này làm sai lệch diễn giải H2"],
  ["Nên tránh", "Không seed tường minh PyTorch", "Mất khả năng tái lập bitwise khi huấn luyện lại"],
  ["Nên tránh", "Thiết kế slot seed chồng lấn (50 → 32 seed thật)", "Phồng mẫu số, phải khai báo pseudoreplication"],
  ["Nên tránh", "Giữ nhiều bản build/tiêu đề phân kỳ trong cùng một cây thư mục", "Rủi ro nộp nhầm bản đã supersede"],
  ["Nên tránh", "Nói 'quỹ đạo mượt hơn' mà chỉ đo sai phân vị trí", "Cần command trace hoặc mô hình chấp hành để nói về độ mượt thực sự"],
];

/* ------------------------------------------------------------------ */
/* Canvas                                                              */
/* ------------------------------------------------------------------ */

export default function A2cApfPaperKnowledge() {
  return (
    <ReportShell width="wide" ariaLabel="Hệ thống hóa kiến thức paper A2C–APF (FAIR 2026)">
      <Stack gap="sectionCompact">
        <header>
          <Stack gap="component">
            <Row gap="inline" align="center" wrap>
              <Tag tone="success">Đã nộp FAIR 2026</Tag>
              <Tag tone="info">IEEE conference · 7/8 trang</Tag>
              <Tag tone="neutral">Tài liệu học tập cho sinh viên</Tag>
            </Row>
            <H1>Component Evaluation of Hybrid A2C–APF Guidance in Wind-Perturbed UAV Simulation</H1>
            <Text tone="secondary">
              Hệ thống hóa toàn bộ kiến thức của paper từ đầu đến cuối: mô hình toán, từng công thức kèm giải thích,
              giao thức thực nghiệm, kết quả, diễn giải, giới hạn và bài học phương pháp luận.
              Nguồn: <Code>FAIR2026/ReviewPackage/Paper_Final/latex/vnict_hybrid_main.tex</Code> (bản canonical)
              và gói <Code>reproducibility/</Code>.
            </Text>
            <Text size="small" tone="tertiary">
              Tác giả: Hieu Ta Chi (Thuyloi University) · Huy Nguyen Anh (Thuyloi University) · Hoa Vu Minh (Foreign Trade University)
            </Text>
            <MetricsGrid variant="header" columns={5} items={headlineMetrics} />
          </Stack>
        </header>

        <ReportSection
          title="Cách đọc tài liệu này"
          description="16 phần, đi đúng theo trình tự của paper. Mỗi công thức có mã CT-n, kèm giải thích bằng lời, đơn vị và cạm bẫy diễn giải."
          divided
        >
          <Stack gap="container">
            <Callout tone="info" title="Quy ước trình bày công thức">
              <Text size="small">
                Công thức được viết bằng ký hiệu Unicode trong khung monospace (Canvas không nhúng LaTeX). Đối chiếu
                1-1 với bản PDF: ví dụ CT-8 là Equation (6) của paper. Những công thức thuộc kiến thức nền mà paper
                không in ra (policy gradient, GAE, Wilson) được đánh dấu rõ là "nền — ngoài paper" để sinh viên không
                nhầm là đóng góp của bài.
              </Text>
            </Callout>
            <Table
              headers={["#", "Phần", "Nội dung chính", "Mục trong paper"]}
              rows={tocRows}
              density="compact"
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 1 ---------------- */}
        <ReportSection
          title="1. Vấn đề nghiên cứu và câu hỏi được kiểm soát"
          description="Paper không đề xuất thuật toán mới. Nó trả lời một câu hỏi hẹp, đo được, trên một implementation cố định."
          meta="§I Introduction · §II Related Work"
          divided
        >
          <Stack gap="container">
            <DocsSection title="Ba yêu cầu đồng thời của bay thấp trong môi trường chật">
              <Bullets
                size="body"
                items={[
                  <span key="a"><b>Tiến bộ liên tục về đích</b> — cần một chính sách có mục tiêu dài hạn.</span>,
                  <span key="b"><b>Tránh va chạm</b> — cần phản xạ cục bộ với hình học vật cản.</span>,
                  <span key="c"><b>Điều khiển không biến đổi đột ngột dưới nhiễu</b> — cần lệnh mượt khi có gió.</span>,
                ]}
              />
            </DocsSection>

            <Table
              headers={["Họ phương pháp", "Điểm mạnh", "Điểm yếu — theo paper", "Hệ quả cho thiết kế nghiên cứu"]}
              rows={[
                ["Planner lấy mẫu (RRT, RRT*)", "Quy hoạch tốt khi biết map; có bảo đảm tiệm cận tối ưu", "Cấu trúc thông tin khác: cần map biết trước, cần replanning; không phải bộ điều khiển phản xạ vòng kín", "Chỉ dùng làm mốc tham chiếu, không so sánh trực tiếp"],
                ["APF (Khatib 1986)", "Rẻ, tính online, phản xạ tức thời", "Local minima, dao động, nhạy gain", "Dùng làm 'guidance prior', không dùng làm planner hoàn chỉnh"],
                ["RL (A2C, PPO, SAC)", "Học ánh xạ state → action qua tương tác; thích ứng với nhiễu", "Kết quả phụ thuộc seed, reward, observation, termination; khó quy kết nguyên nhân", "Chọn A2C vì ÍT thành phần nhất → dễ quy kết đóng góp của thành phần khác"],
                ["APF + RL (2024–2025)", "Đã có nhiều công trình ghép: shaping reward, ràng buộc action, blend trực tiếp", "Việc ghép tự nó không còn mới", "Paper chuyển trọng tâm sang ĐÁNH GIÁ THÀNH PHẦN thay vì đề xuất kiến trúc"],
              ]}
              density="compact"
            />

            <Callout tone="success" title="Câu hỏi nghiên cứu (đúng nguyên văn tinh thần của paper)">
              <Text>
                <i>"Một kênh dẫn hướng APF thêm được giá trị đo lường nào vào một implementation A2C dẫn đường cố định?"</i>
              </Text>
            </Callout>

            <Grid columns={3} gap="container" minColumnWidth={220}>
              <KeyIdea term="Đóng góp 1 — Bộ điều khiển được đặc tả đầy đủ">
                Controller A2C–APF với observation 12 chiều, ngữ nghĩa lực chuẩn hóa, động lực học point-mass,
                gió tương quan và blending thích ứng theo khoảng cách.
              </KeyIdea>
              <KeyIdea term="Đóng góp 2 — Chiến dịch 4 map tách bạch thành phần">
                H0 hybrid, H1 chỉ A2C (khớp ngân sách và giao thức), H2 chỉ APF, H4 chẩn đoán nội suy cùng lưới.
              </KeyIdea>
              <KeyIdea term="Đóng góp 3 — Phân tích ghép cặp ở cấp training run">
                Suy luận trên 20 đơn vị (map × training run) và accounting đầy đủ kết thúc episode, thay vì
                coi 1000 rollout là độc lập.
              </KeyIdea>
            </Grid>

            <Callout tone="warning" title="Ba điều paper chủ động KHÔNG tuyên bố (đây là điểm mạnh, không phải điểm yếu)">
              <Bullets
                items={[
                  "Không đề xuất thuật toán RL mới và không đề xuất khung quy hoạch đường tổng quát.",
                  "Không xếp hạng với PPO, SAC hay RRT — vì chưa có tuning riêng, ngân sách ngang nhau và nhiều seed cho từng thuật toán.",
                  "Không tuyên bố đường bay ngắn hơn, an toàn hơn (clearance) hay nhanh hơn — các khác biệt đó KHÔNG được dữ liệu ủng hộ.",
                ]}
              />
            </Callout>

            <Callout tone="danger" title="Giới hạn chi phối toàn bộ cách diễn giải: bất đối xứng thông tin">
              <Text size="small">
                Observation của A2C chỉ có [vị trí, vận tốc, dịch chuyển tới đích, gió] — <b>không có hình học vật cản</b>.
                H0 nhận hình học vật cản thông qua kênh APF; H1 không nhận gì cả. Vậy nên so sánh H0−H1 đo giá trị của
                <b> cả kênh APF cùng với đầu vào hình học đặc quyền của nó</b>, chứ không cô lập được "phép tính trường
                thế năng". Muốn cô lập, phải cho H1 một đặc trưng vật cản tương đương mà không có blend APF.
              </Text>
            </Callout>
          </Stack>
        </ReportSection>

        {/* ---------------- 2 ---------------- */}
        <ReportSection
          title="2. Kiến thức nền và bảng ký hiệu"
          description="Sinh viên cần nắm cột giữa trước khi đọc phần công thức. Mỗi khái niệm đều được dùng ở một mục cụ thể của paper."
          meta="Đọc trước khi vào §3"
          divided
        >
          <Stack gap="container">
            <Table headers={["Khối kiến thức", "Cần nắm điều gì", "Dùng ở đâu"]} rows={prereqRows} density="compact" />
            <CollapsibleSection title="Bảng ký hiệu toán học đầy đủ (23 ký hiệu)" defaultOpen={false}>
              <Table headers={["Ký hiệu", "Ý nghĩa và đơn vị"]} rows={notationRows} density="compact" />
            </CollapsibleSection>
          </Stack>
        </ReportSection>

        {/* ---------------- 3 ---------------- */}
        <ReportSection
          title="3. MDP: quan sát và ngữ nghĩa hành động"
          description="Đây là phần quyết định paper đo được cái gì. Đọc kỹ hai công thức đầu tiên."
          meta="§III-A · traceability #1, #2, #6"
          divided
        >
          <Stack gap="container">
            <Text>
              Bài toán được phát biểu thành một MDP episodic{" "}
              <Code>M = (S, A, P, R, γ)</Code> với <Code>γ = 0.99</Code>. Mỗi bước, môi trường phơi ra trạng thái:
            </Text>

            <Formula
              tag="CT-1"
              title="Quan sát 12 chiều của A2C"
              code={`sₜ = [ pₜ , vₜ , g − pₜ , wₜ ]  ∈ ℝ¹²
        └─3─┘ └─3─┘ └───3───┘ └─3─┘
       vị trí  vận  dịch chuyển   gió
              tốc   tới đích`}
            />
            <Bullets
              items={[
                <span key="1">Vì sao dùng <Code>g − pₜ</Code> thay vì <Code>g</Code>: đây là vector dịch chuyển tương đối, giúp policy bất biến với vị trí tuyệt đối của đích (map 300 m có đích ở (300, 150, 5)); mạng không phải học một hằng số tọa độ.</span>,
                <span key="2"><b>Không có thành phần vật cản nào</b>: không khoảng cách, không góc, không occupancy. Vật cản chỉ đi vào 4 nơi: APF, số hạng clearance của reward, phép thử va chạm, và các metric offline.</span>,
                <span key="3">Hệ quả phương pháp luận: mọi khác biệt H0−H1 đều bị trộn lẫn với lượng thông tin bổ sung mà kênh APF mang vào (xem Callout ở Phần 1).</span>,
                <span key="4"><Code>wₜ</Code> là vận tốc không khí, không phải lực — xem CT-4.</span>,
              ]}
            />

            <Formula
              tag="CT-2"
              title="Hành động là LỆNH LỰC chuẩn hóa, không phải gia tốc"
              code={`aₜᴬ²ᶜ ∈ [−1, 1]³                      (policy output, liên tục)
F_cmd = 12 N × clip(aₜᴬ²ᶜ, −1, 1)      (clip THEO TỪNG TRỤC)
⇒ ‖F_cmd‖ tối đa = 12·√3 ≈ 20.78 N     (không phải 12 N)`}
            />
            <Bullets
              items={[
                <span key="1"><b>Cạm bẫy số 1:</b> giới hạn 12 N áp dụng cho từng trục, không áp cho chuẩn vector. Vector lực thực tế có thể đạt ~20.78 N theo hướng chéo. Mô tả sai chỗ này sẽ làm sai toàn bộ diễn giải về gia tốc.</span>,
                <span key="2"><b>Cạm bẫy số 2:</b> đây là lực, nên gia tốc còn phụ thuộc khối lượng, trọng lực, drag và gió (CT-4). Không được đọc <Code>a = 1</Code> thành "gia tốc 1 m/s²".</span>,
                <span key="3">Gia tốc lớn nhất có thể ra lệnh theo phương ngang: 12 N / 0.5 kg = 24 m/s² — gần 2.4 g. Đây là con số mà multirotor thật không đạt được, và là lý do paper từ chối nói về flyability.</span>,
              ]}
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 4 ---------------- */}
        <ReportSection
          title="4. Động lực học point-mass, chân trời episode và ngữ nghĩa va chạm"
          description="Bốn công thức vật lý + một công thức chân trời. Tham số: m = 0.5 kg, k_d = 0.12, g₀ = 9.81 m/s², Δt = 0.1 s."
          meta="§III-B, §III-C · traceability #7–#12, #20"
          divided
        >
          <Stack gap="container">
            <Formula
              tag="CT-3"
              title="Tổng lực tác dụng"
              code={`Fₜ = 12 · clip(uₜ, −1, 1) − m · g₀ · e_z

với e_z là vector đơn vị hướng lên (+z); trọng lực luôn kéo xuống
uₜ là lệnh CHUẨN HÓA sau khi đã trộn A2C và APF (xem CT-14)`}
            />
            <Formula
              tag="CT-4"
              title="Gia tốc — drag tác dụng lên VẬN TỐC TƯƠNG ĐỐI"
              code={`aₜ = ( Fₜ − k_d · (vₜ − wₜ) ) / m

(vₜ − wₜ) = vận tốc của UAV so với khối không khí = "air velocity"`}
            />
            <Bullets
              items={[
                <span key="1"><b>Đây là điểm mô hình tinh tế nhất.</b> Gió KHÔNG được cộng thẳng vào vị trí. Nó đi vào qua drag: nếu UAV bay đúng bằng vận tốc gió (vₜ = wₜ) thì drag = 0, tức là "bay theo gió" thì không cảm nhận lực cản.</span>,
                <span key="2">So sánh với mô hình cũ trong <Code>README.md</Code> gốc của repo (<Code>aₓ = (Fₓ + 0.3·wₓ − k_d·vₓ)/m</Code>): ở đó gió là lực cộng trực tiếp. Hai mô hình này KHÁC nhau về vật lý — README gốc đã lỗi thời so với paper, không dùng làm tài liệu tham chiếu.</span>,
                <span key="3">Với k_d = 0.12 và m = 0.5 kg, vận tốc tới hạn khi lực đẩy cân bằng drag là 12/0.12 = 100 m/s theo một trục — mô hình gần như không có giới hạn tốc độ thực tế, một giới hạn cần nêu khi nói về tính hiện thực.</span>,
              ]}
            />

            <Formula
              tag="CT-5, CT-6"
              title="Tích phân Euler bán ẩn (semi-implicit / symplectic)"
              code={`vₜ₊₁ = vₜ + aₜ · Δt          (cập nhật VẬN TỐC trước)
pₜ₊₁ = pₜ + vₜ₊₁ · Δt        (rồi dùng vận tốc MỚI để cập nhật vị trí)

Δt = 0.1 s  ⇒  1 transition = 0.1 s thời gian mô phỏng`}
            />
            <Text size="small" tone="secondary">
              Khác Euler hiện (<Code>pₜ₊₁ = pₜ + vₜ·Δt</Code>) ở chỗ dùng vₜ₊₁. Euler bán ẩn bảo toàn năng lượng tốt hơn
              cho hệ có thành phần bảo thủ, ít bị "nổ" số học khi bước tích phân lớn — lựa chọn hợp lý cho mô phỏng
              RL cần chạy hàng triệu bước.
            </Text>

            <Formula
              tag="CT-7"
              title="Clamp độ cao và reset vận tốc dọc"
              code={`z_cl = clamp(zₜ₊₁, 5 m, 6 m)
nếu z_cl ≠ zₜ₊₁ (tức là clamp có kích hoạt):  v_z ← 0

⇒ không gian bay thực chất là một "tấm slab" 2.5-D dày 1 m
⇒ hệ quả quan trọng: số hạng phạt độ cao r_z trong reward là CODE CHẾT (xem CT-18)`}
            />

            <Formula
              tag="CT-8"
              title="Chân trời episode (Equation 6 trong paper)"
              code={`H = ⌊ ( ‖g_xy − p₀,xy‖ / (v_ref · Δt) ) · 1.8 ⌋ + 300 ,   v_ref = 5 m/s

Với map 300 m:  start (0, 0, 5), goal (300, 150, 5)
  ‖g_xy − p₀,xy‖ = √(300² + 150²) = 335.41 m
  H = ⌊(335.41 / (5 · 0.1)) · 1.8⌋ + 300 = ⌊670.82 · 1.8⌋ + 300 = ⌊1207.48⌋ + 300 = 1507 transition
  ⇒ thời gian tối đa = 1507 × 0.1 s ≈ 150.7 s`}
            />
            <Bullets
              items={[
                <span key="1">Ý nghĩa từng thành phần: <Code>‖g_xy − p₀,xy‖/(v_ref·Δt)</Code> là số bước cần thiết nếu bay thẳng với vận tốc tham chiếu 5 m/s; hệ số <Code>1.8</Code> là dư địa cho đường vòng tránh vật cản và gió thổi lệch; <Code>+300</Code> bước là đệm cố định cho giai đoạn tiếp cận đích.</span>,
                <span key="2">Chân trời TỰ ĐỘNG co giãn theo kích thước map — đây là lựa chọn thiết kế giúp cùng một giao thức áp dụng cho map ngắn/dài mà không phải chỉnh tay.</span>,
                <span key="3">Giá trị 1507 (không phải 500 như tài liệu cũ) giải thích vì sao H1 có những episode kéo dài tới trần và vì sao SD của steps lên tới 451.3.</span>,
              ]}
            />

            <Formula
              tag="CT-9"
              title="Ngữ nghĩa kết thúc episode — mỗi episode đúng MỘT trạng thái"
              code={`collision = swept_AABB(pₜ → pₜ₊₁, obstacle_i, radius = 0)   với mọi i
success   = ( ‖g − p_T‖ < 3 m )  AND  ( NOT collision )
timeout   = hết H transition mà chưa success

Thứ tự ưu tiên: COLLISION được xét TRƯỚC success
⇒ nếu chạm vật cản đúng lúc chạm ngưỡng 3 m → tính là collision`}
            />
            <Bullets
              items={[
                <span key="1"><b>Swept collision (phép thử slab):</b> kiểm tra cả ĐOẠN thẳng từ pₜ đến pₜ₊₁ chứ không chỉ điểm cuối. Với Δt = 0.1 s và vận tốc ~10 m/s, mỗi bước UAV đi được ~1 m — đủ để "xuyên hầm" qua thành mỏng nếu chỉ test điểm cuối.</span>,
                <span key="2"><b>Bán kính phồng UAV = 0</b>: UAV được coi là một điểm. Đây là giả định lạc quan, cần nêu khi bàn về an toàn.</span>,
                <span key="3"><b>Accounting đầy đủ</b>: success + collision + timeout = 1000 cho mỗi cấu hình. Gói reproducibility có test tự động kiểm tra "đúng một trạng thái kết thúc trên mỗi dòng" (0 vi phạm).</span>,
                <span key="4"><b>Vị trí ban đầu có nhiễu:</b> p₀ = (0, 0, 5) cộng nhiễu đều U(−0.5, +0.5) m cho từng tọa độ trước khi clamp độ cao → tránh việc policy học thuộc một điểm khởi đầu duy nhất.</span>,
              ]}
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 5 ---------------- */}
        <ReportSection
          title="5. Artificial Potential Field và cơ chế trộn thích ứng"
          description="Trái tim kỹ thuật của paper: 3 công thức APF + 2 công thức blend. Chú ý quy ước khoảng cách tới TÂM vật cản."
          meta="§III-D · traceability #13–#17"
          divided
        >
          <Stack gap="container">
            <Formula
              tag="CT-10"
              title="Lực hút về đích"
              code={`qₜ = g − pₜ                                   (vector dịch chuyển tới đích)
F_att(pₜ) = k_att · qₜ / (‖qₜ‖ + ε) ,   k_att = 0.04 ,  ε = 10⁻⁶

⇒ ‖F_att‖ ≈ 0.04 (hằng số, không phụ thuộc khoảng cách) — chỉ giữ HƯỚNG`}
            />
            <Text size="small" tone="secondary">
              Đây là gradient của thế hút tuyến tính (thế tỉ lệ với khoảng cách), không phải thế bậc hai. Vì chuẩn hóa
              theo <Code>‖qₜ‖</Code> nên lực hút không tăng khi càng gần đích — tránh hiện tượng "lao vào đích" với
              vận tốc lớn. <Code>ε = 10⁻⁶</Code> chỉ để chống chia 0 khi UAV đứng đúng tại đích.
            </Text>

            <Formula
              tag="CT-11, CT-12"
              title="Lực đẩy từ vật cản — dạng Khatib kinh điển, nhưng đo tới TÂM"
              code={`dᵢ = ‖pₜ − cᵢ‖ + ε            (cᵢ = TÂM của AABB thứ i, không phải điểm gần nhất trên mặt)

                 ⎧ k_rep · (1/dᵢ − 1/d₀) · (pₜ − cᵢ)/dᵢ³      nếu dᵢ < d₀
F_rep,ᵢ(pₜ) =   ⎨
                 ⎩ 0                                            nếu dᵢ ≥ d₀

với k_rep = 18 ,  d₀ = 6 m`}
            />
            <Bullets
              items={[
                <span key="1"><b>Đọc công thức này thế nào:</b> <Code>(1/dᵢ − 1/d₀)</Code> là độ lớn thế đẩy, bằng 0 đúng tại biên d₀ và tiến tới ∞ khi dᵢ → 0; <Code>(pₜ − cᵢ)/dᵢ</Code> là vector đơn vị chỉ hướng đẩy ra xa tâm. Nhân hai cái lại với một <Code>1/dᵢ²</Code> nữa (gradient của thế) → ra số mũ <Code>dᵢ³</Code> ở mẫu.</span>,
                <span key="2"><b>Vai trò của d₀ = 6 m:</b> APF chỉ là phản xạ CỤC BỘ. Ngoài 6 m tính từ tâm vật cản, lực đẩy bằng đúng 0 → UAV không bị "đẩy" bởi cả bản đồ, chỉ bởi thứ ở ngay cạnh.</span>,
                <span key="3"><b>Lỗi thiết kế được paper tự khai báo:</b> vì dᵢ đo tới TÂM, một khối hộp lớn có thể ở rất gần mà APF vẫn im lặng.</span>,
              ]}
            />
            <Callout tone="danger" title="Ví dụ số cho thấy APF under-repel (nên giảng kỹ cho sinh viên)">
              <Text size="small">
                Một khối AABB cạnh 20 m, tâm cách UAV 12 m. Khoảng cách tới MẶT gần nhất chỉ là 12 − 10 = <b>2 m</b> —
                tức là sắp đâm. Nhưng vì dᵢ = 12 m {"≥"} d₀ = 6 m nên <Code>F_rep = 0</Code>: APF hoàn toàn không phản ứng.
                Ngược lại, metric clearance mà paper báo cáo lại dùng khoảng cách BỀ MẶT (2 m). Hai đại lượng khác nhau
                này là lời giải thích cơ chế chính cho tỉ lệ va chạm 90.5% của H2.
              </Text>
            </Callout>

            <Formula
              tag="CT-13"
              title="Tổng hợp lực APF: chuẩn hóa có điều kiện rồi clip"
              code={`F_APF = F_att + Σᵢ F_rep,ᵢ

nếu ‖F_APF‖ > 1:   F_APF ← F_APF / ‖F_APF‖      (chỉ khi vượt 1)
aₜᴬᴾᶠ = clip(F_APF, −1, 1)                        (clip theo từng thành phần)

THỨ TỰ QUAN TRỌNG: normalize TRƯỚC, clip SAU`}
            />
            <Text size="small" tone="secondary">
              Chuẩn hóa có điều kiện (chỉ khi chuẩn {"&gt;"} 1) giữ nguyên hướng và giữ tỉ lệ tương đối giữa hút/đẩy khi
              lực còn nhỏ; clip theo thành phần đảm bảo đầu ra nằm đúng trong không gian hành động <Code>[−1,1]³</Code>{" "}
              để trộn được với output của A2C. Nếu đảo thứ tự (clip trước rồi chuẩn hóa) thì hướng lực sẽ bị méo.
            </Text>

            <Formula
              tag="CT-14, CT-15"
              title="Trộn lồi thích ứng theo khoảng cách tới đích"
              code={`uₜ = (1 − λₜ) · aₜᴬ²ᶜ  +  λₜ · aₜᴬᴾᶠ

λₜ = clip( 1 − ‖g − pₜ‖/300 , 0.15 , 0.55 )

  khoảng cách tới đích   335.4 m   300 m   255 m   180 m   135 m    0 m
  λₜ (giá trị thực tế)    0.15     0.15    0.15    0.40    0.55    0.55
  ý nghĩa                tin RL ←────────────────────────→ tin APF`}
            />
            <Bullets
              items={[
                <span key="1"><b>Vì sao là trộn lồi (convex):</b> cả hai thành phần đều nằm trong [−1,1]³ và λ ∈ [0,1], nên uₜ cũng nằm trong [−1,1]³ — không cần clip lại lần nữa và không bao giờ vượt giới hạn lực.</span>,
                <span key="2"><b>Logic điều khiển:</b> ở pha hành trình xa đích, bài toán chủ yếu là "đi tới" → tin policy học được (λ = 0.15). Ở pha tiếp cận, hình học vật cản quanh khe hở quan trọng hơn → tăng vai trò APF (λ tới 0.55).</span>,
                <span key="3"><b>Giả thuyết cơ chế trong paper:</b> vì là hỗn hợp lồi, APF có thể đã "làm dịu" những thay đổi lệnh lớn của A2C ở vùng cuối → giải thích jitter thấp hơn. Nhưng paper nói rõ đây chỉ là GIẢ THUYẾT CHẨN ĐOÁN vì không có action trace tách riêng hai kênh.</span>,
                <span key="4"><b>Cấu hình đối chứng:</b> H1 đặt <Code>policy_mode = "a2c"</Code> nên bỏ hẳn phép trộn (tương đương λ = 0, và manifest đặt <Code>apf_weight = 0.0</Code>); H2 đặt <Code>policy_mode = "apf"</Code> nên <Code>uₜ = aₜᴬᴾᶠ</Code> với action của policy là vector 0.</span>,
              ]}
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 6 ---------------- */}
        <ReportSection
          title="6. Hàm thưởng — từng số hạng và từng con số"
          description="Sáu thành phần. Chú ý hai điểm: dải clearance chỉ thưởng chứ không phạt, và số hạng độ cao không bao giờ chạy."
          meta="§III-E · traceability #13, #18, #19"
          divided
        >
          <Stack gap="container">
            <Formula
              tag="CT-16"
              title="Reward tại bước t"
              code={`rₜ = 3·(dₜ₋₁ − dₜ)        ① shaping tiến bộ về đích
   − 0.05                  ② phạt thời gian (mỗi bước)
   − 200·𝟙[collision]      ③ phạt va chạm
   + Bₜ·𝟙[success]         ④ thưởng về đích  (xem CT-17)
   + 0.3·(δₜ − 2)·𝟙[2 < δₜ < 8]   ⑤ thưởng giữ khoảng cách an toàn
   + r_z                   ⑥ phạt vượt dải độ cao (xem CT-18 — BẤT HOẠT)

với dₜ = ‖g − pₜ‖ tính SAU transition, δₜ = clearance CÓ DẤU tới bề mặt AABB gần nhất`}
            />
            <Table
              headers={["#", "Số hạng", "Đơn vị / dải", "Giải thích và hệ quả"]}
              rows={[
                ["①", "3·(dₜ₋₁ − dₜ)", "điểm trên mỗi mét tiến lại gần", "Dạng potential-based shaping: chỉ thưởng cho SỰ THAY ĐỔI khoảng cách nên không tạo cực tiểu giả. Tiến 1 m được +3, lùi 1 m bị −3. Đây là tín hiệu dày (dense) duy nhất dẫn dắt policy ở xa đích."],
                ["②", "−0.05 / bước", "điểm", "Chống lảng vảng. Với H = 1507 bước, tổng phạt thời gian tối đa ≈ −75 điểm — nhỏ hơn nhiều so với thưởng về đích (≥ 80) nên không khuyến khích tự kết thúc sớm."],
                ["③", "−200 khi va chạm", "điểm", "Phạt thưa (sparse) nhưng lớn gấp ~2.5 lần thưởng về đích tối đa → tạo gradient ưu tiên an toàn. Tuy nhiên vì thưa nên policy chỉ học được qua những lần thực sự đâm."],
                ["④", "Bₜ khi về đích", "80 → 150 điểm", "Xem CT-17: thưởng GIẢM dần theo số bước đã dùng, nhưng có sàn 80 điểm."],
                ["⑤", "0.3·(δₜ − 2) trong dải 2–8 m", "tối đa +1.8 điểm/bước", "Tăng dần theo clearance trong dải → khuyến khích đi giữa chứ không sát vật cản. NGOÀI dải (δ ≥ 8) không thưởng thêm; DƯỚI 2 m KHÔNG có phạt trực tiếp nào ngoài ③ khi thực sự đâm. Đây là một khoảng trống thiết kế đáng phê bình."],
                ["⑥", "r_z", "−15·(khoảng vượt)", "CODE CHẾT — xem CT-18."],
              ]}
              density="compact"
            />

            <Formula
              tag="CT-17"
              title="Thưởng về đích phụ thuộc thời gian"
              code={`Bₜ = max( 80 , 150 · (1 − nₜ/H) )

  bay rất nhanh (nₜ → 0)     : Bₜ → 150
  bay hết chân trời (nₜ = H) : 150·0 = 0  → nhưng max() ép lên 80
  điểm hoà vốn              : 150·(1 − nₜ/H) = 80  ⇒ nₜ = 0.4667·H ≈ 703 bước`}
            />
            <Text size="small" tone="secondary">
              Vai trò của <Code>max(80, ·)</Code>: đảm bảo về đích LUÔN có lãi ròng so với va chạm (−200) hoặc timeout (0),
              kể cả khi bay chậm. Nếu không có sàn này, một episode chậm sẽ nhận thưởng ~0 và policy có thể học cách
              "kết thúc sớm" để tránh phạt thời gian.
            </Text>

            <Formula
              tag="CT-18"
              title="Phạt độ cao — và vì sao nó không bao giờ chạy"
              code={`r_z = −15·(5 − z)   nếu z < 5 m
r_z = −15·(z − 6)   nếu z > 6 m
r_z = 0             nếu 5 ≤ z ≤ 6

NHƯNG: độ cao đã bị clamp về [5, 6] ở CT-7 TRƯỚC khi reward đọc z
⇒ tại thời điểm tính reward luôn có z ∈ [5, 6] ⇒ cả hai nhánh phạt không thể kích hoạt`}
            />
            <Callout tone="warning" title="Vì sao paper vẫn in công thức của một số hạng chết?">
              <Text size="small">
                Vì nguyên tắc <b>implementation alignment</b> (Henderson 2018): mô tả controller phải khớp CHÍNH XÁC với
                code đã chạy, kể cả phần không hoạt động. Giấu nó đi sẽ khiến người tái lập kết quả gặp một reward
                function khác. Đây là ví dụ rất tốt để dạy sinh viên về sự khác biệt giữa "mô hình trên giấy" và
                "mô hình đã thực thi". Muốn số hạng này có tác dụng, phải tính reward TRƯỚC khi clamp, hoặc bỏ clamp
                và để UAV thực sự bay ra khỏi dải.
              </Text>
            </Callout>

            <CollapsibleSection title="Hai quy ước khoảng cách trong cùng một hệ thống (bắt buộc phải phân biệt)" defaultOpen>
              <Table
                headers={["Đại lượng", "Đo tới đâu", "Dùng ở đâu", "Hệ quả"]}
                rows={[
                  [<Code key="a">dᵢ</Code>, "TÂM của AABB", "Lực đẩy APF (CT-11, CT-12)", "Under-repel với khối lớn; APF có thể im lặng khi sắp đâm"],
                  [<Code key="b">δₜ</Code>, "BỀ MẶT gần nhất của AABB (có dấu)", "Số hạng ⑤ của reward và metric clearance báo cáo trong paper", "Phản ánh đúng rủi ro va chạm"],
                ]}
                density="compact"
              />
              <Text size="small" tone="secondary">
                Paper khẳng định hai đại lượng này không hoán đổi được cho nhau, và không được mô tả lực đẩy APF như
                là "surface-based". Đây chính là một phần lý do H2 (chỉ APF) va chạm 90.5%.
              </Text>
            </CollapsibleSection>
          </Stack>
        </ReportSection>

        {/* ---------------- 7 ---------------- */}
        <ReportSection
          title="7. Mô hình gió tương quan AR(1) (Dryden-lite)"
          description="Gió là nhiễu CÓ MÀU, không phải nhiễu trắng. Bốn công thức và một chứng minh ngắn về phương sai dừng."
          meta="§III-F · seed_provenance.md"
          divided
        >
          <Stack gap="container">
            <Formula
              tag="CT-19"
              title="Hệ số suy giảm theo bước thời gian"
              code={`φ = exp(−Δt / τ) ,   τ = 0.9 s ,  Δt = 0.1 s
φ = exp(−0.1/0.9) = exp(−0.1111) ≈ 0.8948   (giá trị suy ra, paper không in số)`}
            />
            <Text size="small" tone="secondary">
              τ = 0.9 s nghĩa là một cơn gió giật mất khoảng 0.9 s để suy giảm còn 1/e ≈ 37% biên độ. Đây chính là
              "quán tính" của khí quyển: gió không đổi hướng tức thời giữa hai bước mô phỏng.
            </Text>

            <Formula
              tag="CT-20"
              title="Nhiễu đổi mới có tương quan chéo giữa các trục"
              code={`ηₜ = L · ξₜ ,   ξₜ ~ N(0, I₃)

L·Lᵀ có:  tương quan chéo ngang (x↔y) = 0.35
          tương quan ngang–dọc = 0
          hệ số phương sai trục dọc = 0.09  (⇒ tỉ lệ std dọc = √0.09 = 0.3)`}
            />
            <Bullets
              items={[
                <span key="1">L là phân tích Cholesky của ma trận hiệp phương sai mong muốn — cách chuẩn để biến nhiễu trắng độc lập thành nhiễu có cấu trúc tương quan.</span>,
                <span key="2">Tương quan ngang 0.35: gió tạt theo x thường đi kèm thành phần theo y — mô phỏng luồng gió thổi xiên, không phải ba trục độc lập.</span>,
                <span key="3">Hệ số dọc 0.09: nhiễu dọc yếu hơn nhiều (0.3 lần), hợp với thực tế là rối khí quyển ngang mạnh hơn dọc ở tầng thấp. Kết hợp với clamp độ cao [5, 6] m, trục z gần như bị khống chế.</span>,
              ]}
            />

            <Formula
              tag="CT-21"
              title="Cập nhật gió giật và gió tổng"
              code={`gₜ₊₁ʷ = φ · gₜʷ  +  1.2 · √(1 − φ²) · ηₜ
wₜ    = w_base + gₜʷ

w_base = [ 2·cos θ , 2·sin θ , 0 ] ,   θ ~ U(0, 2π)  (lấy mẫu MỘT lần tại reset)`}
            />
            <Callout tone="info" title="Vì sao phải có √(1 − φ²)? — chứng minh 3 dòng nên dạy sinh viên">
              <Stack gap="micro">
                <Text size="small">
                  Gọi Var(gₜʷ) = σ². Ở trạng thái dừng: <Code>σ² = φ²σ² + 1.2²(1 − φ²)</Code>
                </Text>
                <Text size="small">
                  <Code>⇒ σ²(1 − φ²) = 1.2²(1 − φ²)  ⇒  σ² = 1.2²  ⇒  σ = 1.2 m/s</Code>
                </Text>
                <Text size="small" tone="secondary">
                  Nếu bỏ hệ số này, biên độ gió giật sẽ trôi theo φ và phụ thuộc độ dài episode — mỗi map sẽ có một
                  "mức gió" khác nhau, làm hỏng khả năng so sánh. Với φ ≈ 0.8948 thì hệ số nhân thực tế là
                  1.2 × √(1 − 0.8007) ≈ 1.2 × 0.4465 ≈ <b>0.536</b>.
                </Text>
              </Stack>
            </Callout>
            <Bullets
              items={[
                <span key="1"><b>Quy mô nhiễu thực tế:</b> gió nền 2 m/s + gió giật std 1.2 m/s ngang (0.36 m/s dọc) ⇒ tổng vận tốc gió điển hình 2–3.5 m/s, tức ~20–35% tốc độ tham chiếu 5 m/s. Đây là mức gió đáng kể nhưng không cực đoan.</span>,
                <span key="2"><b>Một realization gió cho cả episode:</b> hướng gió nền và chuỗi nhiễu AR(1) đều lấy từ RNG của env, được seed bằng numerical seed. Vì vậy H0 và H1 ở cùng slot đánh giá gặp ĐÚNG MỘT cơn gió — đây là điều kiện để ghép cặp hợp lệ.</span>,
                <span key="3"><b>Giới hạn paper tự nêu:</b> đây không phải phổ Dryden đã kiểm chứng, cũng không phải mô hình khí động học đô thị. Và vì không có điều kiện no-wind hay mức gió khác, paper KHÔNG thiết lập được robustness theo cường độ gió — mặc dù tiêu đề có chữ "Wind-Perturbed".</span>,
                <span key="4">H3 (no-wind) và H5 (strong-wind) đã được ĐỊNH NGHĨA trong manifest nhưng bị loại khỏi tập bằng chứng. Đây là thí nghiệm bổ sung rẻ nhất và đáng làm nhất nếu có revision.</span>,
              ]}
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 8 ---------------- */}
        <ReportSection
          title="8. A2C: nền thuật toán và cấu hình huấn luyện"
          description="Ba công thức nền (KHÔNG in trong paper — kiến thức bổ trợ để hiểu vì sao chọn A2C) và bảng siêu tham số đã dùng."
          meta="§III-G · seed_provenance.md · computational_requirements.md"
          divided
        >
          <Stack gap="container">
            <Callout tone="info" title="Đánh dấu rõ: CT-23 → CT-25 là kiến thức nền về A2C (SB3), paper không trình bày các công thức này">
              <Text size="small">
                Paper chỉ nêu lý do chọn A2C và liệt kê siêu tham số. Ba công thức dưới đây giúp sinh viên hiểu
                "advantage" trong tên gọi A2C nghĩa là gì và entropy coefficient 0.02 tác động vào đâu.
              </Text>
            </Callout>

            <Formula
              tag="CT-23"
              title="Policy gradient với advantage (nền)"
              code={`∇θ J(θ) = E[ ∇θ log πθ(aₜ|sₜ) · Âₜ ]

Âₜ = Qπ(sₜ,aₜ) − Vπ(sₜ)   (advantage: hành động này tốt hơn trung bình bao nhiêu)
⇒ log π được đẩy LÊN nếu Â > 0 và kéo XUỐNG nếu Â < 0`}
            />
            <Formula
              tag="CT-24"
              title="Hàm mất mát A2C mà SB3 tối thiểu hóa (nền)"
              code={`L(θ, φ) = − E[ log πθ(aₜ|sₜ) · Âₜ ]        (actor: leo đồi chính sách)
        + c₁ · E[ ( Vφ(sₜ) − Rₜ )² ]        (critic: hồi quy giá trị, c₁ = 0.5)
        − c₂ · H[ πθ(·|sₜ) ]                (entropy: khuyến khích khám phá, c₂ = 0.02)`}
            />
            <Formula
              tag="CT-25"
              title="GAE — cách tính Â trong thực tế (nền)"
              code={`δₜ = rₜ + γ·Vφ(sₜ₊₁) − Vφ(sₜ)                (TD-error)
Âₜᴳᴬᴱ(γ,λ) = Σₗ₌₀^∞ (γλ)ˡ · δₜ₊ₗ           (γ = 0.99, λ_GAE = 0.95)

λ → 0 : Â ≈ δₜ           (bias cao, phương sai thấp)
λ → 1 : Â ≈ Monte-Carlo  (bias thấp, phương sai cao)
λ = 0.95: điểm cân bằng thực nghiệm`}
            />

            <Table
              headers={["Tham số", "Giá trị", "Vai trò / vì sao chọn"]}
              rows={[
                ["Thư viện & policy", "Stable-Baselines3, MlpPolicy", "Mạng MLP chuẩn, ít thành phần → dễ quy kết nguyên nhân; SB3 là implementation được kiểm chứng rộng rãi"],
                ["Thiết bị", "CPU (device = 'cpu' cưỡng bức)", "A2C với observation 12 chiều không cần GPU; loại bỏ biến thiên do CUDA"],
                ["Learning rate", "3 × 10⁻⁴", "Giá trị mặc định phổ biến cho actor–critic"],
                ["n_steps (rollout)", "256", "On-policy: thu 256 bước rồi cập nhật. Ngắn hơn PPO thường dùng nhưng đủ cho bài toán 1 env"],
                ["γ (chiết khấu)", "0.99", "Tầm nhìn hiệu dụng ~100 bước = 10 s mô phỏng"],
                ["λ (GAE)", "0.95", "Cân bằng bias/variance cho advantage"],
                ["Entropy coefficient", "0.02", "Giữ khám phá; quá nhỏ → policy sập sớm vào nghiệm dao động"],
                ["Max gradient norm", "0.5", "Cắt gradient, ổn định huấn luyện khi có reward −200 thưa và lớn"],
                ["Ngân sách huấn luyện", "5.000.000 bước môi trường cho MỖI unit", "Tổng 40 unit học được (H0 + H1) = 200 triệu bước"],
                ["Số env song song khi train", "1 env (n_envs = 1)", <span key="nenv">Đúng như paper mô tả: <Code>run_rigorous_manifest.py:146</Code> đặt n_envs = 1 cho chiến dịch canonical. Lưu ý: pipeline so sánh cũ (<Code>vnict_hybrid_experiments.py</Code>) có preset n_envs = 4 cho chế độ 300k bước — đó KHÔNG phải run đã dùng cho paper.</span>],
                ["Seed huấn luyện", "101, 211, 307, 401, 503", "5 model ĐỘC LẬP cho mỗi map — không phải 5 checkpoint của một lần chạy"],
                ["Chính sách khi đánh giá", "deterministic = True", "Loại bỏ phương sai lấy mẫu hành động để đo đúng chất lượng policy"],
              ]}
              density="compact"
            />

            <Callout tone="warning" title="Ba lưu ý về thuật ngữ và tính tái lập">
              <Bullets
                items={[
                  <span key="1"><b>"Checkpoint" là từ sai.</b> Code (<Code>train_model</Code>) huấn luyện một model MỚI từ đầu cho mỗi cặp (map, seed). Bản sửa manuscript yêu cầu thay bằng "independent training run / model" — và paper canonical đã dùng "five independently trained runs (models) per map".</span>,
                  <span key="2"><b>PyTorch không được seed tường minh.</b> Chỉ có <Code>random</Code>, <Code>numpy</Code> và VecEnv nhận training seed; không có <Code>torch.manual_seed</Code>. Do đó huấn luyện lại từ đầu KHÔNG tái lập bitwise. Đánh giá lại từ checkpoint đã lưu thì tất định.</span>,
                  <span key="3"><b>Chi phí tính toán:</b> manifest dự phóng ~44.8 ngày chạy TUẦN TỰ cho toàn bộ ma trận huấn luyện được (4 thuật toán × 5 map × 5 seed). Phần bằng chứng thực tế của paper chỉ là tập con A2C 4 map, chạy song song được trên nhiều nhân. Máy tham chiếu: Ryzen 9 9950X (16C/32T), 64 GB RAM, RTX 3090 (không dùng cho A2C).</span>,
                ]}
              />
            </Callout>
          </Stack>
        </ReportSection>

        {/* ---------------- 9 ---------------- */}
        <ReportSection
          title="9. Thiết kế thực nghiệm: H0–H4, cấu trúc lồng nhau và số học của mẫu"
          description="Phần dễ bị reviewer tấn công nhất — và cũng là phần paper xử lý cẩn thận nhất."
          meta="§IV-A · experimental_design.md"
          divided
        >
          <Stack gap="container">
            <Formula
              tag="Sơ đồ"
              title="Hệ thống phân cấp của một cấu hình (đọc từ trên xuống)"
              code={`configuration  (H0 / H1 / H2)
  └── map                 {random-01, corridor-01, barrier-01, mixed-01}   → 4
        └── training run  {seed 101, 211, 307, 401, 503}                    → 5
              │            (H2: chỉ là NHÃN, không học)
              └── evaluation seed slot  base ∈ {1009,1013,1019,1021,1031} × episode 0..9  → 50
                    └── rollout (một episode tất định)                      → 1

  4 map × 5 run = 20 unit / cấu hình học được
  20 unit × 50 slot = 1000 rollout / cấu hình
  3 cấu hình × 1000 = 3000 rollout  (H4 tái dùng 1000 quỹ đạo của H0)`}
            />
            <Table
              headers={["ID", "Loại", "Map / unit", "Huấn luyện", "Rollout", "Học?", "Ghi chú diễn giải"]}
              rows={designRows}
              density="compact"
              rowTone={["success", "info", "warning", "muted"]}
            />

            <CollapsibleSection title="Vấn đề pseudoreplication: 50 slot chỉ có 32 seed phân biệt" defaultOpen>
              <Stack gap="container">
                <Formula
                  tag="CT-26"
                  title="Cách sinh numerical seed và vì sao bị chồng lấn"
                  code={`numerical_seed = base_seed + episode_index
base_seed ∈ {1009, 1013, 1019, 1021, 1031} ,  episode_index ∈ {0..9}

Các cửa sổ 10 slot sinh ra:
  1009 → [1009 … 1018]
  1013 → [1013 … 1022]     chồng 1009 ở 1013–1018
  1019 → [1019 … 1028]     chồng 1013 ở 1019–1022
  1021 → [1021 … 1030]     chồng 1019 ở 1021–1028
  1031 → [1031 … 1040]

⇒ 50 slot nhưng chỉ 32 giá trị seed phân biệt (1009–1040)
⇒ 18 slot / unit là LẶP Y HỆT (cùng map, cùng model, cùng seed, policy tất định)
⇒ toàn chiến dịch: 18 × 60 unit = 1080 instance trùng, đã kiểm chứng byte-identical
   về status / steps / clearance / jitter bởi validate_ledger.py`}
                />
                <Bullets
                  items={[
                    <span key="1"><b>Vì sao đây là vấn đề:</b> nếu coi 50 rollout là 50 quan sát độc lập thì n bị phồng 1.56 lần, khoảng tin cậy hẹp giả tạo và p-value nhỏ giả tạo.</span>,
                    <span key="2"><b>Paper xử lý thế nào:</b> tỉ lệ vẫn báo cáo trên 50 slot (đúng như đã chạy), nhưng <b>không</b> dùng rollout làm đơn vị suy luận — suy luận dùng 20 đơn vị (map × training run). Wilson CI chỉ được gọi là "descriptive".</span>,
                    <span key="3"><b>Cách sửa nếu làm lại:</b> chọn 5 base seed cách nhau ≥ 10 (ví dụ 1009, 1019, 1029, 1039, 1049) → 50 slot với 50 seed phân biệt, không đổi số lượng rollout.</span>,
                    <span key="4"><b>Lưu ý tinh tế:</b> cùng một numerical seed ở hai unit KHÁC nhau vẫn là hai điều kiện khác nhau (map hoặc model khác). Chỉ trùng lặp bên trong một unit. Trường <Code>full_condition_hash = map_hash | controller | numerical_seed</Code> trong ledger nắm đúng điều này.</span>,
                  ]}
                />
              </Stack>
            </CollapsibleSection>

            <CollapsibleSection title="Ghép cặp H0–H1: cái gì khớp và cái gì không" defaultOpen>
              <Table
                headers={["Yếu tố", "H0 và H1 có khớp?", "Bằng chứng / ghi chú"]}
                rows={[
                  ["Map (hình học vật cản)", "KHỚP", "Cùng map_sha256 cho từng cặp"],
                  ["Nhãn training seed", "KHỚP", "Cùng 101/211/307/401/503"],
                  ["Ngân sách huấn luyện", "KHỚP", "5M bước mỗi unit"],
                  ["Realization reset + gió khi đánh giá", "KHỚP", "Cùng numerical seed truyền vào env.reset(seed=…) → cùng nhiễu khởi đầu và cùng chuỗi AR(1)"],
                  ["Số rollout mỗi unit", "KHỚP", "50 slot"],
                  [<b key="x">Trọng số policy đã học</b>, <b key="y">KHÔNG khớp (cố ý)</b>, "Hai model khác nhau — đây chính là đối tượng so sánh"],
                  [<b key="x2">Thông tin vật cản đầu vào</b>, <b key="y2">KHÔNG khớp (điểm yếu chí mạng)</b>, "H0 có qua APF; H1 không có. Đây là bất đối xứng thông tin chi phối mọi diễn giải"],
                ]}
                density="compact"
                rowTone={["default", "default", "default", "default", "default", "info", "danger"]}
              />
            </CollapsibleSection>

            <Grid columns={2} gap="container" minColumnWidth={280}>
              <KeyIdea term="Vì sao H2 không có lặp huấn luyện thật">
                H2 là APF thuần, không học (<Code>model = None</Code>, <Code>timesteps = 0</Code>). Năm nhãn seed mỗi map
                chỉ để giữ cấu trúc sổ sách — chúng là các lượt đánh giá lặp lại của MỘT bộ điều khiển cố định, không phải
                năm mẫu độc lập. Không được dùng H2 trong bất kỳ suy luận ghép cặp nào.
              </KeyIdea>
              <KeyIdea term="Vì sao H4 gần như là no-op">
                Spline tham số hóa từng tọa độ theo chỉ số mẫu chuẩn hóa rồi resample về <Code>max(20, N)</Code> điểm.
                Mọi quỹ đạo H0 đều có N ≥ 20 nên số điểm vào = số điểm ra, và spline được đánh giá đúng tại các vị trí
                tham số cách đều ban đầu. Nó chạy SAU rollout nên không thể đổi action, va chạm hay kết quả.
                Kết luận: jitter và accel không đổi tới độ chính xác số học.
              </KeyIdea>
            </Grid>

            <Table
              headers={["Map 300 m (density 0.8)", "Đặc trưng hình học", "Vai trò trong lập luận"]}
              rows={[
                [<Code key="1">map-random-01</Code>, "Trường vật cản ngẫu nhiên có seed", "Điều kiện chung nhất; H1 yếu nhất ở đây (140/250)"],
                [<Code key="2">map-corridor-01</Code>, "Hành lang tạo bởi các hộp ghép cặp", "Ràng buộc ngang lặp lại → phơi bày dao động; 10 failure của H1 đều là va chạm"],
                [<Code key="3">map-barrier-01</Code>, "Barrier hai phần có khe hở", "Kiểm tra khả năng duy trì tiến bộ qua khe; 50 failure của H1 đều là hết giờ"],
                [<Code key="4">map-mixed-01</Code>, "Barrier + ngẫu nhiên", "Trần kết quả của H1 (250/250) → bằng chứng APF KHÔNG cần thiết cho mọi layout"],
              ]}
              density="compact"
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 10 ---------------- */}
        <ReportSection
          title="10. Chỉ số đo và công thức thống kê"
          description="Bốn nhóm chỉ số và bốn công cụ suy luận. Chú ý ranh giới giữa MÔ TẢ và SUY LUẬN."
          meta="§IV-B"
          divided
        >
          <Stack gap="container">
            <H3>10.1 Nhóm chỉ số kết quả rời rạc</H3>
            <Formula
              tag="CT-27"
              title="Khoảng tin cậy Wilson cho một tỉ lệ (nền — dùng làm MÔ TẢ)"
              code={`        p̂ + z²/(2n)  ±  z · √( p̂(1−p̂)/n + z²/(4n²) )
CI  =  ─────────────────────────────────────────────────
                       1 + z²/n

z = 1.96 (95%) ;  n = 1000 ;  p̂ = success/1000

  H0: p̂ = 1.000 → CI [0.996, 1.000]     (chú ý: chặn trên đúng bằng 1)
  H1: p̂ = 0.830 → CI [0.805, 0.852]
  H2: p̂ = 0.055 → CI [0.042, 0.071]`}
            />
            <Text size="small" tone="secondary">
              Vì sao dùng Wilson thay vì khoảng chuẩn Wald <Code>p̂ ± z√(p̂(1−p̂)/n)</Code>: Wald sụp đổ khi p̂ gần 0 hoặc 1
              (với H0, Wald cho biên độ 0 → CI [1, 1] vô nghĩa). Wilson vẫn hợp lệ ở biên và với n nhỏ. Nhưng paper
              nhấn mạnh các CI này chỉ MÔ TẢ 1000 rollout — suy luận thật nằm ở kiểm định ghép cặp.
            </Text>

            <H3>10.2 Nhóm chỉ số chất lượng đường bay</H3>
            <Formula
              tag="CT-28"
              title="Hiệu suất đường bay thành công"
              code={`E = min( 1 ,  ‖g − p₀‖ / Σₜ₌₀^{T−1} ‖pₜ₊₁ − pₜ‖ )

tử số   = độ dài đường thẳng từ điểm XUẤT PHÁT tới đích
mẫu số  = độ dài đường bay thực tế (tổng quãng đường từng bước)
E = 1  ⇔ bay thẳng hoàn toàn ;  E càng nhỏ ⇔ càng vòng vèo

CHỈ tính trên các episode THÀNH CÔNG (loại bỏ failure)`}
            />
            <Bullets
              items={[
                <span key="1"><b>Thiên lệch sống sót:</b> H1 có 170 failure bị loại. So sánh E của H0 với E của một TẬP CON được chọn lọc của H1 (những episode mà H1 vốn đã làm tốt) là so sánh không cân xứng. Paper nêu rõ điều này.</span>,
                <span key="2"><b>Chỉ 18/20 cặp dùng được:</b> hai unit không có episode thành công nào ở một trong hai controller (<Code>map-barrier-01/seed401</Code> và <Code>map-random-01/seed307</Code>) → không tạo được hiệu ghép cặp.</span>,
                <span key="3"><b>Kết quả bất ngờ:</b> E của H1 (0.892) hơi CAO hơn H0 (0.883). Khác biệt không có ý nghĩa (p = 0.417) nhưng đủ để paper từ chối tuyên bố "hybrid bay thẳng hơn".</span>,
              ]}
            />

            <Formula
              tag="CT-29"
              title="Clearance nhỏ nhất (dùng BỀ MẶT, không dùng tâm)"
              code={`clearance = min trên toàn bộ đường bay của  δₜ   (clearance CÓ DẤU tới mặt AABB gần nhất)

δ > 0 : ngoài vật cản      δ = 0 : chạm mặt      δ < 0 : đã xuyên vào trong
Bán kính phồng UAV = 0
Khác với dᵢ của APF (đo tới tâm) — xem Phần 6`}
            />

            <H3>10.3 Nhóm chỉ số động học (sai phân hữu hạn)</H3>
            <Formula
              tag="CT-30, CT-31"
              title="Gia tốc và jitter lấy từ vị trí lấy mẫu"
              code={`vận tốc    ≈ Δp/Δt
accel index = mean ‖ Δ²p / Δt² ‖     (m/s²)   — đạo hàm bậc 2
jitter      = mean ‖ Δ³p / Δt³ ‖     (m/s³)   — đạo hàm bậc 3
Δt = 0.1 s ; lấy trung bình trên các bước của episode

Δ²pₜ = pₜ₊₁ − 2pₜ + pₜ₋₁        Δ³pₜ = pₜ₊₂ − 3pₜ₊₁ + 3pₜ − pₜ₋₁`}
            />
            <Callout tone="warning" title="Bốn điều các chỉ số này KHÔNG chứng minh được">
              <Bullets
                items={[
                  "Không phải khả thi về cơ cấu chấp hành (actuator feasibility) — không có giới hạn tốc độ motor hay rate limit.",
                  "Không phải công suất motor hay tiêu thụ năng lượng.",
                  "Không phải độ mượt tư thế (attitude smoothness) — mô hình point-mass không có tư thế.",
                  "Không phải độ thoải mái hay tải khí động; càng không phải bằng chứng 'bay được thật'.",
                ]}
              />
            </Callout>
            <Text size="small" tone="secondary">
              So sánh với chuẩn thực sự trong robotics: Minimum-Snap (Mellinger & Kumar 2011) tối ưu jerk/snap của
              QUỸ ĐẠO THAM CHIẾU kèm ràng buộc động lực học. Ở đây jerk chỉ là chẩn đoán trên quỹ đạo ĐÃ THỰC THI.
            </Text>

            <H3>10.4 Nhóm công cụ suy luận</H3>
            <Formula
              tag="CT-32"
              title="Cỡ hiệu ứng ghép cặp Cohen's d_z"
              code={`Δᵢ = (giá trị của H1 tại unit i) − (giá trị của H0 tại unit i) ,  i = 1..20

d_z = Δ̄ / s_Δ      (hiệu trung bình chia cho độ lệch chuẩn CỦA HIỆU)

Quy ước đọc thô: |d_z| ≈ 0.2 nhỏ · 0.5 trung bình · 0.8 lớn · > 1.5 rất lớn

  success  d_z = −0.509   (trung bình, theo hướng H1 kém hơn)
  accel    d_z = +1.07    (lớn)
  jitter   d_z = +1.78    (rất lớn — bằng chứng mạnh nhất của paper)
  steps    d_z = +0.300   (nhỏ)
  efficiency d_z = +0.156 (rất nhỏ, n = 18)
  clearance  d_z = +0.063 (gần như bằng 0)`}
            />
            <Bullets
              items={[
                <span key="1"><b>Wilcoxon signed-rank hai phía</b> trên 20 hiệu ghép cặp: phi tham số, không giả định phân phối chuẩn của hiệu — phù hợp vì steps của H1 có phân phối lệch nặng (SD 451.3).</span>,
                <span key="2"><b>d_z quan trọng hơn p</b> ở đây: với n = 20, p = 0.027 cho success đi kèm d_z chỉ −0.509 (hiệu trung bình), trong khi jitter có d_z = 1.78 (hiệu rất lớn). Paper vì thế nhấn mạnh "exact p-values and effect sizes" thay vì dán nhãn significant/không.</span>,
                <span key="3"><b>Không hiệu chỉnh đa bội:</b> 6 chỉ số thành phần, các outcome chính không được tiền đặc tả như một họ confirmatory → p-value là KHÁM PHÁ. Với Bonferroni (0.05/6 = 0.0083) thì success (p = 0.027) và accel (p = 0.006, sát ngưỡng) sẽ đổi kết luận; jitter (p {"<"} 0.001) vẫn vững. Đây là điểm nên thảo luận với sinh viên.</span>,
              ]}
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 11 ---------------- */}
        <ReportSection
          title="11. Kết quả thực nghiệm"
          description="Ba bảng số liệu chính và ba biểu đồ. Mọi con số đều tái sinh được từ ledger (69/69 claim đối soát)."
          meta="§V · results/rigorous/canonical/"
          divided
        >
          <Stack gap="container">
            <H3>11.1 Accounting kết quả tổng thể (1000 rollout mỗi cấu hình)</H3>
            <Table
              headers={["Controller", "Success", "SR (Wilson 95% CI)", "Collision", "Timeout", "Efficiency (mean ± SD, chỉ success)"]}
              rows={outcomeRows}
              density="comfortable"
              rowTone={["success", "warning", "danger"]}
            />
            <Text size="small" tone="secondary">
              Kiểm tra tính nhất quán: 1000 + 0 + 0 = 1000 · 830 + 58 + 112 = 1000 · 55 + 905 + 40 = 1000.
              Ở cấp training-run, H1 thấp hơn H0 đúng 17 điểm phần trăm (d_z = −0.509, Wilcoxon p = 0.0273, n = 20).
            </Text>

            <ChartContainer
              title="Tỉ lệ hoàn thành theo từng map (250 rollout mỗi ô)"
              description="H0 đạt 250/250 trên cả bốn map. Khoảng cách H0−H1 phụ thuộc mạnh vào layout."
              footer="Kết luận: APF không cần thiết cho mọi layout (mixed đạt trần ở cả H1), nhưng quyết định ở map random và barrier."
              caption="Nguồn: §V-B, results/rigorous/canonical/episode_audit.csv"
              ariaLabel="Success rate by map"
            >
              <BarChart
                categories={["Random", "Corridor", "Barrier", "Mixed"]}
                series={[
                  { name: "H0 Hybrid", data: [100, 100, 100, 100], tone: "success" },
                  { name: "H1 A2C-only", data: [56, 96, 80, 100], tone: "warning" },
                  { name: "H2 APF-only", data: [20, 0, 2, 0], tone: "danger" },
                ]}
                valueSuffix="%"
                height={260}
                ariaLabel="Tỉ lệ hoàn thành theo map"
                accessibilitySummary="H0 đạt 100% trên cả bốn map; H1 đạt 56% random, 96% corridor, 80% barrier, 100% mixed; H2 chỉ đạt 20% random và 2% barrier."
              />
            </ChartContainer>

            <H3>11.2 Cấu trúc thất bại — thông tin quan trọng hơn tỉ lệ thành công</H3>
            <Table
              headers={["Map", "H1 success", "H1 collision", "H1 timeout", "Cơ chế thất bại suy ra"]}
              rows={failureRows}
              density="compact"
            />
            <ChartContainer
              title="Thành phần kết cục của H1 theo map (250 rollout mỗi cột)"
              description="Cùng một tỉ lệ thành công có thể đến từ hai cơ chế thất bại hoàn toàn khác nhau."
              footer="Barrier: 0 va chạm nhưng 50 hết giờ → thiếu tiến bộ, không phải thiếu an toàn. Corridor: 100% failure là va chạm → vấn đề giảm chấn dao động."
              caption="Nguồn: §V-B, §V-D"
              ariaLabel="H1 failure composition"
            >
              <BarChart
                categories={["Random", "Corridor", "Barrier", "Mixed"]}
                series={[
                  { name: "Thành công", data: [140, 240, 200, 250], tone: "success" },
                  { name: "Va chạm", data: [48, 10, 0, 0], tone: "danger" },
                  { name: "Hết giờ", data: [62, 0, 50, 0], tone: "warning" },
                ]}
                stacked
                height={240}
                ariaLabel="Thành phần kết cục của H1"
                accessibilitySummary="Random 140 thành công, 48 va chạm, 62 hết giờ; Corridor 240 thành công, 10 va chạm; Barrier 200 thành công, 50 hết giờ; Mixed 250 thành công."
              />
            </ChartContainer>
            <Callout tone="info" title="Vì sao phân tách này đáng giá (bài học phương pháp luận)">
              <Text size="small">
                Một can thiệp chỉ giảm va chạm mà không giải quyết được sự trì trệ sẽ KHÔNG cải thiện tỉ lệ hoàn thành
                ở map barrier — và ngược lại. Nếu chỉ báo cáo "H1 đạt 83%", thông tin này mất hoàn toàn.
              </Text>
            </Callout>

            <H3>11.3 H2 (chỉ APF) — bảng đầy đủ và phần suy ra</H3>
            <Table
              headers={["Map", "Success", "Collision", "Timeout (suy ra *)"]}
              rows={h2Rows}
              density="compact"
            />
            <Text size="small" tone="tertiary">
              * Paper chỉ công bố tổng 40 timeout cho H2; cột timeout theo map ở đây suy ra từ 250 − success − collision
              (tổng = 40, khớp với paper). H2 không bao giờ thành công trên corridor và mixed.
            </Text>

            <H3>11.4 Chỉ số liên tục: mean ± SD, kèm median để chống diễn giải sai</H3>
            <Table
              headers={["Controller", "Clearance (m)", "Steps (mean ± SD)", "Steps (median)", "Jitter (m/s³)", "Accel (m/s²)"]}
              rows={continuousRows}
              density="compact"
              rowTone={["success", "warning", "danger"]}
            />
            <Grid columns={2} gap="container" minColumnWidth={280}>
              <KeyIdea term="Mean 237.8 vs median 78 của H1 — vì sao không được nói 'H0 nhanh hơn'">
                Phân phối steps của H1 là hỗn hợp ba chế độ: thành công ngắn (~78 bước), va chạm sớm, và những
                episode chạy tới trần 1507 bước (timeout). Mean bị kéo lên bởi đuôi timeout, SD = 451.3 lớn gấp đôi mean.
                So sánh mean vô điều kiện giữa hai phân phối khác hình dạng như vậy là vô nghĩa — đây chính là lý do
                khác biệt steps không được ủng hộ (p = 0.123).
              </KeyIdea>
              <KeyIdea term="Jitter của H2 thấp nhất (2.21) nhưng đây KHÔNG phải tin tốt">
                H2 có accel 0.45 m/s² và jitter 2.21 m/s³ — thấp hơn H0 hàng chục lần. Nhưng nó đi kèm 90.5% va chạm
                và 4% timeout: UAV gần như không di chuyển được hoặc chết sớm. So sánh độ mượt mà KHÔNG điều kiện
                trên việc hoàn thành nhiệm vụ sẽ đảo ngược hoàn toàn kết luận thực tiễn.
              </KeyIdea>
            </Grid>
            <Text size="small" tone="secondary">
              Về 104.4 bước của H0: tương đương 10.44 s thời gian mô phỏng, nhưng KHÔNG được đọc thành thời gian bay
              thật — point-mass nhận lệnh lực trực tiếp, dải độ cao chỉ 1 m, và không có động lực học tư thế/chấp hành
              nào ràng buộc cơ động.
            </Text>

            <H3>11.5 Suy luận ghép cặp H1 − H0 trên 20 đơn vị</H3>
            <Table
              headers={["Chỉ số", "Hiệu trung bình (H1 − H0)", "Cohen's d_z", "Wilcoxon p", "n cặp", "Kết luận của paper"]}
              rows={pairedRows}
              density="compact"
              rowTone={["success", "success", "success", "muted", "muted", "muted"]}
            />
            <ChartContainer
              title="Cỡ hiệu ứng ghép cặp d_z cho sáu chỉ số thành phần"
              description="Giá trị dương nghĩa là H1 (không có APF) kém thuận lợi hơn; riêng success rate mang dấu âm vì H1 có tỉ lệ thấp hơn."
              footer="Chỉ ba chỉ số có bằng chứng: success (d_z −0.509), acceleration (+1.07), jitter (+1.78). Ba chỉ số còn lại có d_z gần 0 và p lớn."
              caption="Nguồn: §V-C; reproducibility/tables/generated/table_paired.csv"
              ariaLabel="Paired effect sizes"
            >
              <BarChart
                categories={["Success rate", "Efficiency", "Clearance", "Steps", "Acceleration", "Jitter"]}
                series={[{ name: "Cohen's d_z (H1 − H0)", data: [-0.509, 0.156, 0.063, 0.3, 1.07, 1.78], tone: "info" }]}
                horizontal
                height={260}
                valuePrecision={2}
                ariaLabel="Cỡ hiệu ứng ghép cặp"
                accessibilitySummary="d_z: success −0.509, efficiency 0.156, clearance 0.063, steps 0.30, acceleration 1.07, jitter 1.78."
              />
            </ChartContainer>
          </Stack>
        </ReportSection>

        {/* ---------------- 12 ---------------- */}
        <ReportSection
          title="12. Diễn giải cơ chế: cái gì giải thích được, cái gì chỉ là giả thuyết"
          description="Paper phân biệt rất rõ ba mức: kết quả quan sát, giải thích cơ chế có bằng chứng, và giả thuyết cần đo thêm."
          meta="§V-D · §VI Discussion"
          divided
        >
          <Stack gap="container">
            <Table
              headers={["Quan sát", "Giải thích đề xuất", "Trạng thái bằng chứng"]}
              rows={[
                ["H0 jitter thấp hơn H1 rõ rệt (d_z = 1.78)", "Hỗn hợp lồi với λ tăng dần tới 0.55 ở vùng cuối làm dịu các thay đổi lệnh lớn của A2C khi tiếp cận đích", "GIẢ THUYẾT — chưa log tách lệnh A2C/APF nên không chứng minh được cơ chế"],
                ["H2 va chạm 90.5%", "APF kích hoạt theo khoảng cách tới TÂM trong bán kính 6 m, nên không phản ứng khi ở gần mặt một khối lớn; cộng thêm local minima kinh điển của trường thế năng", "HỢP LÝ VỀ CƠ CHẾ nhưng chưa được chứng minh bằng force-field ablation riêng"],
                ["H1 thất bại ở barrier toàn bộ là timeout", "Barrier có khe hở hình học nên không phải vấn đề xâm nhập không an toàn, mà là không duy trì đủ tiến bộ về đích", "ỦNG HỘ bởi dữ liệu (0 collision, 50 timeout)"],
                ["H1 thất bại ở corridor toàn bộ là va chạm", "Ràng buộc ngang lặp lại phơi bày lệnh dao động hoặc giảm chấn kém, dù hướng đích đơn giản", "ỦNG HỘ bởi dữ liệu (10 collision, 0 timeout)"],
                ["H1 có efficiency và clearance mean CAO hơn H0 một chút", "Không phải hybrid kém hơn, mà là thiên lệch sống sót: chỉ so trên tập con H1 đã thành công", "GIẢI THÍCH PHƯƠNG PHÁP, đã kiểm chứng bằng p = 0.417 và 0.956"],
                ["H0 đạt 100% trên mọi map", "Kênh APF cộng hình học vật cản mang lại độ tin cậy nhất quán trong giao thức đã đánh giá", "CÓ BẰNG CHỨNG trong phạm vi 4 map này; không phải bảo đảm an toàn tổng quát"],
              ]}
              density="compact"
              rowTone={["warning", "warning", "success", "success", "info", "success"]}
            />
            <DocsSection title="Lịch λ giải thích điều gì — và dừng ở đâu">
              <Text size="small">
                Tại khoảng cách danh định 335.4 m, λ bị clip xuống sàn 0.15. Khi vào trong 255 m, lịch không bị chặn
                nữa; tới 135 m nó đạt trần 0.55. Như vậy đóng góp giải tích yếu nhất ở pha đầu và mạnh nhất ở pha cuối.
                Mặt khác, lực đẩy theo tâm chỉ hoạt động trong 6 m quanh tâm vật cản — nghĩa là phần lớn thời gian hành
                trình, APF thực chất chỉ là lực hút không đổi 0.04 về phía đích. Hai facts này gợi ý rằng giá trị của
                APF nằm ở pha tiếp cận và ở các khe hẹp. Muốn khẳng định, cần log riêng <Code>aₜᴬ²ᶜ</Code> và{" "}
                <Code>aₜᴬᴾᶠ</Code> theo thời gian rồi so sánh biên độ thay đổi lệnh — việc mà paper xếp vào future work.
              </Text>
            </DocsSection>
          </Stack>
        </ReportSection>

        {/* ---------------- 13 ---------------- */}
        <ReportSection
          title="13. Threats to validity — bảng đầy đủ 12 mục"
          description="Paper có một mục Threats riêng; bảng này gộp thêm các mục từ reproducibility/docs/limitations.md."
          meta="§VII · limitations.md"
          divided
        >
          <Table headers={["Nhóm", "Mối đe dọa cụ thể", "Cách paper xử lý / hệ quả diễn giải"]} rows={threatRows} density="compact" />
        </ReportSection>

        {/* ---------------- 14 ---------------- */}
        <ReportSection
          title="14. Kết luận của paper và hướng tương lai"
          meta="§VIII Conclusion"
          divided
        >
          <Stack gap="container">
            <DocsSection title="Đúng ba câu kết luận mà dữ liệu ủng hộ">
              <Bullets
                size="body"
                items={[
                  <span key="1">H0 hoàn thành toàn bộ 1000 rollout, so với 830 của cấu hình chỉ A2C khớp ngân sách–giao thức và 55 của điều khiển chỉ APF.</span>,
                  <span key="2">Phân tích ghép cặp theo đơn vị (map × training run) ủng hộ độ tin cậy hoàn thành CAO HƠN và biến thiên quỹ đạo lấy mẫu THẤP HƠN, nhưng KHÔNG ủng hộ khác biệt về hiệu suất đường bay thành công, clearance hay độ dài episode.</span>,
                  <span key="3">Kết quả phản ánh kênh "APF + hình học vật cản" đã đánh giá, KHÔNG phải một thuật toán học mới hay một planner vượt trội nói chung.</span>,
                ]}
              />
            </DocsSection>
            <Table
              headers={["#", "Hướng tương lai (theo paper)", "Vấn đề nó giải quyết", "Chi phí ước tính"]}
              rows={[
                ["1", "Đánh giá trên map held-out", "External validity: hiện chỉ có 4 map cố định", "Thấp — chỉ cần chạy eval, không cần retrain"],
                ["2", "Cho policy quan sát vật cản tương xứng (H1b)", "Bất đối xứng thông tin — giới hạn chi phối toàn bài", "Trung bình — phải retrain, đổi observation space"],
                ["3", "APF dùng khoảng cách bề mặt thay vì tâm", "Lỗi under-repel giải thích cho H2 và có thể cải thiện H0", "Trung bình — sửa apf_action, retrain"],
                ["4", "Nhiều mức gió (kể cả no-wind = H3 đã định nghĩa)", "Tiêu đề nói 'Wind-Perturbed' nhưng chưa có can thiệp mức gió", "Thấp–trung bình — H3/H5 đã có trong manifest"],
                ["5", "Log tách lệnh A2C và APF", "Chứng minh cơ chế giảm jitter thay vì chỉ giả thuyết", "Rất thấp — chỉ thêm instrumentation khi eval"],
                ["6", "Mô hình fidelity cao hơn hoặc hardware-in-the-loop", "Khoảng cách point-mass → multirotor thật (tư thế, rotor, rate limit)", "Cao"],
              ]}
              density="compact"
            />
          </Stack>
        </ReportSection>

        {/* ---------------- 15 ---------------- */}
        <ReportSection
          title="15. Reproducibility & audit trail — phần đáng học nhất của dự án"
          description="Gói reproducibility/ là điểm khác biệt thực sự so với mặt bằng paper hội nghị: mọi con số đều tái sinh từ một ledger có checksum."
          meta="reproducibility/ · result_lock_certificate.md"
          divided
        >
          <Stack gap="container">
            <MetricsGrid
              variant="card"
              columns={4}
              items={[
                { label: "Artifact thô đã kiểm checksum", value: "182/182", description: "cộng 65 file trong gói release", tone: "success" },
                { label: "Claim đối soát với paper", value: "69/69", description: "29 exact · 40 rounding · 0 mismatch", tone: "success" },
                { label: "Test gate (unit + gate)", value: "25/25", description: "kèm smoke test trong môi trường sạch", tone: "success" },
                { label: "Quyết định release", value: "CONDITIONAL PASS", description: "do binary lớn không phân phối + retrain không bitwise", tone: "warning" },
              ]}
            />

            <Table
              headers={["Gate kiểm tra", "Kết quả", "Ý nghĩa"]}
              rows={[
                ["Artifact thô xác thực bằng SHA-256", "PASS 182/182", "Không file kết quả nào bị thay đổi âm thầm"],
                ["Mỗi dòng ledger đúng một trạng thái kết thúc", "PASS (0 vi phạm)", "Accounting đầy đủ, không rollout nào 'mất tích'"],
                ["Số rollout mỗi controller = 1000", "PASS", "Đúng cardinality thiết kế"],
                ["Mỗi ô controller × map = 250", "PASS", "Thiết kế cân bằng, không ô nào thiếu dữ liệu"],
                ["Unit ghép cặp H0/H1 chia sẻ map + training-run ID", "PASS (20 cặp thật)", "Ghép cặp hợp lệ, không phải ghép nhãn trùng"],
                ["Bảng/biểu đồ sinh ra TỪ ledger", "PASS (analysis/04)", "Không có số liệu gõ tay vào bảng"],
                ["Mọi claim số học EXACT/ROUNDING/SUPPORTED", "PASS", "Paper khớp dữ liệu tới 2 chữ số thập phân"],
                ["Không có MISMATCH / UNREPRODUCIBLE", "PASS", "Không có con số nào không tái sinh được"],
                ["Smoke test trong môi trường sạch", "PASS", "Cài đặt được từ đầu bằng Dockerfile/environment.yml"],
                ["Không có secret/key/credential trong release", "PASS", "An toàn để công khai"],
              ]}
              density="compact"
            />

            <CollapsibleSection title="Vì sao là CONDITIONAL PASS chứ không phải PASS" defaultOpen>
              <Bullets
                size="body"
                items={[
                  <span key="1"><b>Lý do (a):</b> 40 checkpoint và 4000 file quỹ đạo <Code>.npz</Code> không được phân phối trong gói (quá lớn). Người tái lập phải lấy từ research repo và đối chiếu <Code>checkpoint_sha256</Code>. Chúng chỉ cần cho việc đánh giá lại và vẽ hình minh họa — KHÔNG cần để tái sinh bất kỳ con số nào trong paper.</span>,
                  <span key="2"><b>Lý do (b):</b> huấn luyện lại từ đầu không tái lập bitwise (PyTorch không seed tường minh, không có cờ determinism). Đây là lựa chọn có ý thức và đã khai báo.</span>,
                  <span key="3"><b>Điều không bị ảnh hưởng:</b> tái lập phân tích từ <Code>data/raw/rollout_ledger.csv</Code> là CHÍNH XÁC và độc lập máy, chạy dưới 30 s với ~1 GB RAM, không cần GPU. Đánh giá lại từ checkpoint đã lưu là tất định (dung sai ≤ 1e−6 cho chỉ số liên tục).</span>,
                ]}
              />
            </CollapsibleSection>

            <CollapsibleSection title="Traceability: 21 tuyên bố trong paper đã được đối chiếu với code như thế nào (trích 10 mục tiêu biểu)" defaultOpen={false}>
              <Table
                headers={["#", "Tuyên bố trong paper", "Bằng chứng code", "Kết luận"]}
                rows={[
                  ["1", "Observation đúng 12 chiều", "DroneEnv3D._obs = hstack(state[6], goal-disp[3], wind[3]); observation_space = Box((12,))", "CONFIRMED"],
                  ["2", "A2C không thấy hình học/khoảng cách vật cản", "_obs chỉ có pos, vel, goal-displacement, wind", "CONFIRMED"],
                  ["6", "Clip theo từng thành phần, 12 N mỗi trục", "np.clip(action, −1, 1) * self.max_f với max_f = 12.0", "CONFIRMED"],
                  ["8", "Drag tác dụng lên vận tốc tương đối", "acceleration = (force − kd*(velocity − wind))/mass", "CONFIRMED"],
                  ["9", "Euler bán ẩn", "velocity += a*dt rồi x += vx*dt dùng vận tốc MỚI", "CONFIRMED"],
                  ["11", "Va chạm quét đoạn (swept)", "swept_aabb_collision(previous_pos, pos, o, radius) — phép thử slab 3 trục", "CONFIRMED"],
                  ["14", "Lực đẩy APF dùng khoảng cách tới TÂM AABB", "center = (...)/2 ; d = norm(pos − center)", "CONFIRMED (bất đối xứng với #13)"],
                  ["17", "Lịch blend tại 335.4 / 255 / 135 / 0 m", "λ = clip(1 − d/300, 0.15, 0.55) → 0.15, 0.15, 0.55, 0.55", "CONFIRMED"],
                  ["19", "Phạt độ cao bất hoạt sau clamp", "z bị clamp về [5,6] trước khi reward đọc st[2] → cả hai nhánh phạt không tới được", "CONFIRMED INACTIVE"],
                  ["20", "Công thức chân trời và giá trị danh định", "max_steps = int((D_xy/(5.0·dt))·1.8) + 300; D_xy = 335.41 → H = 1507", "CONFIRMED"],
                ]}
                density="compact"
              />
              <Text size="small" tone="tertiary">
                Bảng đầy đủ 21 mục: <Code>reproducibility/docs/implementation_traceability.md</Code>. Các kiểm tra tự động
                nằm ở <Code>tests/test_controller_semantics.py</Code>, <Code>test_dynamics_and_collision.py</Code>,{" "}
                <Code>test_reward_and_horizon.py</Code>.
              </Text>
            </CollapsibleSection>

            <Callout tone="warning" title="Cảnh báo tài liệu lỗi thời trong repo (quan trọng khi cho sinh viên tự đọc code)">
              <Bullets
                items={[
                  <span key="1"><Code>README.md</Code> ở gốc repo mô tả MÔ HÌNH CŨ: quãng đường 700 m, segment curriculum, state 6 chiều, gió cộng trực tiếp vào gia tốc, ngưỡng đến đích 2.0 m. Paper canonical dùng 300 m, observation 12 chiều, gió trong drag tương đối, ngưỡng 3 m. KHÔNG dùng README gốc để đối chiếu công thức.</span>,
                  <span key="2"><Code>README_PAPER_FINAL.md</Code> và <Code>results/rigorous/canonical/qa_status.json</Code> vẫn ghi "results pending / chưa có kết quả 5.000.000 bước" — đã lỗi thời, vì 80 thư mục <Code>steps5000000</Code> đã hoàn tất và <Code>job_full.json</Code> báo <Code>complete</Code>.</span>,
                  <span key="3">Các bản build cũ với tiêu đề khác (<Code>FirstSubmission/</Code>, <Code>final_build/</Code> "Auditable…", <Code>self_review_build/</Code>, <Code>TestFolder/</Code>) đã bị supersede — chỉ đọc để xem lịch sử, không trích dẫn.</span>,
                  <span key="4"><Code>vnict_hybrid_main_paper.md</Code> và toàn bộ <Code>Archived/</Code> được đánh dấu deprecated/noncanonical trong chính README_PAPER_FINAL.md.</span>,
                ]}
              />
            </Callout>

            <ReferencePanel title="Tệp nguồn trong repo (đường dẫn tương đối so với gốc dự án)" items={repoRefs} columns={2} />
          </Stack>
        </ReportSection>

        {/* ---------------- 16 ---------------- */}
        <ReportSection title="16. Thuật ngữ, câu hỏi ôn tập và bài học phương pháp luận" divided>
          <Stack gap="container">
            <CollapsibleSection title="Glossary Anh–Việt (17 thuật ngữ)" defaultOpen={false}>
              <Table headers={["Thuật ngữ", "Tiếng Việt / viết tắt", "Định nghĩa dùng trong paper"]} rows={glossaryRows} density="compact" />
            </CollapsibleSection>

            <CollapsibleSection title="18 câu hỏi ôn tập cho sinh viên (3 mức)" defaultOpen>
              <Stack gap="container">
                <Text size="small" tone="secondary">
                  Mức 1 kiểm tra đọc hiểu công thức. Mức 2 yêu cầu tính toán hoặc suy luận từ thiết kế. Mức 3 là câu hỏi
                  phản biện kiểu reviewer — nên dùng cho buổi seminar.
                </Text>
                <Table headers={["Mức", "Câu hỏi"]} rows={exercises} density="compact" />
              </Stack>
            </CollapsibleSection>

            <CollapsibleSection title="Bài học phương pháp luận: nên học theo gì, nên tránh gì" defaultOpen>
              <Table headers={["Loại", "Thực hành", "Vì sao quan trọng"]} rows={lessonRows} density="compact" />
            </CollapsibleSection>

            <ReferencePanel title="Tài liệu tham khảo của paper (20 nguồn)" items={refs} columns={2} />

            <Divider />

            <Stack gap="component">
              <H3>Dùng tiếp Canvas này</H3>
              <Row gap="inline" wrap>
                <SendToChatButton
                  label="Soạn đề cương seminar 90 phút từ tài liệu này"
                  variant="secondary"
                  prompt="Dựa trên tài liệu hệ thống hóa paper A2C–APF, hãy soạn đề cương seminar 90 phút cho sinh viên năm cuối CNTT: chia mốc thời gian, mục tiêu học tập mỗi phần, 3 hoạt động tương tác, và 5 câu hỏi thảo luận mức phản biện."
                />
                <SendToChatButton
                  label="Giải thích lại Phần 5 (APF) cho người mới"
                  variant="secondary"
                  prompt="Hãy giải thích lại Phần 5 về APF và cơ chế trộn λ trong paper A2C–APF cho sinh viên năm thứ ba chưa học robotics: dùng phép ẩn dụ đời thường, vẽ sơ đồ ASCII, và kèm một ví dụ số đầy đủ từng bước tính lực."
                />
                <SendToChatButton
                  label="Tạo bộ slide 20 trang"
                  variant="secondary"
                  prompt="Từ tài liệu hệ thống hóa paper A2C–APF, hãy tạo nội dung 20 slide báo cáo (tiêu đề + gạch đầu dòng + ghi chú người nói cho mỗi slide), tập trung vào câu hỏi nghiên cứu, thiết kế H0–H4, ba kết quả có bằng chứng, và bất đối xứng thông tin."
                />
              </Row>
              <Text size="small" tone="tertiary">
                Biên soạn từ bản LaTeX canonical ngày 2026-09-23. Mọi con số đối chiếu với{" "}
                <Code>reproducibility/reports/result_reconciliation.md</Code> (69/69 claim, 0 MISMATCH).
                Các giá trị đánh dấu "suy ra" là tính toán bổ sung của tài liệu này, không in trong paper.
              </Text>
            </Stack>
          </Stack>
        </ReportSection>
      </Stack>
    </ReportShell>
  );
}
