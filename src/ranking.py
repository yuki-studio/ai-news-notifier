from src.config import TOP_N
from src.utils import setup_logger

logger = setup_logger("ranking")

def rank_news(news_list):
    """
    Ranks news items by final_score (desc) and publish_time (desc).
    Returns the top N items.
    """
    logger.info(f"Ranking {len(news_list)} items")
    
    # Sort by final_score desc, then publish_time desc
    sorted_news = sorted(
        news_list, 
        key=lambda x: (x.get("final_score", 0), x.get("publish_time")), 
        reverse=True
    )
    
    top_news = sorted_news[:TOP_N]
    
    logger.info(f"Selected top {len(top_news)} items")
    return top_news
