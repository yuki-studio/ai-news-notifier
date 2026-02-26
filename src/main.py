import sys
from src.config import AI_API_KEY, AI_PROVIDER, AI_MODEL, AI_BASE_URL, FEISHU_WEBHOOK
from src.utils import setup_logger
from src.fetch_rss import fetch_rss_feeds
from src.freshness_filter import filter_fresh_news
from src.deduplicate import deduplicate_news
from src.merge_news import merge_news_items
from src.scoring import score_news
from src.ranking import rank_news
from src.ai_summary import generate_summary
from src.feishu_sender import send_to_feishu

logger = setup_logger("main")

def main():
    logger.info("Starting AI News Notifier Pipeline")
    
    # Log configuration (masking sensitive data)
    masked_key = f"{AI_API_KEY[:4]}...{AI_API_KEY[-4:]}" if AI_API_KEY and len(AI_API_KEY) > 8 else "NOT_SET"
    logger.info(f"Configuration: Provider={AI_PROVIDER}, Model={AI_MODEL}, BaseURL={AI_BASE_URL}, API_KEY={masked_key}")
    logger.info(f"Feishu Webhook set: {'Yes' if FEISHU_WEBHOOK else 'No'}")

    # 1. Fetch
    news = fetch_rss_feeds()
    if not news:
        logger.info("No news fetched. Exiting.")
        return

    # 2. Filter Freshness
    fresh_news = filter_fresh_news(news)
    if not fresh_news:
        logger.info("No fresh news found. Exiting.")
        return
        
    # 3. Deduplicate
    unique_news = deduplicate_news(fresh_news)
    if not unique_news:
        logger.info("No unique news found. Exiting.")
        return

    # 4. Merge
    merged_news = merge_news_items(unique_news)
    
    # 5. Score
    scored_news = score_news(merged_news)
    
    # 6. Rank
    top_news = rank_news(scored_news)
    if not top_news:
        logger.info("No top news selected. Exiting.")
        return
        
    # 7. Generate Summaries
    logger.info(f"Generating summaries for {len(top_news)} items")
    summarized_news = []
    for item in top_news:
        try:
            summary_data = generate_summary(item)
            
            # Merge summary data with original item data
            # We want to keep the link and original sources
            final_item = {
                **summary_data,
                "links": item.get("links", []),
                "sources": item.get("sources", []),
                "original_title": item.get("title")
            }
            summarized_news.append(final_item)
        except Exception as e:
            logger.error(f"Error processing summary for item '{item.get('title')}': {e}")
            
    # 8. Send to Feishu
    if summarized_news:
        send_to_feishu(summarized_news)
    else:
        logger.warning("No summaries generated. Nothing to send.")
        
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
