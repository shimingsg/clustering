# clustering
clustering error message for analyzing earlier

## Guide:
1. Create visual environment: ``` python -m venv .venv ```
2. Activate .venv: ``` .venv/Scripts/activate ```
3. Deactivate .venv: ``` .venv/Scripts/deactivate ```
4. Install requirements: ``` pip install -r requirements.txt ```
## clustering using meanshift:
### Usage:
``` 
python -m clustering -sr <result json root path> -pp <path pattern>
```
##### For example: 
```
python -m clustering -sr D:\mytest -pp *\*\*.json
```

## clustering using tf-idf and DBSCAN
### Usage:
```
python .\log_clustering.py -rl <raw data path> -esp <float, default value 0.5> -ms <min-samples, defalut value 2>

``` 

## create raw data from original
```python -m raw -pp test\*```

