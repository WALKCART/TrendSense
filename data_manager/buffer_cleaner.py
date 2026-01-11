import os
from . import config

def clear_articles_csv():   
    print("\Deleting articles.csv...")
    if os.path.exists(config.ARTICLES_CSV):
        try:
            os.remove(config.ARTICLES_CSV)
            print(f"Removed: {os.path.basename(config.ARTICLES_CSV)}")
        except Exception as e:
            print(f"Error deleting {config.ARTICLES_CSV}: {e}")
    else:
        print(f"{os.path.basename(config.ARTICLES_CSV)} was already empty/not found.")
            
    print("articles.csv deleted successfully.")

def clear_temp_log_csv():
    print("\Deleting temp_log.csv...")
    if os.path.exists(config.TEMP_LOG_CSV):
        try:
            os.remove(config.TEMP_LOG_CSV)
            print(f"Removed: {os.path.basename(config.TEMP_LOG_CSV)}")
        except Exception as e:
            print(f"Error deleting {config.TEMP_LOG_CSV}: {e}")
    else:
        print(f"{os.path.basename(config.TEMP_LOG_CSV)} was already empty/not found.")
            
    print("temp_log.csv deleted successfully.")


def clear_clusters_csv():
    print("\Deleting clusters.csv...")
    if os.path.exists(config.CLUSTERS_CSV):
        try:
            os.remove(config.CLUSTERS_CSV)
            print(f"Removed: {os.path.basename(config.CLUSTERS_CSV)}")
        except Exception as e:
            print(f"Error deleting {config.CLUSTERS_CSV}: {e}")
    else:
        print(f"{os.path.basename(config.CLUSTERS_CSV)} was already empty/not found.")
            
    print("clusters.csv deleted successfully.")