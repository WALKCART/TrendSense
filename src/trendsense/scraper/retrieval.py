from scraper.RSS import RSSSource
import pandas as pd
import feedparser
import state_manager.state_manager as sm
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

def load_sources():
    db = pd.read_csv(os.path.join('scraper', 'sources.csv'))
    sources = []

    for rowInd, ser in db.iterrows():
        sources.append(RSSSource(ser.site, ser.section, ser.link))

    return sources

def get_summary(source: RSSSource, 
                entry: int
                ):
    feed = feedparser.parse(source.url)
    return feed.entries[entry].summary

def get_new(sources: list, p: str):
    site = []
    section = []
    title = []
    title_detail = []
    summary = []
    summary_detail = []
    links = []
    link = []
    ids = []
    guidislink = []
    published = []
    published_parsed = []
    body = []
    clustering_index = []


    for source in tqdm(sources):
        feed = feedparser.parse(source.url)
        n = len(feed.entries)

        site.extend([source.site]*n)
        section.extend([source.section]*n)

        for entry in feed.entries:
            title.append(entry.title)
            title_detail.append(entry.title_detail)
            summary.append(entry.summary)
            summary_detail.append(entry.summary_detail)
            links.append(entry.links)
            link.append(entry.link)
            ids.append(entry.id)
            guidislink.append(entry.guidislink)
            published.append(entry.published)
            published_parsed.append(entry.published_parsed)
            body.append(get_text_from_html(get_html(entry['link'])))
            clustering_index.append(pd.NA)

    df = pd.DataFrame({
        'site': site,
        'section': section,
        'title': title, 
        'title_detail': title_detail,
        'summary': summary,
        'summary_detail': summary_detail, 
        'links': links,
        'link': link,
        'id': ids, 
        'guidislink': guidislink,
        'published': published,
        'published_parsed': published_parsed,
        'body': body,
        'clustering_index': clustering_index
    })
    
    sm.set("SCRAPPED", "True")
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