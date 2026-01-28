from trendsense.scraper.RSS import RSSSource
import pandas as pd
import feedparser
import os
from datetime import date, timedelta, datetime
from time import mktime
from typing import Optional
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path

def load_sources():
    base_dir = Path(__file__).resolve().parent
    sources_path = base_dir / "sources.csv"

    db = pd.read_csv(sources_path)

    sources = []
    for _, ser in db.iterrows():
        sources.append(RSSSource(ser.site, ser.section, ser.link))

    return sources

def get_summary(source: RSSSource, 
                entry: int
                ):
    feed = feedparser.parse(source.url)
    return feed.entries[entry].summary

def get_new(sources: list, p: str, end_dt: date, start_dt: Optional[date] = None):
    data = []

    for source in tqdm(sources):
        feed = feedparser.parse(source.url)

        for entry in feed.entries:
            entry_date = datetime.fromtimestamp(mktime(entry.published_parsed))
            is_after_start = (start_dt is None) or (entry_date >= start_dt)
            is_before_end = (entry_date <= end_dt)
            if is_after_start and is_before_end:
                body_text = get_text_from_html(get_html(entry.link))
                data.append({
                    'site': source.site,
                    'section': source.section,
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'link': entry.link,
                    'published': entry_date,
                    'body': body_text,
                    'clustering_index': pd.NA
                })
        
    df = pd.DataFrame(data)
    df.to_csv(p, index=False)

        
def get_html(url: str):
    r = requests.get(url)
    return r.text

def get_text_from_html(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all("p")

    content = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 80:          # threshold for real content
            if not p.find("a"):     # avoid nav-heavy text
                content.append(text)

    article_text = "\n".join(content)
    return article_text