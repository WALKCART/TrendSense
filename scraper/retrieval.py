from scraper.RSS import RSSSource
import pandas as pd
import feedparser
import os

def load_sources():
    db = pd.read_csv(os.path.join('scraper', 'sources.csv'))
    sources = []

    for rowInd, ser in db.iterrows():
        sources.append(RSSSource(ser.title, ser.section, ser.link))

    return sources

def get_summary(source: RSSSource, 
                entry: int
                ):
    feed = feedparser.parse(source.url)
    return feed.entries[entry].summary




