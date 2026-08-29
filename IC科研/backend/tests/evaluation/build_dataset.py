"""Build the deterministic 100-question Digital IC evaluation set."""

import json
from pathlib import Path


QUESTIONS: dict[str, list[tuple[str, list[str]]]] = {
    "RTL": [
        ("组合逻辑 always_comb 中出现 latch 的根因是什么？", ["incomplete assignment", "default assignment", "latch inference"]),
        ("SystemVerilog 中阻塞赋值与非阻塞赋值应如何选择？", ["scheduling semantics", "combinational vs sequential", "race avoidance"]),
        ("参数化仲裁器 RTL 如何避免优先级编码错误？", ["parameterization", "priority", "corner cases"]),
        ("ready/valid 接口如何实现无气泡流水传输？", ["handshake rule", "backpressure", "throughput"]),
        ("如何编码一个可综合的 one-hot 状态机？", ["state encoding", "default recovery", "synthesis"]),
        ("RTL 中有符号与无符号混合运算有哪些风险？", ["width extension", "signedness", "casting"]),
        ("可变位宽移位器怎样避免综合面积异常？", ["barrel shifter", "width bound", "area trade-off"]),
        ("跨模块参数与 package 类型应怎样组织？", ["package", "type consistency", "compile order"]),
        ("计数器溢出行为如何在 RTL 和规格中对齐？", ["overflow semantics", "width", "assertion"]),
        ("为什么不应在普通 RTL 中使用内部生成时钟？", ["clock enable", "clock tree", "timing analysis"]),
    ],
    "CDC": [
        ("单比特异步电平信号如何安全跨时钟域？", ["2FF synchronizer", "single-bit level condition", "MTBF"]),
        ("窄脉冲从快时钟域进入慢时钟域如何防止丢失？", ["pulse stretching", "toggle synchronizer", "handshake"]),
        ("多比特数据总线为什么不能逐位使用 2FF？", ["data coherency", "skew", "handshake or FIFO"]),
        ("异步 FIFO 的 Gray 指针为什么只改变一位？", ["Gray code", "pointer synchronization", "full empty"]),
        ("CDC reconvergence 会产生什么风险？", ["independent latency", "reconvergence", "structural CDC"]),
        ("同步器前存在组合逻辑为什么危险？", ["glitch", "source registration", "metastability rate"]),
        ("2FF 同步器级数应如何根据 MTBF 选择？", ["settling time", "clock frequency", "data toggle rate"]),
        ("相关时钟跨域何时仍应按异步 CDC 处理？", ["provable phase relation", "different PLL", "constraints"]),
        ("CDC waiver 需要记录哪些证据？", ["topology", "mode", "review owner"]),
        ("如何验证异步 FIFO 的复位后首次传输？", ["reset convergence", "pointer state", "assertion"]),
    ],
    "RDC": [
        ("异步复位释放为何会产生 RDC 风险？", ["recovery removal", "reset synchronizer", "deassertion"]),
        ("多个复位域之间的数据交互如何检查？", ["reset domains", "isolation", "structural RDC"]),
        ("复位同步器为什么通常异步置位同步释放？", ["asynchronous assertion", "synchronous deassertion", "latency"]),
        ("复位重汇聚会造成什么功能问题？", ["different release cycles", "reconvergence", "assertions"]),
        ("软件复位与硬件复位叠加时如何避免毛刺？", ["reset combining", "glitch-free logic", "priority"]),
        ("部分模块不复位时如何证明启动状态安全？", ["initialization protocol", "X propagation", "formal proof"]),
        ("低功耗域恢复供电后的复位顺序如何验证？", ["power sequence", "isolation", "reset release"]),
        ("RDC 静态分析中的 waiver 如何签核？", ["structural path", "functional condition", "review"]),
        ("测试模式切换复位源时有哪些 RDC 风险？", ["test mode", "reset mux", "glitch"]),
        ("复位脉宽不足会在芯片中导致什么后果？", ["minimum pulse width", "partial reset", "timing check"]),
    ],
    "STA": [
        ("setup violation 应按什么顺序定位和修复？", ["path validity", "data delay", "clock uncertainty"]),
        ("hold violation 为什么不能简单降低时钟频率解决？", ["same-edge check", "minimum delay", "buffer insertion"]),
        ("set_false_path 与 set_clock_groups 有什么适用差异？", ["exception scope", "asynchronous clocks", "coverage"]),
        ("multicycle path 为什么必须同时考虑 hold 约束？", ["setup shift", "hold adjustment", "functional intent"]),
        ("input delay 与 output delay 应如何从板级接口推导？", ["external timing", "virtual clock", "margin"]),
        ("时钟不确定度包含哪些成分？", ["jitter", "skew", "margin"]),
        ("generated clock 定义错误会如何污染 STA？", ["waveform", "source", "clock propagation"]),
        ("OCV/AOCV/POCV 的核心差异是什么？", ["variation model", "path depth", "statistical derate"]),
        ("时序例外如何做覆盖率与合理性审查？", ["exception coverage", "unconstrained path", "audit"]),
        ("跨层次约束在综合和 P&R 间如何保持一致？", ["constraint ownership", "object names", "signoff parity"]),
    ],
    "SYNTHESIS": [
        ("综合后面积突然增加应如何定位 RTL 根因？", ["report comparison", "inference", "resource sharing"]),
        ("为什么动态循环边界可能不可综合？", ["static elaboration", "bounded loop", "hardware replication"]),
        ("RAM 推断失败时应检查哪些编码条件？", ["template", "read write mode", "vendor inference"]),
        ("综合中的 retiming 会怎样影响验证？", ["register movement", "equivalence checking", "constraints"]),
        ("dont_touch 过度使用会造成什么问题？", ["optimization barrier", "timing", "area"]),
        ("时钟门控应由 RTL 推断还是实例化 ICG？", ["flow ownership", "library cell", "verification"]),
        ("不同 case 语句写法如何影响综合结果？", ["priority", "parallel", "unique case"]),
        ("算术表达式位宽如何影响乘法器面积？", ["operand width", "signedness", "truncation"]),
        ("综合约束缺失会导致哪些假优化？", ["clock definition", "I/O delay", "timing-driven optimization"]),
        ("如何用逻辑等价检查保护 RTL 到网表转换？", ["LEC", "mapping", "black box"]),
    ],
    "VERIFICATION": [
        ("UVM scoreboard 应比较事务还是逐周期信号？", ["abstraction level", "ordering", "predictor"]),
        ("功能覆盖率达到 100% 为什么仍不能说明验证完成？", ["coverage model quality", "assertions", "bug escape"]),
        ("SVA 中 overlapped 与 non-overlapped implication 如何选择？", ["sampling cycle", "|->", "|=>"]),
        ("如何验证 APB wait-state 与错误响应组合？", ["protocol timing", "PREADY", "PSLVERR"]),
        ("约束随机测试出现不可解约束时如何调试？", ["constraint isolation", "solver diagnostics", "bias"]),
        ("UVM objection 使用错误为什么会造成测试挂起？", ["phase lifecycle", "raise drop", "drain time"]),
        ("参考模型与 DUT 同源实现有什么验证风险？", ["common-mode bug", "independent model", "specification"]),
        ("X propagation 测试应覆盖哪些场景？", ["initialization", "power reset", "control corruption"]),
        ("回归测试失败如何自动最小化复现条件？", ["seed", "configuration capture", "test reduction"]),
        ("形式验证与仿真如何划分验证目标？", ["state space", "end-to-end scenarios", "assumptions"]),
    ],
    "LOW_POWER": [
        ("时钟门控如何避免产生毛刺时钟？", ["ICG latch", "enable stability", "clock gating check"]),
        ("power gating 中 isolation 应在何时开启？", ["power sequence", "clamp", "domain boundary"]),
        ("retention register 的保存恢复协议如何验证？", ["save restore", "retention supply", "state comparison"]),
        ("UPF 中 supply set 与 power domain 如何关联？", ["power intent", "supply network", "domain"]),
        ("电平转换器方向如何由电压域决定？", ["voltage crossing", "level shifter", "placement"]),
        ("动态功耗的主要 RTL 驱动因素有哪些？", ["activity factor", "capacitance", "frequency"]),
        ("多电压模式下 STA 应如何组织分析场景？", ["MMMC", "voltage corner", "mode"]),
        ("低功耗仿真中的 corruption semantics 是什么？", ["power state", "X corruption", "isolation"]),
        ("clock gating coverage 应怎样定义？", ["enable scenarios", "gated clock activity", "functional coverage"]),
        ("低功耗设计中 always-on 逻辑如何识别？", ["AON supply", "control path", "power sequence"]),
    ],
    "DFT": [
        ("scan chain 插入会对功能时序造成哪些影响？", ["scan mux", "timing overhead", "reorder"]),
        ("stuck-at 与 transition fault 模型有什么区别？", ["fault model", "at-speed", "coverage"]),
        ("ATPG coverage 低时应如何分类未检测故障？", ["untestable", "aborted", "constraints"]),
        ("多时钟 scan shift 如何避免时钟冲突？", ["lockup latch", "clock domains", "shift protocol"]),
        ("MBIST 为什么需要 March algorithm？", ["memory fault", "operation sequence", "coverage"]),
        ("测试点插入如何权衡覆盖率与 PPA？", ["control observe points", "coverage gain", "overhead"]),
        ("X-bounding 为什么会影响 scan diagnosis？", ["unknown source", "masking", "diagnosis resolution"]),
        ("compression architecture 中 aliasing 风险如何评估？", ["compactor", "signature", "probability"]),
        ("DFT 模式约束应如何进入 STA？", ["test clocks", "case analysis", "test mode"]),
        ("boundary scan 与内部 scan 的目标有何不同？", ["board interconnect", "internal logic", "JTAG"]),
    ],
    "PHYSICAL_DESIGN": [
        ("宏单元 floorplan 如何减少拥塞与长连线？", ["macro placement", "channels", "connectivity"]),
        ("时钟树综合后 skew 过大应如何定位？", ["clock topology", "latency", "variation"]),
        ("IR drop 问题如何区分静态与动态成因？", ["power grid", "activity", "decap"]),
        ("routing congestion 为什么可能在 placement 早期预测？", ["density", "pin access", "global routing"]),
        ("setup 修复与 hold 修复在 ECO 中有什么冲突？", ["delay trade-off", "path sharing", "corner"]),
        ("天线效应如何在布线阶段修复？", ["antenna ratio", "diode", "layer hopping"]),
        ("为什么高扇出网需要专门综合？", ["fanout", "buffer tree", "transition"]),
        ("多角多模签核如何控制场景数量？", ["scenario reduction", "coverage", "correlation"]),
        ("串扰如何同时影响 setup 与 hold？", ["coupling", "delta delay", "aggressor alignment"]),
        ("物理感知综合能解决哪些传统综合盲点？", ["wire delay", "congestion", "placement estimate"]),
    ],
    "ARCHITECTURE": [
        ("五级流水线的数据冒险有哪些处理方案？", ["forwarding", "stall", "dependency"]),
        ("片上总线仲裁应如何权衡公平性与延迟？", ["arbitration", "QoS", "starvation"]),
        ("cache coherence 目录协议的扩展性来自哪里？", ["directory", "sharer tracking", "traffic"]),
        ("异步 FIFO 深度如何根据突发流量估算？", ["rate mismatch", "burst", "latency"]),
        ("NoC 虚通道如何缓解 head-of-line blocking？", ["virtual channel", "buffer", "routing"]),
        ("流水线加深对频率、功耗和分支代价有何影响？", ["frequency", "register power", "mispredict penalty"]),
        ("AXI outstanding transaction 数量如何确定？", ["latency hiding", "ID space", "buffering"]),
        ("硬件加速器的双缓冲何时有效？", ["compute transfer overlap", "bandwidth", "buffer size"]),
        ("中断架构如何避免高负载下的 livelock？", ["priority", "masking", "rate control"]),
        ("SoC reset and boot 架构应定义哪些依赖关系？", ["reset tree", "clock power dependency", "boot order"]),
    ],
}

SOURCE_HINTS = {
    "RTL": ["IEEE SystemVerilog standard", "synthesis tool user guide"],
    "CDC": ["vendor CDC methodology", "static CDC tool report"],
    "RDC": ["vendor RDC methodology", "library recovery/removal data"],
    "STA": ["timing signoff tool user guide", "Liberty timing data"],
    "SYNTHESIS": ["synthesis tool user guide", "technology library guide"],
    "VERIFICATION": ["IEEE SystemVerilog standard", "UVM standard"],
    "LOW_POWER": ["IEEE 1801 UPF standard", "low-power tool methodology"],
    "DFT": ["DFT tool user guide", "test methodology reference"],
    "PHYSICAL_DESIGN": ["place-and-route tool guide", "foundry signoff rule deck"],
    "ARCHITECTURE": ["architecture specification", "measured workload evidence"],
}


def build() -> list[dict[str, object]]:
    records = []
    for category, questions in QUESTIONS.items():
        for question, key_points in questions:
            records.append(
                {
                    "question": question,
                    "category": category,
                    "expected_key_points": key_points,
                    "forbidden_errors": [
                        "invented citation or DOI",
                        "unqualified universal recommendation",
                        "missing applicability condition",
                    ],
                    "recommended_sources": SOURCE_HINTS[category],
                }
            )
    assert len(records) == 100
    return records


if __name__ == "__main__":
    target = Path(__file__).with_name("ic_questions.json")
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(build())} questions to {target}")

