import requests
import json
from src.config import FEISHU_WEBHOOK
from src.utils import setup_logger

from datetime import datetime

logger = setup_logger("feishu_sender")

def send_to_feishu(summaries):
    """
    Sends the list of summarized news to Feishu via Webhook.
    """
    if not FEISHU_WEBHOOK:
        logger.warning("FEISHU_WEBHOOK not set. Skipping notification.")
        return

    logger.info(f"Sending {len(summaries)} items to Feishu")
    
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Header
    card_header = {
        "title": {
            "tag": "plain_text",
            "content": f"🤖 AI行业快讯 | {current_date}"
        },
        "template": "blue"
    }
    
    elements = []
    
    for i, item in enumerate(summaries):
        # Separator for items after the first one
        if i > 0:
            elements.append({"tag": "hr"})
            
        # Title with Emoji number
        emoji_num = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][i] if i < 5 else f"{i+1}."
        
        # Ensure we have a valid URL. 
        # Priority: URL from AI summary -> URL from original item -> '#'
        url = item.get('url')
        if not url or url == "":
            links = item.get('links', [])
            if links:
                url = links[0]
            else:
                url = "#"

        source_name = item.get('source_name', 'Unknown Source')

        # Combined Text Block
        # 1. Title
        # 2. Summary
        # 3. Source Link
        content = f"**{emoji_num} {item['title']}**\n\n{item['summary']}\n\n来源：[{source_name}]({url})"

        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": content
            }
        })

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
        
        # Check for Feishu specific error codes in body even if HTTP 200
        res_json = response.json()
        if res_json.get("code") and res_json.get("code") != 0:
            logger.error(f"Feishu API Error: {res_json}")
        else:
            logger.info("Successfully sent to Feishu")
            
    except Exception as e:
        logger.error(f"Failed to send to Feishu: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"Feishu Response: {e.response.text}")

if __name__ == "__main__":
    # Test
    pass
