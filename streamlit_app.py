import streamlit as st
import feedparser
from google import genai

# Page Configuration
st.set_page_config(page_title="Chrome Market Post Generator", page_icon="⛏️", layout="wide")

st.title("⛏️ Chrome & Ferrochrome Market Intelligence")
st.write("Generate daily executive-ready LinkedIn posts from real-time commodity mining updates.")

# 1. API Key Setup (Pulling safely from Streamlit Secrets or Manual Input)
GEMINI_API_KEY = ""

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Fallback input field if secrets are not set
if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("Enter Gemini API Key", type="password")
# Fallback if secret isn't configured yet
if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.sidebar.text_input("Enter Gemini API Key", type="password")

# 2. News Sources
SOURCES = {
    "Mining Weekly (Latest News)": "https://www.miningweekly.com/page/rss-feed/feed:latest-news",
    "Mining.com Feed": "https://www.mining.com/feed/",
    "Commodity Africa News": "https://www.miningweekly.com/page/ferrous-metals/rss",
}

def fetch_chrome_news():
    news_items = []
    for source_name, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                link = entry.get("link", "")
                
                combined_text = f"{title} {summary}".lower()
                if any(kw in combined_text for kw in ["chrome", "ferrochrome", "mining", "metals", "platinum", "south africa", "port", "smelter"]):
                    news_items.append(f"SOURCE: {source_name}\nTITLE: {title}\nSUMMARY: {summary[:300]}...\nLINK: {link}\n")
                    count += 1
                    if count >= 2:
                        break
        except Exception:
            pass
    return news_items

def generate_linkedin_posts(raw_news):
    client = genai.Client(api_key=GEMINI_API_KEY)
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
        with st.spinner("Fetching latest news & generating trade insights..."):
            news = fetch_chrome_news()
            if news:
                drafts = generate_linkedin_posts(news)
                if drafts:
                    st.success("Drafts Generated Successfully!")
                    st.markdown("### 📋 Copy Your Post Below:")
                    st.code(drafts, language="markdown")
                else:
                    st.error("Could not generate drafts. Please check your API quota or key.")
            else:
                st.warning("No new chrome/mining stories found today.")