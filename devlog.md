**24 December 2025**
- created `dev/` fodler that contains all test files and refernces.
- created `dev/rss_test.py` to test out `feedparser`
- created `sources.py` to add/remove sources (temporarily stored as a csv)
  - added the sources requested by `Aditya Gupta`.
- created `retrieval.py` that does the job getting the data from the sources.
- created `RSS.py` that has helpful classes and functions in the context of RSS retrieval.
- created temporary `main.py` to test out the different modules.

**25 Decmeber 2025**
- started working on the `get-new` function which can be used for scheduled retrieval.
- realized that the schema of every entry from every website is the same: 
  - title
  - title_detail
  - summary
  - summary_detail
  - links
  - link
  - id
  - guidislink
  - published
  - published_parsed
- all the entries will be temporarily stored in a csv.
- refactored `title` in sources.csv to `site`. Made changes in all the files.

**26 December 2025**
- Read [TutorialsPoint article](https://www.tutorialspoint.com/python_web_scraping/python_web_scraping_data_extraction.htm) on web scraping and html processing.
- referred [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#quick-start) for getting text from site.
- wrote `get_html` func in `retrieval.py` to get html from article url.
- write `get_text_from_html` func in `retrieval.py` to get article body from article html.
- made `get_new()` func faster, added progress bar. `articles.csv` to now have the article body as well.

**27 December 2025**
- started working on the clustering algo
- decided to start with cosine similarity.
- using the `all-MiniLM-L6-v2` model for getting embeddings.
- wrote `get_cosine_similarity` func for getting cosine similarity.
- replaced numpy code with torch code
- made it device agnostic.