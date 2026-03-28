# RagGuard

企业知识库 RAG 检索安全验证框架。针对知识库投毒、越权检索、文档篡改三类威胁，建立攻击模拟与安全控制验证流程。

## 技术栈

| 组件 | 用途 |
|------|------|
| LangChain | 文档切片、检索编排 |
| ChromaDB | 向量索引与持久化 |
| sentence-transformers | 本地文本 Embedding |

## 目录结构

```
ragguard/
├── ingestion/     文档切片、HMAC 签名、向量入库
├── retrieval/     相似度检索、置信度过滤、引用溯源
├── defense/       部门 ACL、密级控制、来源白名单
├── attacks/       攻击载荷构造与场景模拟
├── audit/         加固前后对比测试
├── report/        验证报告输出
└── pipeline.py    RAG 查询主流程
```

## 环境要求

- Python 3.10+
- 磁盘空间 ≥ 2GB（含 Embedding 模型缓存）
- 首次索引需联网下载模型（约 470MB）

## 构建

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 镜像配置

国内网络环境下，常用镜像如下。

**pip**

```bash
pip install -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn
```

| 源 | URL |
|----|-----|
| 清华大学 | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple` |

**HuggingFace 模型**

```bash
export HF_ENDPOINT=https://hf-mirror.com          # Windows PowerShell: $env:HF_ENDPOINT=...
```

项目根目录提供 `scripts/run_demo_cn.sh` / `scripts/run_demo_cn.ps1`，内置上述镜像配置。

## 运行

```bash
python -m ragguard.main --demo
```

执行流程：加载种子文档 → 建立向量索引 → 运行三项攻击场景对比测试 → 输出验证报告。

## 输出

| 输出 | 路径 |
|------|------|
| 验证报告 | `reports/RagGuard_安全验证报告.md` |
| 向量索引 | `data/chroma/<session>/` |
| 模型缓存 | 系统 HuggingFace 缓存目录 |

## 测试范围

1. **知识库投毒** — 恶意文档注入后的检索污染与敏感信息泄露
2. **越权检索** — 跨部门/外部文档的访问边界
3. **文档篡改** — HMAC 签名校验对内容变更的识别能力

## 安全控制

- HMAC-SHA256 文档块签名
- 检索相似度阈值过滤
- 部门 ACL 与文档密级策略
- 可信来源作者白名单
- 引用溯源（doc_id、片段、相似度分数）
