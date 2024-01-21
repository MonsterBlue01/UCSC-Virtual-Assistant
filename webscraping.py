import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试获取标题，如果找不到则使用默认值
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title found.'

        # 尝试获取主要内容，如果找不到则使用默认值
        # 您可能需要根据目标网页的实际结构调整选择器
        main_content = soup.find('main')  # 或其他适合的选择器
        text = main_content.get_text(strip=True) if main_content else 'No main content could be extracted.'

        return {
            'url': url,
            'title': title,
            'text': text
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {'url': url, 'title': 'No title found.', 'text': 'No main content could be extracted.', 'error': str(e)}
