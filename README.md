# AI News Notifier 🤖

This project is an automated AI news aggregation and notification system. It fetches news from various RSS sources (OpenAI, Google, Anthropic, etc.), filters, deduplicates, scores, and summarizes the top AI news using AI (OpenAI/DeepSeek), and then sends a daily digest to Feishu (Lark).

## Features

- **Multi-Source Fetching**: Aggregates news from 10+ authoritative AI blogs and tech media.
- **Intelligent Filtering**: Filters out old news (default 48h) and deduplicates similar articles.
- **Smart Scoring**: Ranks news based on keywords (e.g., "GPT-5", "Release"), source authority, and AI-based importance scoring.
- **AI Summarization**: Generates concise, structured summaries (Title, Summary, Key Points, Impact) using LLMs.
- **Feishu Integration**: Sends beautiful rich text cards to your Feishu/Lark group.
- **Automated**: Runs daily via GitHub Actions.

## Prerequisites

- Python 3.9+
- OpenAI API Key (or DeepSeek API Key)
- Feishu Webhook URL

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AI News Notifier"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**
   Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   - `AI_API_KEY`: Your LLM API Key.
   - `FEISHU_WEBHOOK`: Your Feishu Bot Webhook URL.
   - `AI_PROVIDER`: `openai` or `deepseek`.
   - `AI_MODEL`: e.g., `gpt-4o` or `deepseek-chat`.

4. **Run Locally**
   ```bash
   python -m src.main
   ```

## Deployment (GitHub Actions)

This project is configured to run automatically on GitHub Actions every day at 09:00 Beijing Time (01:00 UTC).

1. **Push to GitHub**
   Push this code to a new GitHub repository.

2. **Configure Secrets**
   Go to your GitHub Repository -> Settings -> Secrets and variables -> Actions -> New repository secret.
   Add the following secrets:
   - `AI_API_KEY`: Your API Key.
   - `FEISHU_WEBHOOK`: Your Feishu Webhook URL.
   - `RSS_FEEDS` (Optional): Comma-separated list of RSS URLs if you want to override defaults.

3. **Configure Variables (Optional)**
   Go to "Variables" tab in Actions settings to override defaults:
   - `FRESHNESS_HOURS`: Default `48`.
   - `AI_PROVIDER`: Default `openai`.
   - `AI_MODEL`: Default `gpt-4o`.
   - `TOP_N`: Default `5`.

4. **Manual Trigger**
   You can manually trigger the workflow from the "Actions" tab to test it immediately.

## Project Structure

- `src/fetch_rss.py`: Fetches RSS feeds.
- `src/freshness_filter.py`: Filters old news.
- `src/deduplicate.py`: Removes duplicates.
- `src/merge_news.py`: Merges similar stories.
- `src/scoring.py`: Calculates importance scores.
- `src/ranking.py`: Selects top news.
- `src/ai_summary.py`: Generates summaries using AI.
- `src/feishu_sender.py`: Sends notifications.
- `src/main.py`: Main entry point.

## License

MIT
