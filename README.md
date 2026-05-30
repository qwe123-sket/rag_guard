# RagGuard

RagGuard 是面向企业知识库的 RAG 检索安全验证工具，用于复现知识库投毒、越权检索和文档篡改，并对加固前后的检索结果进行对比。安全链路包含文档完整性校验、来源校验、访问控制、置信度过滤和引用溯源。

## 功能

- 文档切分、Embedding 与 ChromaDB 向量索引
- HMAC-SHA256 文档分片签名与检索时验签
- 部门 ACL、文档密级和来源白名单
- 相似度阈值过滤与 Top-K 检索
- 文档、片段、相似度和拦截原因溯源
- 安全链路与未加固链路对比
- 单次查询、交互查询和自动化验证报告

## 检索流程

```text
Document ingestion
  ├─ chunk
  ├─ sign
  └─ index
        │
        ▼
Vector retrieval
  ├─ score threshold
  ├─ signature verification
  ├─ source allowlist
  ├─ department ACL / classification
  └─ provenance
        │
        ▼
Authorized context
```

## 技术栈

- Python 3.10+
- ChromaDB
- sentence-transformers
- LangChain 文本切分与 Chroma / Embedding 适配组件

## 安装

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

首次运行会下载 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`，需要约 470 MB 模型缓存。

## 使用

### 安全验证

```bash
python -m ragguard.main --demo
```

该命令运行知识库投毒、越权检索和文档篡改三类验证，并生成 `reports/RagGuard_安全验证报告.md`。

### 单次查询

```bash
python -m ragguard.main \
  --query "运维值班电话是多少？" \
  --dept ops
```

### 交互查询

```bash
python -m ragguard.main --interactive --dept finance
```

### 对比未加固链路

```bash
python -m ragguard.main \
  --query "研发部工程师薪资是多少？" \
  --dept ops \
  --insecure
```

`--insecure` 仅用于测试对比，会关闭 ACL、验签和阈值过滤。

## 验证结果

仓库中的示例报告基于 3 篇种子文档：

| 场景 | 未加固链路 | 加固链路 | 结果 |
|------|------------|----------|------|
| 知识库投毒 | 检索到污染内容 | 污染片段被过滤 | 通过 |
| 越权检索 | 返回跨部门内容 | 未授权片段被过滤 | 通过 |
| 文档篡改 | 不校验完整性 | 签名不匹配 | 通过 |

结果记录在 [`reports/RagGuard_安全验证报告.md`](reports/RagGuard_安全验证报告.md)。该报告是本地种子数据上的功能验证，不代表生产环境检测率。

## 配置

当前参数位于 `ragguard/config.py`：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `chunk_size` | 400 | 文档分片大小 |
| `chunk_overlap` | 60 | 分片重叠 |
| `top_k` | 4 | 初始召回数量 |
| `min_score` | 0.62 | 最低相似度 |
| `embedding_model` | multilingual MiniLM | 本地 Embedding 模型 |

生产环境应通过密钥管理服务注入签名密钥，不应使用代码中的开发默认值。

## 项目结构

```text
ragguard/
├── attacks/       攻击数据与场景
├── audit/         加固前后对比
├── data/          种子文档
├── defense/       ACL、密级与来源策略
├── ingestion/     切分、签名与索引
├── report/        Markdown 报告
├── retrieval/     存储、过滤与溯源
└── pipeline.py    检索流程
```

## 安全边界

- 当前实现用于本地验证，不包含认证服务、多租户策略中心和集中密钥管理。
- ACL 和密级策略依赖调用方提供的可信用户部门信息。
- HMAC 能识别内容变更，但不能判断已签名内容是否真实可信。
- 相似度阈值需要根据企业语料重新标定。
- ChromaDB 和本地模型配置不等同于生产环境的容量、并发和可用性设计。

## License

MIT
