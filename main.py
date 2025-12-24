from retrieval import load_sources, get_summary

sources = load_sources()

summ = get_summary(
    source=sources[0],
    entry=0
)

print(summ)
print()
print(sources[0])