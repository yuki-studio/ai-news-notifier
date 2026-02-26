from difflib import SequenceMatcher
from src.utils import setup_logger
from src.config import SIMILARITY_THRESHOLD

logger = setup_logger("deduplicate")

def is_similar(title1, title2):
    """
    Check if two titles are similar using SequenceMatcher.
    """
    return SequenceMatcher(None, title1, title2).ratio() > SIMILARITY_THRESHOLD

def deduplicate_news(news_list):
    """
    Removes duplicate news items based on link and title similarity.
    """
    unique_news = []
    seen_links = set()
    seen_titles = [] # List of (title, news_item) to check similarity against
    
    logger.info(f"Starting deduplication on {len(news_list)} items")
    
    for item in news_list:
        link = item.get("link")
        title = item.get("title")
        
        # Check exact link match
        if link in seen_links:
            continue
        
        # Check title similarity
        is_duplicate = False
        for seen_title, _ in seen_titles:
            if is_similar(title, seen_title):
                is_duplicate = True
                # logger.debug(f"Duplicate title found: '{title}' similar to '{seen_title}'")
                break
        
        if is_duplicate:
            continue
            
        seen_links.add(link)
        seen_titles.append((title, item))
        unique_news.append(item)
        
    logger.info(f"Deduplication complete. Removed {len(news_list) - len(unique_news)} duplicates. Remaining: {len(unique_news)}")
    return unique_news
