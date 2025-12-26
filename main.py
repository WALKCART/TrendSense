from scraper.retrieval import *
from prettyPrint import centerPrint, divPrint
import os
sources = load_sources()
menus = ''
menus += '0: List Sources\n'
menus += '1: Get Summary\n'
menus += '2: Get New Articles\n'
menus += '3: Save Article\n'
menus += '4: Exit'

#printing the title 
text = ''
with open('title.txt', 'r') as file:
    text = file.read()

centerPrint(text)
divPrint()
os.system('figlet Menu')
print(menus)
while True:
    inp = input('>>> ')
    match inp:
        case '0':
            sites = list(map(
                lambda x: f'{x.site}_{x.section}',
                sources
            ))
            for ind in range(len(sites)):
                print(f'{ind}: {sites[ind]}')
        case '1':
            source_ind = int(input('Enter Source Index: '))
            ind = int(input('Enter Entry Index: '))
            summ = get_summary(
                source=sources[source_ind],
                entry=ind
            )
            print(summ)
            print()
            print(sources[source_ind])
        case '2':
            p = input('Enter path to save: ')
            get_new(
                sources=sources, 
                p=p
            )
        case '3':
            source_ind = int(input('Enter Source Index: '))
            ind = int(input('Enter Entry Index: '))
            feed = feedparser.parse(sources[source_ind].url)
            url = feed.entries[ind]['link']
            
            m = get_html(url)
            body = get_text_from_html(m)
            with open('article.txt', 'w') as file:
                file.write(body)
        case '4':
            centerPrint('Thank You for using TrendSense!')
            break
        case _:
            print(menus)
            continue
        