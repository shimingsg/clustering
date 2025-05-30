# -*- coding: utf-8 -*-
import argparse
import json
import glob
import re

args = argparse.ArgumentParser()
args.add_argument(
    "--sample_root",
    "-sr",
    help="The root path of sample data.",
    type=str,
    default="",
)

args.add_argument(
    "--path_pattern",
    "-pp",
    help="The path pattern of the result, e.g. '*/result/*/*/*.json'.",
    type=str,
    default="*.json",
)

args.add_argument(
    "--verbose",
    "-v",
    help="The verbosity level.",
    action="store_true",)

parsed_args = args.parse_args()
 
template_dict = {
    'pid': r'PID [0-9]+ \[0x[0-9a-fA-F]+\]',
    'tid': r'Thread: [0-9]+ \[0x[0-9a-fA-F]+\]',
    'date': r'\b\d{1,2}:\d{2}:\d{2}(?:\.\d+)?(?:\s?[APMapm]{2})?\b',
    'memory address': r'0[xX][0-9a-fA-F]+(?:`[0-9a-fA-F]+)?',
    # 'win path': r'\b[a-zA-Z]:\\?(?:[^\n\\/:*?"<>|]+\\)*[^\n\\/:*?"<>|]+\.\w+',
    # 'unix_path': r'(/[^: \r\n]+)+',
} 
 
def main() -> None:
    if parsed_args.sample_root:
       pathname_pattern = parsed_args.sample_root +"**\\*.json"
    elif parsed_args.path_pattern:
       pathname_pattern = parsed_args.path_pattern
    else:
         raise ValueError("Please provide either --sample_root or --path_pattern argument.")
    # pathname_pattern = Path( parsed_args.sample_root
    result_json_path_list = glob.glob(pathname_pattern, recursive=True)
    result_json_path_list_size = len(result_json_path_list)
    err_msg_list = []
    cleaned_err_msg_list = []
    for idx, json_path in enumerate(result_json_path_list):
        with open(json_path, 'r') as fd:
            test_result = json.load(fd)
        err_msg = test_result['errorMessage']
        err_msg_list.append(err_msg)
        for key, pattern in template_dict.items():
            err_msg = re.sub(pattern, f'<{key}>', err_msg)
        cleaned_err_msg_list.append(err_msg)

    from sklearn.feature_extraction.text import TfidfVectorizer
    # from sklearn.decomposition import TruncatedSVD as DemensionReducer

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), use_idf=True, smooth_idf=True, sublinear_tf=True)
    tfidf_matrix = vectorizer.fit_transform(cleaned_err_msg_list)

    # demension_reducer = DemensionReducer(n_components=256)
    # densed_tfidf_matrix = demension_reducer.fit_transform(tfidf_matrix)
    print(f'Number of error message: {result_json_path_list_size}')

    import numpy as np
    from sklearn.mixture import GaussianMixture as GMM
    from sklearn.metrics.pairwise import cosine_distances
    from sklearn.cluster import AgglomerativeClustering as Cluster

    cosine_distances_matrix = cosine_distances(tfidf_matrix)

    distance_scores = np.reshape(cosine_distances_matrix[np.triu_indices_from(cosine_distances_matrix, k=1)], (-1, 1))

    gmm = GMM(n_components=2, covariance_type='full', random_state=42)
    gmm.fit(distance_scores)
    threshold = np.min(gmm.means_,)

    cluster = Cluster(n_clusters=None, metric='precomputed', linkage='average', distance_threshold=threshold, compute_full_tree=True)
    label_list = cluster.fit_predict(cosine_distances_matrix)

    label = dict()
    for idx, label_value in enumerate(label_list):
        if label_value not in label.keys():
            label[label_value] = []
        label[label_value].append(idx)

    for label_value in label.keys():
        print(f'Label {label_value} has {len(label[label_value])} error messages')
        output_path = f'output\\label-{label_value}.txt'
        with open(output_path, 'wb+') as fp:
            for idx in label[label_value]:
                fp.write(f'{err_msg_list[idx]}\n\n'.encode('utf-8'))
                fp.write('=========================\n\n'.encode('utf-8'))
                
if __name__ == "__main__":
    main()