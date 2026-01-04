from scraper.retrieval import *
from prettyPrint import centerPrint, divPrint
from clustering.embedding import *
from clustering.articles import *
from clustering.textGenerator import warm_up
import os
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

sources = load_sources()
articles = pd.DataFrame()
clustered = False
p = 'articles.csv'
warm_up()


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
            inds = get_clustering_inds(sents=articles.summary) 
            articles['clustering_index'] = inds
            articles.to_csv(p, index=False)
            clusters = create_article_clusters(
                db=pd.read_csv(p),
                clustering_index_col='clustering_index'
                )
            for ind in range(len(clusters)):
                print(f'{ind}: {clusters[ind]}')
            save_clusters('clusters.csv', clusters=clusters)
            clustered = True
        case '4':
            if not clustered:
                print('Clusters not assigned!')
                print('Run Menu Option 3')
            else:
                print(f'Clustering index range: (0-{len(clusters)})')
                cluster_ind = int(input('Clustering Ind: '))
                print(clusters[cluster_ind])
                print(clusters[cluster_ind].articles)
        case '5':
            centerPrint('Thank You for using TrendSense!')
            break
        case _:
            print(menus)
            continue
        