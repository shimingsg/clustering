import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
import hdbscan
import umap
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score

# Initialize Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to clean and preprocess text
def preprocess_text(text):
    return text.lower().replace('\n', ' ').replace('\r', ' ')

# Function to extract fields
def extract_fields(logs):
    data = []
    for log in logs:
        test_case = log.get('testCase', {}).get('name', '')
        error_message = log.get('errorMessage', '')
        stack_trace = log.get('stackTrace', '')
        data.append((test_case, error_message, stack_trace))
    return data

# Function to embed text
def embed_text(data):
    texts = [preprocess_text(f"{tc} {em} {st}") for tc, em, st in data]
    return model.encode(texts, show_progress_bar=True)

# Function to cluster logs
def cluster_logs(embeddings):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    labels = clusterer.fit_predict(embeddings)
    return labels

# Function to label clusters
def label_clusters(data, labels):
    cluster_texts = {}
    for i, label in enumerate(labels):
        if label not in cluster_texts:
            cluster_texts[label] = []
        cluster_texts[label].append(f"{data[i][1]} {data[i][2]}")
    cluster_labels = {}
    for label, texts in cluster_texts.items():
        vectorizer = CountVectorizer(stop_words='english')
        X = vectorizer.fit_transform(texts)
        freqs = zip(vectorizer.get_feature_names_out(), X.sum(axis=0).tolist()[0])
        sorted_freqs = sorted(freqs, key=lambda x: -x[1])
        cluster_labels[label] = ' '.join([word for word, _ in sorted_freqs[:5]])
    return cluster_labels

# Function to visualize clusters
def visualize_clusters(embeddings, labels):
    reducer = umap.UMAP()
    umap_embeddings = reducer.fit_transform(embeddings)
    plt.figure(figsize=(10, 6))
    plt.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], c=labels, cmap='Spectral', s=10)
    plt.title("UMAP projection of clustered logs")
    st.pyplot(plt)

# Streamlit app
def main():
    st.title("Test Log Clustering Dashboard")
    uploaded_files = st.file_uploader("Upload JSON log files", accept_multiple_files=True, type="json")

    if uploaded_files:
        logs = [json.load(f) for f in uploaded_files]
        data = extract_fields(logs)
        embeddings = embed_text(data)
        labels = cluster_logs(embeddings)
        cluster_names = label_clusters(data, labels)

        df = pd.DataFrame(data, columns=["Test Case", "Error Message", "Stack Trace"])
        df["Cluster"] = labels
        df["Cluster Label"] = df["Cluster"].map(cluster_names)

        st.success("Clustering complete!")
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "clustered_logs.csv")

        st.subheader("Cluster Visualization")
        visualize_clusters(embeddings, labels)

        if len(set(labels)) > 1:
            score = silhouette_score(embeddings, labels)
            st.write(f"Silhouette Score: {score:.2f}")

        st.subheader("Cluster Summaries")
        for label, summary in cluster_names.items():
            st.write(f"**Cluster {label}**: {summary}")

if __name__ == "__main__":
    main()
