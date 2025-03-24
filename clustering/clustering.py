# coding: utf-8

import argparse
import json
import glob
import os

from itertools import groupby
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MeanShift
from utls import eclapsed_timer, generate_repeated_string, logger

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
    "--model_name",
    "-mn",
    help="The name of the SentenceTransformer model.",
    type=str,
    default="all-MiniLM-L6-v2",
)
parsed_args = args.parse_args()

def get_error_message(json_path) -> str:
    '''
    Get the error message from the json file.
    
    :param json_path: The path of the json file.
    :return: The error message.
    '''
    with open(json_path, 'r') as fd:
        test_result = json.load(fd)
    return test_result['errorMessage']  

def meanshift_predict(embeddings_list) -> list:
    '''
    Clustering the embeddings by MeanShift.
    
    :param embeddings_list: The embeddings list.
    :return: The cluster result.
    '''
    clustering_model = MeanShift()
    return clustering_model.fit_predict(embeddings_list)

@eclapsed_timer
def main() -> None:
    logger.info('Start clustering')
    logger.info(f'Loads SentenceTransformer model: [{parsed_args.model_name}]')
    model = SentenceTransformer(parsed_args.model_name)
    logger.info(f'Loads SentenceTransformer model successfully')

    if os.path.exists(parsed_args.sample_root) is False:
        logger.error(f'Path {parsed_args.sample_root} does not exist')
        return
    result_json_path_pattern = os.path.join(parsed_args.sample_root, parsed_args.path_pattern)
 
    logger.info(f'Clustering result jsons from {parsed_args.sample_root}')
    result_json_list = glob.glob(result_json_path_pattern)
    logger.info(f'Found {len(result_json_list)} json files')
    embeddings_list = list()
    for json_path in result_json_list:
        err_msg = get_error_message(json_path)
        embeddings_list.append(model.encode(err_msg))
         
    result = meanshift_predict(embeddings_list) # clustering
    if len(result) == len(result_json_list):
        logger.info('Clustering successfully')
        merged_result = list(zip(result, result_json_list)) # merge cluster number and json path
        merged_result.sort(key=lambda x: x[0]) # sort by cluster number
        repeated_string = generate_repeated_string('=', 75)
        for key, path in groupby(merged_result, key=lambda x: x[0]):
            paths = list(path)
            logger.info(f'Cluster {key}, count: {len(paths)}')
            for p in iter(paths):
                logger.info(p[1])
                logger.info(get_error_message(p[1]))
                logger.info(repeated_string)
    else:
        logger.error('Clustering failed')
if __name__ == "__main__":
    main()