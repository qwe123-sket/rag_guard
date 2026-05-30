from pathlib import Path

from ragguard.config import settings
from ragguard.models import ScenarioAudit, SecurityAuditReport
from ragguard.retrieval.provenance import render_provenance


def render_markdown(report: SecurityAuditReport) -> str:
    scenario_pass = sum(1 for s in report.scenarios if s.defense_effective)
    tamper_ok = report.tamper_blocked
    total = len(report.scenarios) + 1
    pass_count = scenario_pass + (1 if tamper_ok else 0)

    lines = [
        "# RagGuard 安全验证报告",
        "",
        "| 字段 | 内容 |",
        "|------|------|",
        f"| 项目 | {report.project} |",
        f"| 报告日期 | {report.generated_at} |",
        f"| 文档集规模 | {report.doc_count} 篇源文档 |",
        f"| 测试场景 | {total} 项 |",
        f"| 控制措施有效率 | {pass_count}/{total} |",
        "",
        "## 1. 背景",
        "",
        "本报告记录 RagGuard 在企业内网知识库 RAG 场景下的安全验证结果。"
        "测试对象覆盖运维手册、财务规范等内部文档，"
        "验证重点为检索链路上的投毒、越权与篡改三类风险及其对应控制措施。",
        "",
        "## 2. 测试环境",
        "",
        "| 项目 | 配置 |",
        "|------|------|",
        "| 定位 | RAG 检索安全验证 |",
        "| 向量存储 | ChromaDB |",
        "| Embedding | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |",
        f"| 置信度阈值 | {settings.min_score} |",
        f"| Top-K | {settings.top_k} |",
        "",
        "## 3. 结论摘要",
        "",
        _summary_table(report),
        "",
        "## 4. 安全控制措施",
        "",
    ]

    for i, measure in enumerate(report.defense_measures, 1):
        lines.append(f"{i}. {measure}")

    lines.extend([
        "",
        "## 5. 测试用例",
        "",
    ])

    for scenario in report.scenarios:
        lines.extend(_render_scenario(scenario))

    lines.extend([
        "### 5.3 文档篡改检测",
        "",
        "| 指标 | 结果 |",
        "|------|------|",
        "| 测试方法 | 对文档块内容做单字节变更，使用原签名进行校验 |",
        f"| 校验结果 | {'签名不匹配，变更被识别' if report.tamper_blocked else '签名校验未识别变更'} |",
        f"| 判定 | {_verdict(tamper_ok)} |",
        "",
        "## 6. 基准检索记录",
        "",
        "以下为加固模式下、无攻击注入时的标准检索结果，用作对照基线。",
        "",
        f"查询：{report.normal_query.question}",
        "",
        f"响应：{report.normal_query.answer}",
        "",
    ])

    if report.normal_query.citations:
        lines.append(render_provenance(report.normal_query.citations))
        lines.append("")

    return "\n".join(lines)


def _verdict(ok: bool) -> str:
    return "符合预期" if ok else "未达预期"


def _summary_table(report: SecurityAuditReport) -> str:
    rows = [
        "| 场景 | 未加固 | 已加固 | 拦截数 | 判定 |",
        "|------|--------|--------|--------|------|",
    ]
    for s in report.scenarios:
        base = "泄露" if s.baseline_leaked else "无泄露"
        hard = "泄露" if s.hardened_leaked else "无泄露"
        rows.append(
            f"| {s.scenario} | {base} | {hard} | {s.blocked_count} | {_verdict(s.defense_effective)} |"
        )
    tamper = "变更被识别" if report.tamper_blocked else "变更未识别"
    rows.append(
        f"| 文档篡改 | — | {tamper} | — | {_verdict(report.tamper_blocked)} |"
    )
    return "\n".join(rows)


def _render_scenario(s: ScenarioAudit) -> list[str]:
    idx = {"知识库投毒": "5.1", "越权检索": "5.2"}.get(s.scenario, "5.x")
    lines = [
        f"### {idx} {s.scenario}",
        "",
        f"查询语句：{s.question}",
        "",
        f"测试目的：{s.objective}",
        "",
        "| 指标 | 未加固链路 | 加固链路 |",
        "|------|------------|----------|",
        f"| 检索命中数 | {s.baseline_hit_count} | {s.hardened_hit_count} |",
        f"| 敏感信息泄露 | {'是' if s.baseline_leaked else '否'} | {'是' if s.hardened_leaked else '否'} |",
        f"| 拦截片段数 | — | {s.blocked_count} |",
        f"| 判定 | — | {_verdict(s.defense_effective)} |",
        "",
        f"未加固链路响应：{s.baseline_answer}",
        "",
        f"加固链路响应：{s.hardened_answer}",
        "",
    ]
    if s.notes:
        lines.append("测试记录：")
        for note in s.notes:
            lines.append(f"- {note}")
        lines.append("")
    return lines


def write_report(report: SecurityAuditReport, output_dir: Path | None = None) -> Path:
    out_dir = output_dir or settings.report_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    content = render_markdown(report)
    main_path = out_dir / "RagGuard_安全验证报告.md"
    main_path.write_text(content, encoding="utf-8")
    return main_path.resolve()
