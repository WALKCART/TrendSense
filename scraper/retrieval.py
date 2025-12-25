from scraper.RSS import RSSSource
import pandas as pd
import feedparser
import os

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


    for source in sources:
        feed = feedparser.parse(source.url)
        n = len(feed.entries)

        site.extend([source.site]*n)
        section.extend([source.section]*n)

        title.extend(list(map(
            lambda x: x.title,
            feed.entries
        )))

        title_detail.extend(list(map(
            lambda x: x.title_detail,
            feed.entries
        )))

        summary.extend(list(map(
            lambda x: x.summary,
            feed.entries
        )))

        summary_detail.extend(list(map(
            lambda x: x.summary_detail,
            feed.entries
        )))

        links.extend(list(map(
            lambda x: x.links,
            feed.entries
        )))

        link.extend(list(map(
            lambda x: x.link,
            feed.entries
        )))

        ids.extend(list(map(
            lambda x: x.id,
            feed.entries
        )))

        guidislink.extend(list(map(
            lambda x: x.guidislink,
            feed.entries
        )))

        published.extend(list(map(
            lambda x: x.published,
            feed.entries
        )))

        published_parsed.extend(list(map(
            lambda x: x.published_parsed,
            feed.entries
        )))

    pd.DataFrame({
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
        'published_parsed': published_parsed
    }).to_csv(p)

        
