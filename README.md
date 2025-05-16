# clustering
clustering error message for analyzing earlier

## Guide:
1. create visual environment: 
    ``` python 
    python -m venv .env
    ```
2. activate .env: .env/Scripts/activate
3. deactivate .env: .env/Scripts/deactivate
4. install requirements
    ```python
    pip install -r requirements.txt
    ```
## Usage:
``` python
python -m clustering -sr <result json root path> -pp <path pattern>
```
### demo: 
```python
python -m clustering -sr D:\mytest -pp *\*\*.json
```

# clustering using tf-idf and DBSCAN
## usage:
```python
python .\log_clustering.py -rl <raw data path> -esp <float, default value 0.5> -ms <min-samples, defalut value 2>

```
 