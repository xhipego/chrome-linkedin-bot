import streamlit as st
import feedparser
from google import genai

# Page Configuration
st.set_page_config(page_title="Chrome Market Intelligence", page_icon="⛏️", layout="wide")

st.title("⛏️ Chrome & Ferrochrome Market Intelligence")
st.write("Generate daily executive-ready LinkedIn posts from real-time commodity mining updates.")

# 1. API Key Setup
GEMINI_API_KEY = ""
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("Enter Gemini API Key", type="password")

# 2. Expanded Mining & Commodity Feeds
SOURCES = {
    "Mining Weekly (Latest)": "https://www.miningweekly.com/page/rss-feed/feed:latest-news",
    "Mining.com Feed": "https://www.mining.com/feed/",
    "Mining Weekly (Ferrous/Chrome)": "https://www.miningweekly.com/page/ferrous-metals/rss",
    "Engineering News (Freight & Logistics)": "https://www.engineeringnews.co.za/page/rss-feed/feed:latest-news",
    "Miningmx (African Mining & PGMs)": "https://www.miningmx.com/feed/",
}

# Keywords to match
PRIMARY_KEYWORDS = ["chrome", "ferrochrome", "chromium", "ug2", "lumpy ore", "smelter"]
SECONDARY_KEYWORDS = ["south africa", "transnet", "richards bay", "maputo", "port", "ferrous", "mining", "metals", "platinum"]

def fetch_chrome_news():
    news_items = []
    
    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:20]: # Expanded to scan 20 entries
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                link = entry.get("link", "")
                combined_text = f"{title} {summary}".lower()
                
                # Broadened keyword check across mining, logistics, and trading
                keywords = ["chrome", "ferrochrome", "mining", "metals", "platinum", "south africa", "port", "smelter", "freight", "transnet", "logistics"]
                
                if any(kw in combined_text for kw in keywords):
                    news_items.append(f"SOURCE: {source_name}\nTITLE: {title}\nSUMMARY: {summary[:350]}...\nLINK: {link}\n")
        except Exception:
            pass
            
    if news_items:
        return news_items[:5]
    else:
        # Emergency context if RSS feeds are completely down/empty
        return ["SOURCE: Industry General\nTITLE: Global Chrome Ore & Ferrochrome Supply Chain Market Dynamics\nSUMMARY: Ongoing logistics focus across Southern African transport corridors, port turnaround times at Richards Bay/Durban, and demand indicators from major Asian stainless steel smelters."]

def generate_linkedin_posts(raw_news):
    client = genai.Client(api_key=GEMINI_API_KEY)
    combined_context = "\n-------------------\n".join(raw_news)
    
    prompt = f"""
    You are an expert Commodity Trader specializing in Chrome Ore and Ferrochrome trading. 
    Analyze these raw mining and logistics updates gathered from the market:

    {combined_context}

    Your task is to write 2 distinct, highly professional LinkedIn post drafts aimed at attracting commodity buyers, ferrochrome smelters, and trade partners.

    Draft 1: "Market Insight & Trade Commentary"
    - Relate the provided news to chrome/ferrochrome supply dynamics, logistics corridors (South Africa/Mozambique), or pricing trends.
    - Provide 3 crisp bullet points breaking down key market implications.
    - End with trader commentary on what this means for chrome ore buyers/sellers.

    Draft 2: "Commodity Spotlight / Strategy Analysis"
    - Highlight key trade specs (e.g., 40-42% Cr concentrate, lumpy ore, South Africa/Zimbabwe exports, Chinese port inventory).
    - Explain why this market dynamic matters right now in the supply chain.

    Formatting Rules:
    - Keep tone executive, clear, and direct.
    - Avoid AI buzzwords.
    - End each post with a subtle Call To Action inviting DMs for off-take, specs, or pricing inquiries.
    """

    target_models = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3.1-flash-lite', 'gemini-2.0-flash']
    
    for model_name in target_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except Exception:
            continue
    return None

# Web UI Logic
if st.button("🚀 Generate Today's LinkedIn Posts", type="primary"):
    if not GEMINI_API_KEY:
        st.error("Please provide a valid Gemini API Key to proceed.")
    else:
        with st.spinner("Scanning market intelligence & generating insights..."):
            news = fetch_chrome_news()
            if news:
                drafts = generate_linkedin_posts(news)
                if drafts:
                    st.success("Drafts Generated Successfully!")
                    st.markdown("### 📋 Copy Your Post Below:")
                    st.code(drafts, language="markdown")
                else:
                    st.error("Could not generate drafts. Please check your API key.")
            else:
                st.warning("No articles found.")