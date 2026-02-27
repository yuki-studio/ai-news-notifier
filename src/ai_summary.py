import json
import os
from openai import OpenAI
from src.config import AI_API_KEY, AI_MODEL, AI_PROVIDER, AI_BASE_URL
from src.utils import setup_logger

logger = setup_logger("ai_summary")

client = None
if AI_API_KEY:
    if AI_BASE_URL:
        client = OpenAI(api_key=AI_API_KEY, base_url=AI_BASE_URL)
    elif AI_PROVIDER == "deepseek":
        client = OpenAI(api_key=AI_API_KEY, base_url="https://api.deepseek.com")
    else:
        client = OpenAI(api_key=AI_API_KEY)
else:
    logger.warning("AI_API_KEY not set. AI features will be disabled or mocked.")

def get_ai_score(news_item):
    """
    Asks AI to score the importance of the news item (0-100).
    """
    if not client:
        return 50 # Default if no API key
        
    title = news_item.get("title", "")
    summary = " ".join(news_item.get("summaries", []))[:1000] # Truncate to save tokens
    
    prompt = f"""
    Give this AI news item an importance score (0-100).
    Consider: Industry Impact, Technical Breakthrough, Company Influence.
    Return ONLY the number.
    
    Title: {title}
    Summary: {summary}
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are an AI news analyst. Output only a number between 0 and 100."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )
        content = response.choices[0].message.content.strip()
        # Extract number
        import re
        match = re.search(r'\d+', content)
        if match:
            return int(match.group())
        return 50
    except Exception as e:
        logger.error(f"Error getting AI score: {e}")
        # Log response body if available for debugging
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"API Response: {e.response.text}")
        return 50

def generate_summary(news_item):
    """
    Generates a structured summary for the news item using AI.
    Returns a dictionary with title, summary, key_points, impact, etc.
    """
    if not client:
        return {
            "title": news_item.get("title"),
            "summary": "AI API Key missing. " + news_item.get("summaries", [""])[0],
            "key_points": ["API Key missing"],
            "impact": "Unknown",
            "publish_date": news_item.get("publish_time").strftime("%Y-%m-%d")
        }
        
    title = news_item.get("title", "")
    summaries = "\n".join(news_item.get("summaries", []))
    sources = ", ".join(news_item.get("sources", []))
    
    prompt = f"""
    你是AI行业资深分析师，正在为科技高管和开发者撰写每日行业简报。
    你的任务是从输入的AI新闻中提炼出最有价值、最硬核的信息，拒绝空洞的套话。
    
    输入新闻:
    Title: {title}
    Sources: {sources}
    Content Summaries: {summaries}

    输出JSON:
    {{
        "title":"",
        "summary":"",
        "source_name":"",
        "url":""
    }}
    
    要求:
    
    1. title: <= 30字，必须包含公司名和产品名/技术名。必须使用中文。
    
    2. summary: 
       - 80-120字。
       - 必须是一段连贯的文字，禁止分段。
       - 写作风格：客观、专业、高密度、新闻体。
       - 必须包含：
         * 【主体】哪家公司/机构发布了什么？
         * 【核心特性】相比前代或竞品，最大的技术突破/性能提升是什么？（如有具体参数，必须保留，如"上下文窗口提升至1M"、"推理成本降低50%"）
         * 【应用/影响】对开发者或行业意味着什么？
       - 拒绝：
         * 拒绝"旨在解决..."、"有望..."等虚词。
         * 拒绝"引发了广泛关注"、"具有里程碑意义"等主观评价。
         * 拒绝"该框架..."、"这项技术..."等指代不清的开头，直接说产品名。
    
    3. source_name: 来源名称（如 OpenAI Blog, TechCrunch）。
    
    4. url: 原文链接。
    
    规则:
    - 必须使用中文。
    - 必须保留关键技术参数（如参数量、分数、价格、倍数）。
    """
    
    try:
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI news assistant. Respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
             logger.error(f"API Response: {e.response.text}")
        return {
            "title": title,
            "summary": "Failed to generate summary.",
            "source_name": "Unknown",
            "url": ""
        }
