# Product Hunt 每日中文热榜 - 自动更新到飞书多维表格

[English](README.en.md) | [中文](README.md)

![License](https://img.shields.io/github/license/ViggoZ/producthunt-daily-hot) ![Python](https://img.shields.io/badge/python-3.x-blue)

Product Hunt 每日热榜是一个基于 GitHub Action 的自动化工具,用于生成 Product Hunt 上的热门产品榜单,并自动更新到多个平台。该项目旨在帮助用户快速了解每日最热门的科技产品和创新项目。

榜单会在每天下午3点自动更新，可以在 [🌐 这里查看](https://sxwqam5d2bh.feishu.cn/docx/S2mTdzFrToxGSjx4aAgc4fDBnjb?from=from_copylink)。

## 预览

![Preview](./preview.gif)

## 主要功能

- **自动获取数据**: 每天自动获取 Product Hunt Top 30 产品数据,确保信息的及时性和准确性。
- **AI 辅助内容生成**: 
  - 使用 OpenAI 的 GPT-4 模型或 Dify API 生成简洁易懂的中文关键词
  - 对产品描述进行高质量的中文翻译,帮助用户更好地理解产品内容
- **多平台自动发布**: 
  - 生成包含产品数据、关键词和翻译描述的 Markdown 文件,并自动提交到 GitHub 仓库
  - 支持自动发布到 WordPress 网站,方便进行内容分发
  - 自动更新到飞书多维表格,便于团队协作和数据分析
- **灵活配置**: 
  - 支持通过 GitHub Actions 进行定时自动运行
  - 也可以手动触发工作流,满足不同的使用需求
  - 脚本易于扩展或修改,可以根据需要调整文件格式或添加额外内容

## 快速开始

### 前置条件

- Python 3.x
- GitHub 账户及仓库
- OpenAI API Key 或 Dify API 凭证 (用于AI内容生成)
- Product Hunt API 凭证 (用于获取产品数据)
- WordPress 网站及凭证 (可选,用于自动发布)
- 飞书多维表格凭证 (可选,用于数据更新)

### 安装

1. 克隆仓库:

```bash
git clone https://github.com/imjszhang/producthunt-daily-hot.git
cd producthunt-daily-hot
```

2. 安装 Python 依赖:

```bash
pip install -r requirements.txt
```

### 配置

1. 在 GitHub 仓库中添加以下 Secrets:

   - `OPENAI_API_KEY`: OpenAI API 密钥 (如果使用OpenAI)
   - `DIFY_API_BASE_URL`: Dify API 的基础 URL (如果使用Dify)
   - `DIFY_API_KEY`: Dify API 密钥 (如果使用Dify)
   - `PRODUCTHUNT_CLIENT_ID`: Product Hunt API 客户端 ID
   - `PRODUCTHUNT_CLIENT_SECRET`: Product Hunt API 客户端密钥
   - `PAT`: 用于推送更改到仓库的 GitHub 个人访问令牌
   - `WORDPRESS_URL`: WordPress 网站 URL (可选)
   - `WORDPRESS_USERNAME`: WordPress 用户名 (可选)
   - `WORDPRESS_PASSWORD`: WordPress 密码 (可选)
   - `FEISHU_APP_ID`: 飞书应用的 App ID (可选)
   - `FEISHU_APP_SECRET`: 飞书应用的 Secret (可选)
   - `FEISHU_BITABLE_APP_TOKEN`: 飞书多维表格的 APP Token (可选)
   - `FEISHU_BITABLE_TABLE_ID`: 飞书多维表格的 TABLE ID (可选)

2. 配置 GitHub Actions 工作流:

   工作流定义在 `.github/workflows/` 目录中:
   - `generate_markdown.yml`: 生成 Product Hunt 每日热门产品的 Markdown 文件
   - `publish_to_wordpress.yml`: 自动发布 Markdown 文件到 WordPress 网站 (可选)
   - `publish_to_feishubitable.yml`: 自动发布到飞书多维表格 (可选)

   可以根据需要调整这些工作流的触发条件和运行时间。

### 自定义

- 修改 `scripts/product_hunt_list_to_md.py` (使用 OpenAI API 的版本)
- 修改 `scripts/product_hunt_list_to_md_dify.py` (使用 Dify API 的版本)

这些文件控制了生成的 Markdown 内容的格式和结构,可以根据需要进行自定义。

### 使用

设置完成后,GitHub Action 将根据配置的时间自动运行,生成并发布 Product Hunt 每日热门产品信息。您也可以手动触发工作流来立即生成内容。

生成的 Markdown 文件将存储在 `data/` 目录下,以 `producthunt-daily-YYYY-MM-DD.md` 的格式命名。

## 贡献

欢迎任何形式的贡献！如果您有任何改进建议或新功能想法,请提交 issue 或 pull request。

## 许可证

本项目基于 MIT 许可证开源。详情请参阅 [LICENSE](LICENSE) 文件。
