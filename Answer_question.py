
import json
import requests

Pro_Walled_city_spots = './Pro_Walled_city_spots_1.json'

with open(Pro_Walled_city_spots, 'r', encoding='utf-8') as file:
   data = json.load(file)

# API 地址
BASE_URL = "http://********:7800"

def create_vectorstore(data, bge_model_path=None, vectorstore_savepath=None):
    """
    调用 /create_vectorstore API 创建向量存储。
    
    参数：
    - data: 包含文本和元数据的列表，格式为 [{'text': '...', 'metadata': {...}}, ...]
    - bge_model_path: BGE 模型路径（可选）
    - vectorstore_savepath: 向量存储保存路径（可选）
    
    返回：
    - 响应 JSON 数据
    """
    url = f"{BASE_URL}/create_vectorstore"
    payload = {
        "data": data,
    }
    if bge_model_path:
        payload["bge_model_path"] = bge_model_path
    if vectorstore_savepath:
        payload["vectorstore_savepath"] = vectorstore_savepath

    response = requests.post(url, json=payload)
    
    # 打印原始响应内容
    print("Raw Response:", response.text)
    
    return response.json()


def query_vectorstore(query, k=5):
    """
    调用 /query API 查询相似文档。
    
    参数：
    - query: 查询文本
    - k: 返回结果的数量（默认为 5）
    
    返回：
    - 响应 JSON 数据
    """
    url = f"{BASE_URL}/query"
    payload = {
        "query": query,
        "k": k,
    }

    response = requests.post(url, json=payload)
    return response.json()

create_response = create_vectorstore(data)


def find_text(query):

   query_response = query_vectorstore(query, k=10)

   return query_response['results']