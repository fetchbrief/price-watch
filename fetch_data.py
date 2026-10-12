"""抓取公开 JSON 数据的最小骨架。

只演示三件事：带超时地取数、检查响应状态、失败原样抛出。
**抓不到就报错，绝不返回编造的数据。**

只用公开、无需登录的数据源。换真实数据源时，改 URL 和解析逻辑即可。
"""

import logging

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # 秒
DEFAULT_HEADERS = {"User-Agent": "price-watch/0.1 (+https://github.com/fetchbrief)"}


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


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    # 占位数据源：httpbin 的回显接口。公开、无需登录、不含任何隐私数据。
    # 换成真实数据源时，只需要替换这一行 URL。
    url = "https://httpbin.org/json"

    try:
        data = fetch_json(url)
    except (requests.RequestException, ValueError) as exc:
        # 抓不到就如实失败，不用假数据兜底。
        raise SystemExit(f"抓取失败：{exc}")

    print(f"抓取成功，顶层字段：{sorted(data.keys())}")
    print(data)


if __name__ == "__main__":
    main()
