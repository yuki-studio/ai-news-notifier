from difflib import SequenceMatcher
from src.utils import setup_logger

logger = setup_logger("merge_news")

MERGE_SIMILARITY_THRESHOLD = 0.7

def is_similar(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio() > MERGE_SIMILARITY_THRESHOLD

def merge_news_items(news_list):
    """
    Merges news items that are about the same topic (title similarity > 70%).
    """
    merged_news = []
    
    logger.info(f"Starting merge process on {len(news_list)} items")
    
    # Sort by publish time desc so we prioritize latest as the "base"
    sorted_news = sorted(news_list, key=lambda x: x['publish_time'], reverse=True)
    
    while sorted_news:
        base_item = sorted_news.pop(0)
        
        # Initialize merged structure
        merged_item = {
            "title": base_item["title"],
            "sources": [base_item["source"]],
            "links": [base_item["link"]],
            "publish_time": base_item["publish_time"],
            "summaries": [base_item["summary"]],
            "contents": [base_item.get("content", "")],
            "original_items": [base_item] # Keep original items for reference if needed
        }
        
        # Find similar items in the remaining list
        remaining_news = []
        for item in sorted_news:
            if is_similar(base_item["title"], item["title"]):
                # Merge this item
                if item["source"] not in merged_item["sources"]:
                    merged_item["sources"].append(item["source"])
                if item["link"] not in merged_item["links"]:
                    merged_item["links"].append(item["link"])
                merged_item["summaries"].append(item["summary"])
                merged_item["contents"].append(item.get("content", ""))
                merged_item["original_items"].append(item)
                
                # Update publish time if this one is newer (though we sorted desc, so base should be newest)
                if item["publish_time"] > merged_item["publish_time"]:
                    merged_item["publish_time"] = item["publish_time"]
                    merged_item["title"] = item["title"] # Use title of newest
            else:
                remaining_news.append(item)
        
        sorted_news = remaining_news
        merged_news.append(merged_item)
        
    logger.info(f"Merge complete. Resulted in {len(merged_news)} items from {len(news_list)} original items.")
    return merged_news
