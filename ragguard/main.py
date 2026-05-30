"""RagGuard 入口：运行安全验证并输出报告。"""

from __future__ import annotations

import argparse
import sys

from ragguard.audit.runner import AuditRunner
from ragguard.data.seed import load_seed_documents
from ragguard.pipeline import SecureRAGPipeline
from ragguard.report.generator import write_report


def run_query(
    question: str,
    *,
    user_dept: str = "ops",
    secure: bool = True,
    top_k: int | None = None,
) -> None:
    pipe = SecureRAGPipeline()
    try:
        pipe.bootstrap(load_seed_documents())
        result = pipe.query(
            question,
            user_dept=user_dept,
            top_k=top_k,
            secure=secure,
        )
        print(pipe.explain(result))
    finally:
        pipe.close()


def run_interactive(
    *,
    user_dept: str = "ops",
    secure: bool = True,
    top_k: int | None = None,
) -> None:
    pipe = SecureRAGPipeline()
    try:
        print("正在加载种子文档并建立索引（首次需下载 Embedding 模型）…")
        pipe.bootstrap(load_seed_documents())
        mode = "加固链路" if secure else "裸检索"
        print(f"RagGuard 交互模式 [{mode}] 部门={user_dept}，输入问题后回车；空行或 quit 退出\n")
        while True:
            try:
                question = input("Q> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not question or question.lower() in {"quit", "exit", "q"}:
                break
            result = pipe.query(
                question,
                user_dept=user_dept,
                top_k=top_k,
                secure=secure,
            )
            print(pipe.explain(result))
            print()
    finally:
        pipe.close()


def run_demo() -> None:
    report = AuditRunner().run()
    path = write_report(report)

    passed = sum(s.defense_effective for s in report.scenarios) + (
        1 if report.tamper_blocked else 0
    )
    total = len(report.scenarios) + 1

    print(f"RagGuard 安全验证完成  {passed}/{total}")
    for s in report.scenarios:
        status = "符合预期" if s.defense_effective else "未达预期"
        print(f"  {s.scenario}\t{status}\t拦截 {s.blocked_count}")
    tamper = "符合预期" if report.tamper_blocked else "未达预期"
    print(f"  文档篡改检测\t{tamper}")
    print(f"报告: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ragguard")
    parser.add_argument("--demo", action="store_true", help="运行安全验证")
    parser.add_argument("-q", "--query", metavar="TEXT", help="单次检索问答")
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="交互模式，可连续输入问题",
    )
    parser.add_argument(
        "--dept",
        default="ops",
        choices=["ops", "finance", "hr"],
        help="模拟用户部门（默认 ops）",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="关闭 ACL/验签/阈值，对比裸 RAG",
    )
    parser.add_argument("--top-k", type=int, default=None, help="检索条数")
    args = parser.parse_args(argv)

    if args.interactive:
        run_interactive(
            user_dept=args.dept,
            secure=not args.insecure,
            top_k=args.top_k,
        )
        return 0

    if args.query:
        run_query(
            args.query,
            user_dept=args.dept,
            secure=not args.insecure,
            top_k=args.top_k,
        )
        return 0

    if args.demo or len(argv or sys.argv) == 1:
        run_demo()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
