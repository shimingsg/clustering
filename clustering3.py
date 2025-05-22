# import os
import json
import pandas as pd
# import numpy as np
from sentence_transformers import SentenceTransformer
import hdbscan
# import umap
from sklearn.feature_extraction.text import CountVectorizer
# import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
import glob
import argparse

args = argparse.ArgumentParser()
args.add_argument(
    "--output",
    "-o",
    help="file name of the output csv file",
    type=str,
    default="clustered_logs.csv",
)
args.add_argument(
    "--root",
    "-r",
    help="The root path of the result, e.g. 'D:\\test\\assets'.",
    type=str,
    default=".",
)
parsed_args = args.parse_args()

# Initialize Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Directory containing JSON log files
# log_dir = rf'D:\shimingsg\logs'
json_path_pattern = rf'D:\shimingsg\AzDO_bySG\result\*\*\*.json'
# Function to read and parse JSON files
def read_logs():
    logs = []
    # for filename in os.listdir(log_dir):
    for filename in glob.glob(f"{parsed_args.root}/**/*.json", recursive=True):
    # for filename in glob.glob(path_pattern):
        # if filename.endswith('.json'):
        with open(filename, 'r') as file:
            log = json.load(file)
            logs.append(log)
    return logs

# Function to extract relevant fields from logs
def extract_fields(logs):
    data = []
    for log in logs:
        test_case = log.get('testCase', {}).get('name', '')
        error_message = log.get('errorMessage', '')
        stack_trace = log.get('stackTrace', '')
        data.append((test_case, error_message, stack_trace))
    return data

# Function to clean and preprocess text
def preprocess_text(text):
    return text.lower().replace('\n', ' ').replace('\r', ' ')

# Function to embed text using Sentence-BERT
def embed_text(data):
    texts = [preprocess_text(f"{test_case} {error_message} {stack_trace}") for test_case, error_message, stack_trace in data]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings

# Function to cluster logs using HDBSCAN
def cluster_logs(embeddings):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, prediction_data=True)
    cluster_labels = clusterer.fit_predict(embeddings)
    return cluster_labels, clusterer

# Function to label clusters using keyword frequency
def label_clusters(data, cluster_labels):
    cluster_texts = {}
    for i, label in enumerate(cluster_labels):
        if label not in cluster_texts:
            cluster_texts[label] = []
        cluster_texts[label].append(f"{data[i][1]} {data[i][2]}")
    
    cluster_labels = {}
    for label, texts in cluster_texts.items():
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform(texts)
        freqs = zip(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist()[0])
        sorted_freqs = sorted(freqs, key=lambda x: -x[1])
        cluster_labels[label] = ' '.join([word for word, freq in sorted_freqs[:5]])
    
    return cluster_labels

# Function to save results to CSV
def save_results(data, cluster_labels, cluster_names, filename='clustered_logs1.csv'):
    df = pd.DataFrame(data, columns=['Test Case', 'Error Message', 'Stack Trace'])
    df['Cluster'] = cluster_labels
    df['Cluster Label'] = df['Cluster'].map(cluster_names)
    df.to_csv(filename, index=False)

# Function to visualize clusters using UMAP
def visualize_clusters(embeddings, cluster_labels):
    # reducer = umap.UMAP()
    # umap_embeddings = reducer.fit_transform(embeddings)
    # plt.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], c=cluster_labels, cmap='Spectral', s=5)
    # plt.colorbar(boundaries=np.arange(len(set(cluster_labels))+1)-0.5).set_ticks(np.arange(len(set(cluster_labels))))
    # plt.title('UMAP projection of the clustered logs')
    # plt.show()
    ...

# Main function to process logs
def main():
    logs = read_logs()
    data = extract_fields(logs)
    embeddings = embed_text(data)
    cluster_labels, clusterer = cluster_logs(embeddings)
    cluster_names = label_clusters(data, cluster_labels)
    save_results(data, cluster_labels, cluster_names, parsed_args.output)
    visualize_clusters(embeddings, cluster_labels)
    silhouette_avg = silhouette_score(embeddings, cluster_labels)
    print(f'Silhouette Score: {silhouette_avg}')

if __name__ == "__main__":
    # from pathlib import Path
    # folder_path = Path(parsed_args.root)
    # for f in folder_path.rglob("*.json"):
    #     print(f)
    # for filename in glob.glob(f"{parsed_args.root}/**/*.json", recursive=True):
    #     print(filename)
    main()
