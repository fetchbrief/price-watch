"""抓取公开汇率数据 —— 一个真实场景下的最小骨架。

场景：盯住美元兑人民币等主要币种的汇率，抓下来交给 AI 出日报。
数据源：open.er-api.com（公开、免注册、免 API key）。160+ 个币种，每小时更新。

只做三件事：带超时地取数、检查响应、失败原样抛出。
**抓不到就报错，绝不返回编造的数据。**

换场景时，改 RATES_URL 和 WATCH_SYMBOLS 即可，其余文件不用动。
"""

import logging
import sys

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 15  # 秒
DEFAULT_HEADERS = {"User-Agent": "price-watch/0.1 (+https://github.com/fetchbrief)"}

# 公开、免 key 的汇率接口，基准货币为美元。
# 来源：https://www.exchangerate-api.com/docs/free
RATES_URL = "https://open.er-api.com/v6/latest/USD"

# 只盯这几个币种 —— 报告里也只讲这几个。少即是多。
WATCH_SYMBOLS = ["CNY", "EUR", "JPY", "GBP", "HKD", "KRW"]


def fetch_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """抓取一个公开的 JSON 接口，返回解析后的字典。

    Args:
        url: 公开、无需登录的 JSON 接口地址。
        timeout: 请求超时秒数，避免卡死。

    Returns:
        解析后的 JSON（字典）。

    Raises:
        requests.RequestException: 网络错误、超时，或状态码非 2xx。
        ValueError: 响应体不是合法 JSON。
    """
    logger.info("GET %s", url)
    resp = requests.get(url, timeout=timeout, headers=DEFAULT_HEADERS)
    resp.raise_for_status()

    try:
        return resp.json()
    except ValueError as exc:
        raise ValueError(
            f"{url} 返回的不是合法 JSON（响应前 200 字符）：{resp.text[:200]!r}"
        ) from exc


def extract_rates(data: dict, symbols: list[str] = WATCH_SYMBOLS) -> dict:
    """从汇率接口的原始返回里，只取出我们要盯的那几个币种。

    刻意的瘦身：原始返回有 160+ 个币种和一堆元数据，全丢给 AI 既慢又贵、
    还容易让它扯到不相关的币种上。这里只保留真实存在、且真正关心的字段。

    Raises:
        ValueError: 接口自身报错，或缺少我们要的币种。
    """
    if data.get("result") != "success":
        raise ValueError(
            f"接口返回失败：result={data.get('result')!r} "
            f"error-type={data.get('error-type')!r}"
        )

    rates = data.get("rates")
    if not isinstance(rates, dict) or not rates:
        raise ValueError("接口没有返回 rates 字段，或该字段为空。")

    missing = [s for s in symbols if s not in rates]
    if missing:
        raise ValueError(f"接口返回里缺少这些币种：{missing}")

    return {
        "基准货币": data.get("base_code"),
        "更新时间(UTC)": data.get("time_last_update_utc"),
        "汇率": {s: rates[s] for s in symbols},
    }


def _print(result: dict) -> None:
    """在 Windows 控制台上也要能正常显示中文。"""
    if hasattr(sys.stdout, "reconfigure") and (sys.stdout.encoding or "").lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")  # Python 3.7+

    base = result["基准货币"]
    print(f"基准货币：{base}　更新时间：{result['更新时间(UTC)']}")
    print("-" * 44)
    for code, rate in result["汇率"].items():
        print(f"  1 {base} = {rate:>12.6f} {code}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        data = fetch_json(RATES_URL)
        result = extract_rates(data)
    except (requests.RequestException, ValueError) as exc:
        # 抓不到就如实失败，不用假数据兜底。
        raise SystemExit(f"抓取失败：{exc}")

    _print(result)


if __name__ == "__main__":
    main()
