from dataclasses import dataclass
import pandas as pd
import feedparser

@dataclass
class RSSSource:
    site: str = ''
    section: str = ''
    url: str = '' 

    def load_from_series(self, ser: pd.Series):
        self.site = ser.site
        self.section = ser.section
        self.url = ser.link

    def __str__(self):
        return f'RSSSource(\n\tsite: {self.site},\n\tsection: {self.section}\n\turl: {self.url}\n)'
    
