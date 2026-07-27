import os
import feedparser
from google import genai

# ==========================================
# 1. SETUP YOUR GEMINI API KEY
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. TOP WORKING MINING RSS FEEDS
# ==========================================
SOURCES = {
    "Mining Weekly (Latest News)": "https://www.miningweekly.com/page/rss-feed/feed:latest-news",
    "Mining.com Feed": "https://www.mining.com/feed/",
    "Commodity Africa News": "https://www.miningweekly.com/page/ferrous-metals/rss",
}

def fetch_chrome_news():
    """Fetches latest articles and filters for chrome / mining topics."""
    print("🔎 Searching feeds for Chrome & Mining updates...\n")
    news_items = []
    
    for source_name, url in SOURCES.items():
        print(f"📡 Checking {source_name}...")
        try:
            feed = feedparser.parse(url)
            count = 0
            
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                link = entry.get("link", "")
                
                # Filter for chrome or general ferrous mining keywords, or grab recent headlines
                combined_text = f"{title} {summary}".lower()
                if any(kw in combined_text for kw in ["chrome", "ferrochrome", "mining", "metals", "platinum", "south africa", "port", "smelter"]):
                    news_items.append(
                        f"SOURCE: {source_name}\nTITLE: {title}\nSUMMARY: {summary[:300]}...\nLINK: {link}\n"
                    )
                    count += 1
                    if count >= 2: # Keep top 2 matches per source
                        break
            print(f"   ↳ Found {count} relevant articles.")
        except Exception as e:
            print(f"   ⚠️ Could not fetch from {source_name}: {e}")
            
    return news_items

def generate_linkedin_posts(raw_news):
    """Passes collected news to Gemini to generate trade-focused LinkedIn posts."""
    if not raw_news:
        print("\n⚠️ No new articles matching Chrome/Mining were found right now.")
        return

    combined_context = "\n-------------------\n".join(raw_news)
    
    prompt = f"""
    You are an expert Commodity Trader specializing in Chrome Ore and Ferrochrome. 
    Analyze these raw news updates gathered today:

    {combined_context}

    Your task is to write 2 distinct, highly professional LinkedIn post drafts aimed at attracting commodity buyers, ferrochrome smelters, and trade partners.

    Draft 1: "Market Insight & Trade Commentary"
    - Focus on supply trends, price shifts, port logistics, or regional mining news.
    - Provide 3 bullet points breaking down key facts.
    - End with trader commentary on what this means for chrome ore buyers/sellers.

    Draft 2: "Commodity Spotlight / Grade Analysis"
    - Highlight key specifications (e.g., 40-42% Cr concentrate, lumpy ore, South Africa/Zimbabwe exports, Chinese port inventory).
    - Explain why this dynamic matters right now in the supply chain.

    Formatting Rules:
    - Keep tone executive, clear, and direct.
    - Avoid AI buzzwords (no "delve", "game-changer", "testament").
    - End each post with a subtle Call To Action inviting DMs for off-take, specs, or pricing inquiries.
    """

    print("\n🤖 Processing market intelligence with Gemini...\n")
    
    # Try preferred models in sequence
    # Try current active 2026 models in sequence
    target_models = [
        'gemini-3.6-flash', 
        'gemini-3.5-flash', 
        'gemini-3.1-flash-lite',
        'gemini-2.0-flash'
    ]
    
    for model_name in target_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            print(f"✅ Generated successfully using {model_name}!")
            return response.text
        except Exception as e:
            print(f"⚠️ Model {model_name} unavailable, trying next...")
            
    print("❌ Could not generate post with available models.")
    return None
if __name__ == "__main__":
    news = fetch_chrome_news()
    if news:
        linkedin_drafts = generate_linkedin_posts(news)
        
        # Add a safety check here to prevent the TypeError!
        if linkedin_drafts:
            print("\n================ YOUR LINKEDIN DRAFTS FOR TODAY ================\n")
            print(linkedin_drafts)
            
            # Save output to a local file
            with open("today_drafts.txt", "w", encoding="utf-8") as f:
                f.write(linkedin_drafts)
            print("\n✅ Success! Saved your drafts to 'today_drafts.txt'!")
        else:
            print("\n⚠️ Draft generation failed. Please check your Google AI API key quotas.")