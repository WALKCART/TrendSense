from scraper.retrieval import *
from prettyPrint import centerPrint, divPrint
from clustering.embedding import *
from clustering.articles import *
from clustering.textGenerator import warm_up
from data_manager import s3_upload, articlesdb_upload, config
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
menus += '3: Upload Articles to S3 and Supabase\n'
menus += '4: Get Clusters\n'
menus += '5: View Cluster\n'
menus += '6: Exit'

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
            if not os.path.exists(config.ARTICLES_CSV) or os.stat(config.ARTICLES_CSV).st_size == 0:
                print("Data Buffer is Empty.\n Run 'Get New Articles (Case 2) first.")
            else:
                print("Initialising Cloud Sync...")
                s3_upload.s3_upload()
                status = articlesdb_upload.articlesdb_upload()
                print(status)
        case '4':
            articles = pd.read_csv(p)
            # Using both the title and summary; Filling nan values with empty string
            combined_text = articles['title'].fillna("").astype(str) + " - " + articles['summary'].fillna("").astype(str)
            inds = get_clustering_inds_hdb(sents=combined_text) 
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
        case '5':
            if not clustered:
                print('Clusters not assigned!')
                print('Run Menu Option 3')
            else:
                print(f'Clustering index range: (0-{len(clusters)})')
                cluster_ind = int(input('Clustering Ind: '))
                print(clusters[cluster_ind])
                print(clusters[cluster_ind].articles)
        case '6':
            centerPrint('Thank You for using TrendSense!')
            break
        case _:
            print(menus)
            continue
        