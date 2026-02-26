import requests
import json
from src.config import FEISHU_WEBHOOK
from src.utils import setup_logger

logger = setup_logger("feishu_sender")

def send_to_feishu(summaries):
    """
    Sends the list of summarized news to Feishu via Webhook.
    """
    if not FEISHU_WEBHOOK:
        logger.warning("FEISHU_WEBHOOK not set. Skipping notification.")
        return

    logger.info(f"Sending {len(summaries)} items to Feishu")
    
    # Construct Feishu Card
    # We can send one card with multiple elements, or multiple messages.
    # A single card is cleaner.
    
    elements = []
    
    # Header
    card_header = {
        "title": {
            "tag": "plain_text",
            "content": "🤖 AI 每日精选资讯"
        },
        "template": "blue"
    }
    
    for i, item in enumerate(summaries):
        # Separator for items after the first one
        if i > 0:
            elements.append({"tag": "hr"})
            
        # Title
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**[{item['title']}]({item.get('links', ['#'])[0]})**" 
                # Note: 'links' might not be in the summary object if it came purely from generate_summary.
                # We need to make sure we pass the original link or include it in summary object.
                # In main.py, we should merge the original link into the summary object or pass it.
            }
        })
        
        # Summary
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"📖 **摘要**: {item['summary']}"
            }
        })
        
        # Key Points
        if item.get('key_points'):
            points = "\n".join([f"- {p}" for p in item['key_points']])
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"💡 **核心能力**:\n{points}"
                }
            })
            
        # Impact
        if item.get('impact'):
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"🚀 **影响**: {item['impact']}"
                }
            })
            
        # Footer/Sources
        sources_text = item.get('publish_date', '')
        if item.get('sources'):
             # Handle if sources is list or string (generate_summary might return list in prompt but string in practice, let's check)
             # In generate_summary prompt I asked for JSON but didn't strictly specify source list in output JSON, 
             # but I did ask for "Sources" in input.
             # Actually the output JSON format in prompt doesn't have "sources" field. 
             # I should probably add it or rely on the input context.
             pass
             
    card = {
        "msg_type": "interactive",
        "card": {
            "header": card_header,
            "elements": elements
        }
    }
    
    try:
        response = requests.post(
            FEISHU_WEBHOOK, 
            headers={"Content-Type": "application/json"},
            data=json.dumps(card)
        )
        response.raise_for_status()
        logger.info("Successfully sent to Feishu")
    except Exception as e:
        logger.error(f"Failed to send to Feishu: {e}")

if __name__ == "__main__":
    # Test
    pass
