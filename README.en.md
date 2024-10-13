# Product Hunt Daily Hot List - Auto Update to Feishu Bitable

[English](README.en.md) | [中文](README.md)

![License](https://img.shields.io/github/license/ViggoZ/producthunt-daily-hot) ![Python](https://img.shields.io/badge/python-3.x-blue)

Product Hunt Daily Hot is a GitHub Action-based automation tool that generates a daily list of popular products from Product Hunt and automatically updates it to multiple platforms. This project aims to help users quickly understand the most popular tech products and innovative projects of the day.

The leaderboard is automatically updated daily at 3:00 PM Beijing Time. You can view it [🌐 here](https://sxwqam5d2bh.feishu.cn/docx/S2mTdzFrToxGSjx4aAgc4fDBnjb?from=from_copylink).

## Preview

![Preview](./preview.gif)

## Main Features

- **Automated Data Retrieval**: Automatically retrieves the top 30 products from Product Hunt daily, ensuring timeliness and accuracy of information.
- **AI-Assisted Content Generation**: 
  - Uses OpenAI's GPT-4 model or Dify API to generate concise and easy-to-understand Chinese keywords
  - Provides high-quality Chinese translations of product descriptions, helping users better understand the product content
- **Multi-Platform Automatic Publishing**: 
  - Generates Markdown files containing product data, keywords, and translated descriptions, and automatically commits them to the GitHub repository
  - Supports automatic publishing to WordPress websites for easy content distribution
  - Automatically updates to Feishu Bitable, facilitating team collaboration and data analysis
- **Flexible Configuration**: 
  - Supports scheduled automatic runs through GitHub Actions
  - Also allows manual triggering of workflows to meet different usage needs
  - Scripts are easy to extend or modify, allowing adjustment of file formats or addition of extra content as needed

## Quick Start

### Prerequisites

- Python 3.x
- GitHub account and repository
- OpenAI API Key or Dify API credentials (for AI content generation)
- Product Hunt API credentials (for retrieving product data)
- WordPress website and credentials (optional, for automatic publishing)
- Feishu Bitable credentials (optional, for data updates)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/imjszhang/producthunt-daily-hot.git
cd producthunt-daily-hot
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

1. Add the following Secrets to your GitHub repository:

   - `OPENAI_API_KEY`: OpenAI API key (if using OpenAI)
   - `DIFY_API_BASE_URL`: Base URL for Dify API (if using Dify)
   - `DIFY_API_KEY`: Dify API key (if using Dify)
   - `PRODUCTHUNT_CLIENT_ID`: Product Hunt API client ID
   - `PRODUCTHUNT_CLIENT_SECRET`: Product Hunt API client secret
   - `PAT`: GitHub Personal Access Token for pushing changes to the repository
   - `WORDPRESS_URL`: WordPress website URL (optional)
   - `WORDPRESS_USERNAME`: WordPress username (optional)
   - `WORDPRESS_PASSWORD`: WordPress password (optional)
   - `FEISHU_APP_ID`: Feishu App ID (optional)
   - `FEISHU_APP_SECRET`: Feishu App Secret (optional)
   - `FEISHU_BITABLE_APP_TOKEN`: Feishu Bitable APP Token (optional)
   - `FEISHU_BITABLE_TABLE_ID`: Feishu Bitable TABLE ID (optional)

2. Configure GitHub Actions workflows:

   Workflows are defined in the `.github/workflows/` directory:
   - `generate_markdown.yml`: Generates Markdown files for Product Hunt daily hot products
   - `publish_to_wordpress.yml`: Automatically publishes Markdown files to WordPress website (optional)
   - `publish_to_feishubitable.yml`: Automatically publishes to Feishu Bitable (optional)

   You can adjust the trigger conditions and run times of these workflows as needed.

### Customization

- Modify `scripts/product_hunt_list_to_md.py` (version using OpenAI API)
- Modify `scripts/product_hunt_list_to_md_dify.py` (version using Dify API)

These files control the format and structure of the generated Markdown content and can be customized as needed.

### Usage

Once set up, GitHub Action will automatically run according to the configured time, generating and publishing daily hot product information from Product Hunt. You can also manually trigger the workflow to generate content immediately.

Generated Markdown files will be stored in the `data/` directory, named in the format `producthunt-daily-YYYY-MM-DD.md`.

## Contributing

Contributions of any form are welcome! If you have any suggestions for improvements or new feature ideas, please submit an issue or pull request.

## License

This project is open-sourced under the MIT License. For details, please refer to the [LICENSE](LICENSE) file.
