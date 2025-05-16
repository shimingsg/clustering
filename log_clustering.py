# -*- coding: utf-8 -*-

import re, json, os, logging,argparse
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from itertools import groupby

args = argparse.ArgumentParser()
args.add_argument(
    "--epsilon",
    "-esp",
    help="The maximum distance between two samples for them to be considered as in the same neighborhood.",
    type=float,
    default=0.5,
)

args.add_argument(
    "--min_samples",
    "-ms",
    help="The minimum number of samples in a neighborhood for a point to be considered a core point.",
    type=int,
    default=2,
)

args.add_argument(
    "--verbose",
    "-v",
    help="The verbosity level.",
    action="store_true",
)

args.add_argument(
    "--raw_logs",
    "-rl",
    help="The path of the raw logs.",
    type=str,
    default="*.json",
)

parsed_args = args.parse_args()

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
    logging.info("Preprocessing logs...")
    preprocessed_logs = [preprocess_log(log) for log in logs]
    logging.info(f"Preprocessed {len(preprocessed_logs)} logs.")
    
    # Feature extraction using TF-IDF
    logging.info("Extracting features using TF-IDF...") 
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(preprocessed_logs)
    logging.info(f"Extracted features from {X.shape[0]} logs with {X.shape[1]} features.")
    
    # Clustering using DBSCAN
    logging.info("Clustering logs using DBSCAN...")
    # DBSCAN parameters
    dbscan = DBSCAN(eps=parsed_args.epsilon, min_samples=parsed_args.min_samples)
    clusters = dbscan.fit_predict(X)
    logging.info(f"Clustering completed. ")
    
    return clusters

def configure_logging():
    os.makedirs("logs", exist_ok=True)
    logging.FileHandler(f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log')
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/output_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S_%f")}.log'),
            logging.StreamHandler()
        ]
    )

def main():
    configure_logging()
    logs = list()
    raw_logs = rf"D:\repos\clustering\rawdata\raw_data_1745476397.176719.json"
    raw_logs = rf"D:\repos\clustering\rawdata\raw_data_1747364466.534833.json"
    
    logging.info(f'Loading raw logs from {parsed_args.raw_logs}')
    logging.info(f'with parameter - epsilon : {parsed_args.epsilon}')
    logging.info(f'     parameter - min_samples : {parsed_args.min_samples}')
    with open(parsed_args.raw_logs, 'r') as fd:
        test_result = json.load(fd)
        logging.info(f'Loaded raw logs from {raw_logs}')
        try:
            if type(test_result) == list:
                for e in test_result:
                    logs.append(e['error_message'])
        except Exception as e:
            logging.exception(f"exception threw when loading raw file: {e}")
    
    logging.info(f'Loaded {len(logs)} logs loaded')
    
    # Cluster logs
    clusters = cluster_logs(logs)
    logging.info(f"Clusters: {len(set(clusters))}")
    
    # Print results
    for cluster, log in groupby(sorted(zip(clusters, logs), key=lambda x: x[0]), key=lambda x: x[0]):
        c_logs = list(log)
        logging.info(f"============= Cluster {cluster}: [{len(c_logs)}] logs =============")
        if parsed_args.verbose:
            for log in c_logs:
                logging.info(log[1])
            logging.info("="*75)
            
if __name__ == "__main__":
    main()

