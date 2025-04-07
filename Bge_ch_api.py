from flask import Flask, request, jsonify
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
import os
import shutil

app = Flask(__name__)

# 全局变量保存向量存储实例
vectorstore = None
aa = 0



def create_vectorstore(data, bge_model_path='/home/zhangbi/Zhangbi_Traveler/LLM_model/Model_api/checkpoints/bge-large-zh-v1.5/', vectorstore_savepath="./Vectorstore_jsr/"):
    """
    创建向量存储库。
    
    参数：
    - data: 包含文本和元数据的列表，格式为 [{'text': '...', 'metadata': {...}}, ...]
    - bge_model_path: BGE 模型路径，默认为 './bge-large-zh-v1.5/'
    - vectorstore_savepath: 向量存储保存路径，默认为 './Vectorstore_1/'
    
    返回：
    - vectorstore: 创建的 Chroma 向量存储实例
    """
    try:
        # 清理旧的向量存储目录
        if os.path.exists(vectorstore_savepath):
            shutil.rmtree(vectorstore_savepath)
        os.makedirs(vectorstore_savepath, exist_ok=True)

        # 初始化嵌入模型
        huggingface_bge_embedding = HuggingFaceBgeEmbeddings(model_name=bge_model_path)

        # 创建文档对象
        docs = [Document(page_content=doc['text'], metadata=doc['metadata']) for doc in data]

        # 分割文档
        text_splitter = CharacterTextSplitter(separator="。", chunk_size=300, chunk_overlap=0)
        split_docs = text_splitter.split_documents(docs)

        # 创建 Chroma 向量存储
        global aa

        vectorstore_instance = Chroma.from_documents(split_docs, huggingface_bge_embedding, persist_directory=vectorstore_savepath+f"/{aa}")
        aa += 1
        vectorstore_instance.persist()

        print("Vectorstore created successfully.")
        return vectorstore_instance

    except Exception as e:
        print(f"Error creating vectorstore: {e}")
        return None


@app.route('/create_vectorstore', methods=['POST'])
def api_create_vectorstore():
    """
    API 端点：创建向量存储。
    """
    global vectorstore

    try:
        # 获取请求中的数据
        data = request.json.get('data')
        bge_model_path = request.json.get('bge_model_path', '/home/zhangbi/Zhangbi_Traveler/LLM_model/Model_api/checkpoints/bge-large-zh-v1.5/')
        vectorstore_savepath = request.json.get('vectorstore_savepath', './Vectorstore_jsr/')

        if not data or not isinstance(data, list):
            return jsonify({"status": "error", "message": "Invalid or missing 'data' field."}), 400

        # 调用创建向量存储函数
        vectorstore = create_vectorstore(data, bge_model_path, vectorstore_savepath)

        if vectorstore:
            return jsonify({"status": "success", "message": "Vectorstore created successfully."}), 200
        else:
            return jsonify({"status": "error", "message": "Failed to create vectorstore."}), 500

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/query', methods=['POST'])
def api_query():
    """
    API 端点：查询相似文档。
    """
    global vectorstore

    try:
        # 获取请求中的查询参数
        query = request.json.get('query')
        k = request.json.get('k', 20)

        if not query or not isinstance(query, str):
            return jsonify({"status": "error", "message": "Invalid or missing 'query' field."}), 400

        if vectorstore is None:
            return jsonify({"status": "error", "message": "Vectorstore not initialized."}), 400

        # 执行相似性搜索
        results = vectorstore.similarity_search(query, k=k)


        def format_docs(results):
            return "\n".join(list(set([d.page_content for d in results])))


        result = format_docs(results)


        return jsonify({"status": "success", "results": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host='#####', port=7800)