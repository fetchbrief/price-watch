# price-watch

一个自动化的多源数据抓取与 AI 报告生成工具。

## 解决什么问题？
很多人需要定期监控特定数据（比如商品价格、特定网页信息），但不想手动整理。本项目提供一个极简的框架，能自动抓取数据并利用 AI 生成结构化报告，最后推送到指定邮箱。

## 我能提供什么服务？
- 定制化数据抓取（仅限合法公开数据）
- 自动生成日报/周报（AI 分析）
- 自动化推送（邮件/其他渠道）

## 联系方式
- GitHub: @fetchbrief

## 如何运行

需要 Python 3.9+（开发环境为 3.14）。

```bash
# 1. 进入项目目录并创建虚拟环境
cd price-watch
python -m venv .venv
.venv\Scripts\activate        # Windows；macOS/Linux 用 source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥（只放进 .env，绝不提交）
#    在项目根目录新建 .env，写入一行：
#    DEEPSEEK_API_KEY=你的密钥

# 4. 抓取数据（占位数据源：httpbin.org/json，公开、无需登录）
python fetch_data.py

# 5. 抓取并生成 AI 报告
python generate_report.py
```

**失败即失败：** 抓不到数据、密钥缺失、接口报错时，脚本会直接报错退出，不会用假数据或占位文本兜底。这是刻意设计的——报告里出现的每个数字都必须来自真实抓取。