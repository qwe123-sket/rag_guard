from ragguard.models import SourceDoc


def load_seed_documents() -> list[SourceDoc]:
    return [
        SourceDoc(
            doc_id="ops-manual-2024",
            title="运维值班手册",
            department="ops",
            classification="internal",
            author="platform-team",
            content=(
                "运维值班手册 v2.1\n\n"
                "1. 7x24 值班热线：400-800-1234，转分机 9 接入值班工程师。\n"
                "2. 变更窗口：每周二、周四 22:00-24:00，紧急变更需值班长审批。\n"
                "3. 故障分级：P0 15 分钟响应，P1 30 分钟，P2 下一工作日处理。\n"
                "4. 登录运维堡垒机需使用个人 UKey，禁止使用共享账号。"
            ),
        ),
        SourceDoc(
            doc_id="finance-policy-2024",
            title="费用报销管理规范",
            department="finance",
            classification="internal",
            author="finance-office",
            content=(
                "费用报销管理规范\n\n"
                "1. 单笔 5000 元以下由部门负责人审批；5000-20000 元需财务经理复核。\n"
                "2. 差旅报销须附电子发票及行程单，提交截止为费用发生后 30 日。\n"
                "3. 禁止拆分报销规避审批额度。"
            ),
        ),
        SourceDoc(
            doc_id="shared-security-2024",
            title="信息安全基线",
            department="shared",
            classification="public",
            author="security-team",
            content=(
                "信息安全基线\n\n"
                "1. 密码长度不少于 12 位，需包含大小写字母、数字及符号。\n"
                "2. 禁止在 IM、邮件正文中明文传输密钥或口令。\n"
                "3. 离职员工账号须在最后一个工作日内完成回收。"
            ),
        ),
    ]
