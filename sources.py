import pandas as pd

sources = {
    'title': ['livemint'] * 2 + ['business_standard'] * 8 + ['economic_times'] * 2,
    'section': ['markets', 
                'companies',
                'world_news',
                'technology',
                'companies',
                'industry',
                'economy',
                'finance',
                'markets',
                'budget',
                'markets',
                'technology'
                ],
    'link': ['https://www.livemint.com/rss/markets',
             'https://www.livemint.com/rss/companies',
             'https://www.business-standard.com/rss/world-news-221.rss',
             'https://www.business-standard.com/rss/technology-108.rss',
             'https://www.business-standard.com/rss/companies-101.rss',
             'https://www.business-standard.com/rss/industry-217.rss',
             'https://www.business-standard.com/rss/economy-102.rss',
             'https://www.business-standard.com/rss/finance-103.rss',
             'https://www.business-standard.com/rss/markets-106.rss',
             'https://www.business-standard.com/rss/budget-110.rss',
             'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
             'https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms'
             ]
}

df = pd.DataFrame(sources)
df.to_csv('sources.csv', index=False)

