import requests
import google.generativeai as genai
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

# Configure Gemini AI
GEMINI_API_KEY = "AIzaSyDr-LstHZ4bR2j6RaYzpSW5Lk_M--ug_ec"
genai.configure(api_key=GEMINI_API_KEY)

import time

def get_final_url(query):
    """Search for the best matching webpage link using DuckDuckGo API with rate limit handling."""
    time.sleep(2)  # ✅ Add delay to avoid rate limiting

    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=1))
    
    if results:
        return results[0]['href']
    
    return None


def fetch_webpage_content(url, summarize=False):
    """Fetch webpage content and optionally summarize."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unnecessary elements
            for tag in soup(["script", "style", "header", "footer", "nav", "aside"]):
                tag.extract()

            # Extract main content
            main_content = soup.find("article") or soup.find("div", class_="content")
            text = main_content.get_text(separator="\n", strip=True) if main_content else "Content not found"

            if summarize:
                return summarize_content(text)  # ✅ Call summarize_content() directly
            return text  

        return "Failed to fetch content"

    except Exception as e:
        return f"Error: {str(e)}"


def summarize_content(text):
    """Summarize content using Gemini AI with error handling."""
    try:
        # Limit text size to avoid API input limits
        words = text.split()[:500]  # Keep only the first 500 words
        clean_text = " ".join(words)

        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f"""
            You are an AI assistant designed to summarize news articles in a **concise, neutral, and professional manner**.
            
            **Important Instructions:**
            - Focus only on factual, informative content.
            - Exclude any **harmful, sensitive, or controversial details**.
            - If the article contains **unsafe content**, return: "⚠️ This content cannot be summarized due to safety restrictions."
            - Provide a **neutral and unbiased** summary.

            **News Article:**
            {clean_text}

            **Summarize the key points clearly in about 100-150 words.**
            """
        )

        if response and hasattr(response, "text"):  # Ensure response contains valid text
            return response.text  
        else:
            return "⚠️ Summary could not be generated due to content restrictions."

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

import google.generativeai as genai

def format_news_content(full_content):
    """
    Uses Gemini AI to format long news content into clear, meaningful paragraphs.
    """

    prompt = f"""
    Format the following news content into meaningful, well-structured paragraphs:
    
    {full_content}
    
    Ensure the readability is improved but do not change the original meaning.
    """

    try:
        response = genai.generate_content(prompt)
        formatted_content = response.text.strip() if response.text else full_content
    except Exception as e:
        formatted_content = full_content  # Fallback to original if API fails

    return formatted_content


