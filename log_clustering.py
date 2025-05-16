# -*- coding: utf-8 -*-

import re, json, os, logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from itertools import groupby

def preprocess_log(log):
    """
    Preprocess the log entry by removing special characters and converting to lowercase.
    """
    log = re.sub(r'\W+', ' ', log)
    log = log.lower()
    return log

def cluster_logs(logs):
    """
    Cluster logs using TF-IDF and DBSCAN.
    """
    # Preprocess logs
    preprocessed_logs = [preprocess_log(log) for log in logs]
    
    # Feature extraction using TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(preprocessed_logs)
    
    # Clustering using DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=2)
    clusters = dbscan.fit_predict(X)
    
    return clusters

def configure_logging():
    # with open('logging_config.yaml', 'r') as f:
    os.makedirs("logs", exist_ok=True)
    # config = yaml.safe_load(f)
    # config["handlers"]["file"]["filename"] = f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log'
    # # logging.config.dictConfig(config)
    # logging.StreamHandler()
    logging.FileHandler(f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log'),
            logging.StreamHandler()
        ]
    )
    # logger = logging.getLogger("clustering")

def main():
    configure_logging()
    logs = list()
        
    raw_logs = rf"D:\repos\clustering\rawdata\raw_data_1745476397.176719.json"
    raw_logs = rf"D:\repos\clustering\rawdata\raw_data_1747364466.534833.json"
    logging.info(f'Loading raw logs from {raw_logs}')
    with open(raw_logs, 'r') as fd:
        test_result = json.load(fd)
        print(test_result)
        try:
            if type(test_result) == list:
                for e in test_result:
                    logs.append(e['error_message'])
        except Exception as e:
            logging.exception(f"exception threw when loading raw file: {e}")
    
    logging.info(f'{len(logs)} logs loaded')

    
    # Cluster logs
    clusters = cluster_logs(logs)
    
    # Print results
    zipped_logs = zip(clusters, logs)
    groupby_logs = groupby(zipped_logs, key=lambda x: x[0])
    # logs, clusters = zip(*sorted_logs)
    for cluster, log in groupby_logs:
        c_logs = list(log)
        logging.info(f"============= Cluster {cluster}:")
        for log in c_logs:
            logging.info(f"Log:{log[1]} ")
        print("==================================================>\n")

if __name__ == "__main__":
    main()

