"""冒烟测试：只验证两件事——抓得到、失败时如实失败。

跑法：
    pytest test_smoke.py -v

需要联网（会请求 api.github.com，公开接口，无需登录）。
"""

import os
import subprocess
import sys
from pathlib import Path

from fetch_data import PLACEHOLDER_URL, fetch_json

PROJECT_ROOT = Path(__file__).resolve().parent


def test_fetch_json_gets_public_data():
    """fetch_json 能从公开接口抓到 JSON 并解析成字典。"""
    data = fetch_json(PLACEHOLDER_URL)

    assert isinstance(data, dict), f"期望 dict，实际是 {type(data).__name__}"
    assert data, "接口返回了空字典，说明没真正抓到数据"


def test_missing_api_key_exits_nonzero():
    """没有 DEEPSEEK_API_KEY 时，generate_report.py 必须以非零码退出。

    不能静默失败，也不能用占位文本兜底——这是「数据宁缺毋假」的底线。
    """
    # 把密钥置为空字符串：os.environ 里已存在这个键，
    # 所以 load_dotenv() 不会再从 .env 覆盖它，真实密钥不会被读进来。
    # 而空字符串是假值，脚本会走「密钥缺失」分支。
    env = {**os.environ, "DEEPSEEK_API_KEY": ""}

    proc = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "generate_report.py")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )

    output = proc.stdout + proc.stderr
    assert proc.returncode != 0, f"缺少密钥时应非零退出，实际返回 {proc.returncode}\n{output}"
    assert "DEEPSEEK_API_KEY" in output, f"错误信息应明确指出缺哪个变量：\n{output}"
