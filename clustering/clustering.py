# coding: utf-8

import argparse
import json
import glob
import os

from itertools import groupby
from sentence_transformers import SentenceTransformer
from sklearn.cluster import MeanShift
from utls import eclapsed_timer, generate_repeated_string, logger
from tqdm import tqdm

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

args.add_argument(
    "--verbose",
    "-v",
    help="The verbosity level.",
    action="store_true",)

parsed_args = args.parse_args()

def get_error_message(json_path) -> str:
    '''
    Get the error message from the json file.
    
    :param json_path: The path of the json file.
    :return: The error message.
    '''
    with open(json_path, 'r') as fd:
        test_result = json.load(fd)
        try:
            if type(test_result) == list:
                return test_result[0]['errorMessage']
            elif type(test_result) == dict:
                return test_result['errorMessage']
        except:
            return "Invalid error message"

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
    logger.info(f'Loading SentenceTransformer model: [{parsed_args.model_name}]')
    model = SentenceTransformer(parsed_args.model_name)
    logger.info(f'Loading SentenceTransformer model successfully')

    if os.path.exists(parsed_args.sample_root) is False:
        logger.error(f'Path {parsed_args.sample_root} does not exist')
        return
    result_json_path_pattern = os.path.join(parsed_args.sample_root, parsed_args.path_pattern)
 
    logger.info(f'Clustering result jsons from {result_json_path_pattern}')
    result_json_list = glob.glob(result_json_path_pattern)
    logger.info(f'Found {len(result_json_list)} json files')
    embeddings_list = list()
    
    for json_path in tqdm(result_json_list, desc='Model encoding'):
        if os.path.exists(json_path) is False:
            logger.error(f'Path {json_path} does not exist')
            continue
        if os.path.getsize(json_path) == 0:
            logger.error(f'File {json_path} is empty')
            continue
        err_msg = get_error_message(json_path)
        embeddings_list.append(model.encode(err_msg))
        
    
    # for json_path in result_json_list:
    #     logger.info(f'Processing {json_path}')
    #     err_msg = get_error_message(json_path)
    #     embeddings_list.append(model.encode(err_msg))
    logger.info(f'Embeddings count: {len(embeddings_list)}')

    result = meanshift_predict(embeddings_list) # clustering
    if len(result) == len(result_json_list):
        logger.info('Clustering successfully')
        merged_result = list(zip(result, result_json_list)) # merge cluster number and json path
        merged_result.sort(key=lambda x: x[0]) # sort by cluster number
        repeated_string = generate_repeated_string('=', 75)
        for key, path in groupby(merged_result, key=lambda x: x[0]):
            paths = list(path)
            logger.info(f'Cluster {key}, count: {len(paths)}')
            if parsed_args.verbose:
                for p in iter(paths):
                    logger.info(p[1])
                    logger.info(get_error_message(p[1]))
                    logger.info(repeated_string)
    else:
        logger.error('Clustering failed')
if __name__ == "__main__":
    main()