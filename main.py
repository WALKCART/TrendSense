from retrieval import load_sources, get_summary
from prettyPrint import centerPrint, divPrint
import os
sources = load_sources()
menus = '0: List Sources\n1: Get Summary\n2: Exit'

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
            titles = list(map(
                lambda x: f'{x.title}_{x.section}',
                sources
            ))
            for ind in range(len(titles)):
                print(f'{ind}: {titles[ind]}')
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
            centerPrint('Thank You for using TrendSense!')
            break
        case _:
            print(menus)
            continue
        