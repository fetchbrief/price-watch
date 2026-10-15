"""调用 DeepSeek API，把抓到的数据写成一段中文报告。

规矩（不省）：
1. 密钥只从环境变量 / .env 读取，绝不落盘、绝不进日志、绝不写进 README。
2. DEEPSEEK_API_KEY 缺失，或接口调用失败 —— **直接报错退出**。
3. 绝不编造数据，也绝不返回占位文本冒充实测结果。
"""

import json
import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

SYSTEM_PROMPT = (
    "你是一个汇率日报助手。用户会给你一段 JSON，里面有基准货币、更新时间和几个币种的汇率。"
    "请用中文写一份简短的日报，要求："
    "1) 开头一句话点明基准货币和更新时间；"
    "2) 用列表逐个列出币种和汇率，数字保留 4 位小数；"
    "3) 结尾一句话说明这份数据的局限（比如：这只是某一时点的汇率，不能作为交易依据）。"
    "只描述数据里真实存在的内容。如果数据不足以得出结论，直接说明不足，"
    "不要推测、不要补全、不要编造任何数字。"
)


def _get_client() -> OpenAI:
    """从环境变量构造 DeepSeek 客户端。密钥缺失直接抛错。"""
    load_dotenv()  # 读取同目录下的 .env（如果存在）
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "环境变量 DEEPSEEK_API_KEY 未设置。\n"
            "请在项目根目录新建 .env 文件并写入：DEEPSEEK_API_KEY=你的密钥\n"
            "（.env 已在 .gitignore 中，不会被提交。）"
        )
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


def generate_report(data: Any) -> str:
    """把结构化数据交给 DeepSeek，返回生成的报告正文。

    Raises:
        RuntimeError: 密钥缺失，或接口调用失败。
    """
    client = _get_client()
    payload = json.dumps(data, ensure_ascii=False)

    logger.info("调用 DeepSeek（model=%s，输入 %d 字符）", DEEPSEEK_MODEL, len(payload))
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"以下是本次抓取到的数据：\n\n{payload}"},
            ],
            temperature=0.3,
        )
    except Exception as exc:
        # 调用失败必须让流程失败，不能吞掉错误继续往下走。
        raise RuntimeError(f"DeepSeek API 调用失败：{exc}") from exc

    content = resp.choices[0].message.content
    if not content:
        raise RuntimeError("DeepSeek 返回了空内容，已中止（不编造报告）。")
    return content


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 延迟 import，避免只想要报告函数时也触发网络请求。
    from fetch_data import RATES_URL, extract_rates, fetch_json

    try:
        # 先校验配置再联网：没配密钥就没必要发请求，也让失败原因一眼可见。
        _get_client()

        data = fetch_json(RATES_URL)
        report = generate_report(extract_rates(data))
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"生成报告失败：{exc}")

    if hasattr(sys.stdout, "reconfigure") and (sys.stdout.encoding or "").lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")  # Python 3.7+

    print("\n===== 报告 =====\n")
    print(report)


if __name__ == "__main__":
    main()
