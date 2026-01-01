from scraper.retrieval import *
from prettyPrint import centerPrint, divPrint
from clustering.embedding import *
import os
sources = load_sources()
articles = pd.DataFrame()
clustered = False
p = 'articles.csv'
menus = ''
menus += '0: List Sources\n'
menus += '1: Get Summary\n'
menus += '2: Get New Articles\n'
menus += '3: Get Clusters\n'
menus += '4: View Cluster\n'
menus += '5: Exit'

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
            articles = pd.read_csv(p)
            # import code; code.interact(local=locals())
            clusters = get_clustering_inds(articles.summary.replace(pd.NA, ''))
            articles['clustering_index'] = clusters
            articles.to_csv(p)
            print('Added clustering indices to the articles!')
            clustered = True
        case '4':
            if not clustered:
                print('Clusters not assigned!')
                print('Run Menu Option 3')
            else:
                minim = articles.clustering_index.min()
                maxim = articles.clustering_index.max()
                print(f'Clustering index range: ({minim}-{maxim})')
                cluster_ind = int(input('Clustering Ind: '))
                print(articles[articles.clustering_index == cluster_ind])
        case '5':
            centerPrint('Thank You for using TrendSense!')
            break
        case _:
            print(menus)
            continue
        