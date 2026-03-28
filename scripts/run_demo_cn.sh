#!/usr/bin/env bash
# RagGuard — 国内镜像环境运行

set -euo pipefail
cd "$(dirname "$0")/.."

export HF_ENDPOINT="https://hf-mirror.com"
PIP_INDEX="https://pypi.tuna.tsinghua.edu.cn/simple"
PIP_TRUSTED="pypi.tuna.tsinghua.edu.cn"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -r requirements.txt -i "$PIP_INDEX" --trusted-host "$PIP_TRUSTED"
python -m ragguard.main --demo
