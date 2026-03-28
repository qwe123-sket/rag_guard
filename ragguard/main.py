"""RagGuard 入口：运行安全验证并输出报告。"""

from __future__ import annotations

import argparse
import sys

from ragguard.audit.runner import AuditRunner
from ragguard.report.generator import write_report


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
    args = parser.parse_args(argv)

    if args.demo or len(argv or sys.argv) == 1:
        run_demo()
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
