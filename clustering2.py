import json
import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import glob

# Function to clean and sanitize JSON content
def clean_json_content(json_content):
    # Remove invalid control characters
    sanitized_content = re.sub(r'[\x00-\x1F\x7F]', '', json_content)
    return sanitized_content

# Collect logs in a list
logs_list = []

# Load and clean multiple JSON log files
json_path_pattern = rf'D:\shimingsg\AzDO_bySG\result\*\*\*.json'
for file_path in glob.glob(json_path_pattern):
    with open(file_path, 'r') as file:
        raw_content = file.read()
        cleaned_content = clean_json_content(raw_content)
        try:
            log_data = json.loads(cleaned_content)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from file {file_path}: {e}")
            continue
        
        # Extract relevant fields from the log
        test_case_name = log_data.get('testCase', {}).get('name', '')
        error_message = log_data.get('errorMessage', '')
        stack_trace = log_data.get('stackTrace', '')
        
        # Combine error message and stack trace for clustering
        combined_text = error_message + ' ' + stack_trace
        
        # Append the log to the DataFrame)
        logs_list.append({
            'test_case_name': test_case_name,
            'error_message': error_message,
            'stack_trace': stack_trace,
            'combined_text': combined_text
        })

print(f"Loaded {len(logs_list)} logs from JSON files.")
 
# Initialize an empty DataFrame to hold all logs
logs_df = pd.DataFrame(logs_list,columns=['test_case_name', 'error_message', 'stack_trace', 'combined_text'])

# Preprocess the text data
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(logs_df['combined_text'])

# Apply KMeans clustering
num_clusters = 3  # You can adjust the number of clusters
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
logs_df['cluster'] = kmeans.fit_predict(X)

# Calculate silhouette score to evaluate clustering
silhouette_avg = silhouette_score(X, logs_df['cluster'])
print(f'Silhouette Score: {silhouette_avg}')

# Output the clusters
for cluster_num in range(num_clusters):
    print(f'\nCluster {cluster_num}:')
    cluster_logs = logs_df[logs_df['cluster'] == cluster_num]
    for index, row in cluster_logs.iterrows():
        print(f"Test Case: {row['test_case_name']}")
        print(f"Error Message: {row['error_message']}")
        print(f"Stack Trace: {row['stack_trace']}\n")
        print("#" * 80)

