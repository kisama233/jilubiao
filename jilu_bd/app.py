from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pymysql
from datetime import datetime, date
import email.utils
from flasgger import Swagger

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# 配置
# 使用绝对路径，避免切换工作目录导致保存/读取异常
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_DIR = os.path.join(BASE_DIR, 'documents')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '*****'),
    'database': os.getenv('DB_NAME', 'jilu_db'),
    'cursorclass': pymysql.cursors.DictCursor
}

# 确保文档目录存在
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def ensure_database_and_tables():
    """确保数据库和必须的数据表存在。"""
    root_config = DB_CONFIG.copy()
    db_name = root_config.pop('database', None)
    if not db_name:
        return
    # 1) 确保数据库存在
    root_connection = pymysql.connect(**root_config)
    try:
        with root_connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{db_name}` \
                   DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        root_connection.commit()
    finally:
        root_connection.close()

    # 2) 在数据库中确保表存在
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS `records` (
                  `id` INT PRIMARY KEY AUTO_INCREMENT,
                  `date` DATE NOT NULL,
                  `title` VARCHAR(255) NOT NULL,
                  `content` TEXT,
                  `status` VARCHAR(32) NOT NULL,
                  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """
            )
        connection.commit()
    finally:
        connection.close()

# 启动时确保数据库与表
ensure_database_and_tables()

@app.route('/docs', methods=['GET'])
def docs_page():
    return (
        """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>API 文档（测试）</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC', 'Microsoft YaHei', 'WenQuanYi Micro Hei', sans-serif; margin: 24px; }
                code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
                ul { line-height: 1.7; }
            </style>
        </head>
        <body>
            <h1>API 文档（测试）</h1>
            <p>后端服务默认运行在 <code>http://localhost:5000</code>。</p>
            <h2>接口列表</h2>
            <ul>
                <li>GET <code>/docs</code></li>
                <li>POST <code>/api/save-document</code></li>
                <li>GET <code>/api/load-document?filename=xxx.md</code></li>
                <li>GET <code>/api/list-documents</code></li>
                <li>POST <code>/api/add-record</code></li>
                <li>GET <code>/api/get-records</code></li>
                <li>PUT <code>/api/update-record/&lt;id&gt;</code></li>
                <li>DELETE <code>/api/delete-record/&lt;id&gt;</code></li>
            </ul>
        </body>
        </html>
        """
    )

# 文件上传API
@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """
    上传文档文件
    ---
    tags:
      - documents
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: 要上传的文件
    responses:
      200:
        description: 上传成功
        schema:
          type: object
          properties:
            status:
              type: string
            filename:
              type: string
            fileUrl:
              type: string
    """
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        file.save(filepath)
        return jsonify({
            'status': 'success',
            'filename': filename,
            'fileUrl': f'/documents/{filename}'
        })
    
    return jsonify({'status': 'error', 'message': 'File upload failed'}), 400

# Markdown文档API
@app.route('/api/save-document', methods=['POST'])
def save_document():
    """
    保存 Markdown 文档
    ---
    tags:
      - markdown
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            filename:
              type: string
              description: 可选的文件名，默认使用时间戳命名
            content:
              type: string
              description: Markdown 内容
    responses:
      200:
        description: 保存成功
        schema:
          type: object
          properties:
            status:
              type: string
            filename:
              type: string
    """
    data = request.json
    filename = data.get('filename', datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.md')
    content = data.get('content', '')
    
    with open(os.path.join(DOCUMENTS_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(content)
    
    return jsonify({'status': 'success', 'filename': filename})

@app.route('/api/load-document', methods=['GET'])
def load_document():
    """
    加载指定 Markdown 文档
    ---
    tags:
      - markdown
    parameters:
      - in: query
        name: filename
        required: true
        type: string
        description: 文件名（例如 2024-01-01-00-00-00.md）
    responses:
      200:
        description: 成功返回内容
        schema:
          type: object
          properties:
            status:
              type: string
            content:
              type: string
      404:
        description: 文件未找到
    """
    filename = request.args.get('filename')
    try:
        with open(os.path.join(DOCUMENTS_DIR, filename), 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'status': 'success', 'content': content})
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': 'File not found'}), 404

@app.route('/api/list-documents', methods=['GET'])
def list_documents():
    """
    列出文档目录下所有文件（按修改时间倒序）
    ---
    tags:
      - markdown
    responses:
      200:
        description: 返回文件名数组
        schema:
          type: object
          properties:
            status:
              type: string
            files:
              type: array
              items:
                type: string
    """
    files = [f for f in os.listdir(DOCUMENTS_DIR) if not f.startswith('.')]  # 排除隐藏文件
    files.sort(key=lambda name: os.path.getmtime(os.path.join(DOCUMENTS_DIR, name)), reverse=True)
    return jsonify({'status': 'success', 'files': files})

def _is_safe_filename(name: str) -> bool:
    return isinstance(name, str) and ('/' not in name and '\\' not in name and '..' not in name)

def normalize_date_string(value: str) -> str:
    """将各种可能的日期字符串规范为 YYYY-MM-DD。"""
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip()
        # RFC 格式（如 Mon, 18 Aug 2025 00:00:00 GMT）
        if ',' in v and 'GMT' in v:
            try:
                dt = email.utils.parsedate_to_datetime(v)
                return dt.strftime('%Y-%m-%d')
            except Exception:
                pass
        # ISO 或已是 YYYY-MM-DD 前缀
        if len(v) >= 10 and v[4] == '-' and v[7] == '-':
            return v[:10]
    return value

def _to_iso_date_for_json(value):
    """将后端从数据库获取到的日期字段统一转为 'YYYY-MM-DD' 字符串，便于前端使用。"""
    if isinstance(value, (datetime, date)):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, str) and len(value) >= 10 and value[4] == '-' and value[7] == '-':
        return value[:10]
    # 尝试解析 RFC 风格
    if isinstance(value, str) and ',' in value and 'GMT' in value:
        try:
            dt = email.utils.parsedate_to_datetime(value)
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return value
    return value

@app.route('/api/delete-document', methods=['DELETE'])
def delete_document():
    """
    删除指定 Markdown 文档
    ---
    tags:
      - markdown
    parameters:
      - in: query
        name: filename
        required: true
        type: string
        description: 仅允许删除 documents 目录下的 .md 文件
    responses:
      200:
        description: 删除成功
    """
    filename = request.args.get('filename', '')
    if not _is_safe_filename(filename):
        return jsonify({'status': 'error', 'message': 'invalid filename'}), 400
    target = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(target):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
    os.remove(target)
    return jsonify({'status': 'success'})

@app.route('/api/rename-document', methods=['POST'])
def rename_document():
    """
    重命名 Markdown 文档
    ---
    tags:
      - markdown
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            oldName:
              type: string
              description: 原文件名
            newName:
              type: string
              description: 新文件名
    responses:
      200:
        description: 重命名成功
      400:
        description: 文件名不合法
      404:
        description: 原文件不存在
    """
    data = request.json
    old_name = data.get('oldName', '')
    new_name = data.get('newName', '')
    
    if not _is_safe_filename(old_name) or not _is_safe_filename(new_name):
        return jsonify({'status': 'error', 'message': 'invalid filename'}), 400
        
    old_path = os.path.join(DOCUMENTS_DIR, old_name)
    new_path = os.path.join(DOCUMENTS_DIR, new_name)
    
    if not os.path.exists(old_path):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
    os.rename(old_path, new_path)
    return jsonify({'status': 'success'})

# 表格记录API
def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

@app.route('/api/add-record', methods=['POST'])
def add_record():
    """
    新增记录
    ---
    tags:
      - records
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            date:
              type: string
              example: 2024-01-01
            title:
              type: string
            content:
              type: string
            status:
              type: string
              enum: [进行中, 完成]
    responses:
      200:
        description: 新增成功
    """
    data = request.json
    data['date'] = normalize_date_string(data.get('date'))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO records (date, title, content, status) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (data['date'], data['title'], data['content'], data['status']))
        connection.commit()
        return jsonify({'status': 'success'})
    finally:
        connection.close()

@app.route('/api/get-records', methods=['GET'])
def get_records():
    """
    获取记录列表
    ---
    tags:
      - records
    responses:
      200:
        description: 成功返回记录数据
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM records ORDER BY date DESC"
            cursor.execute(sql)
            result = cursor.fetchall()
            # 统一日期字段为 YYYY-MM-DD
            for row in result:
                if 'date' in row:
                    row['date'] = _to_iso_date_for_json(row['date'])
        return jsonify({'status': 'success', 'data': result})
    finally:
        connection.close()

@app.route('/api/update-record/<int:id>', methods=['PUT'])
def update_record(id):
    """
    更新记录
    ---
    tags:
      - records
    parameters:
      - in: path
        name: id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            date:
              type: string
            title:
              type: string
            content:
              type: string
            status:
              type: string
    responses:
      200:
        description: 更新成功
    """
    data = request.json
    data['date'] = normalize_date_string(data.get('date'))
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE records SET date=%s, title=%s, content=%s, status=%s WHERE id=%s"
            cursor.execute(sql, (data['date'], data['title'], data['content'], data['status'], id))
        connection.commit()
        return jsonify({'status': 'success'})
    finally:
        connection.close()

@app.route('/documents/<filename>')
def serve_document(filename):
    """提供文档目录下的静态文件"""
    return send_from_directory(DOCUMENTS_DIR, filename)

@app.route('/api/delete-record/<int:id>', methods=['DELETE'])
def delete_record(id):
    """
    删除记录
    ---
    tags:
      - records
    parameters:
      - in: path
        name: id
        required: true
        type: integer
    responses:
      200:
        description: 删除成功
    """
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM records WHERE id=%s"
            cursor.execute(sql, (id,))
        connection.commit()
        return jsonify({'status': 'success'})
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
