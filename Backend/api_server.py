from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import socket
import os
import logging
import netifaces  # 用于获取网络接口信息

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_ip_addresses():
    ip_list = []
    interfaces = netifaces.interfaces()
    
    for interface in interfaces:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = addr['addr']
                if not ip.startswith('127.'):  # 排除本地回环地址
                    ip_list.append((interface, ip))
    return ip_list

app = Flask(__name__)

# 配置 CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)

# 健康检查端点
@app.route('/health-check', methods=['GET', 'OPTIONS'])
def health_check():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    client_ip = request.remote_addr
    logger.info(f"收到健康检查请求，来自: {client_ip}")
    return jsonify({
        "status": "ok",
        "message": "服务器运行正常",
        "client_ip": client_ip
    })

# 处理视频编辑请求
@app.route('/process-video', methods=['POST', 'OPTIONS'])
def process_video():
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        logger.info(f"收到视频处理请求，来自: {request.remote_addr}")
        data = request.json
        if not data or 'instruction' not in data:
            return jsonify({"error": "缺少必要的参数"}), 400
            
        instruction = data['instruction']
        logger.info(f"处理指令: {instruction}")
        
        return jsonify({
            "status": "success",
            "message": f"收到指令: {instruction}",
            "result": "视频处理完成"
        })
        
    except Exception as e:
        logger.error(f"处理视频时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 上传视频端点
@app.route('/upload-video', methods=['POST', 'OPTIONS'])
def upload_video():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    try:
        logger.info(f"收到视频上传请求，来自: {request.remote_addr}")
        if 'video' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400
            
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"error": "未选择文件"}), 400
            
        # 保存文件
        upload_folder = 'uploads'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, video_file.filename)
        video_file.save(file_path)
        logger.info(f"视频保存成功: {file_path}")
        
        return jsonify({
            "status": "success",
            "message": "视频上传成功",
            "file_path": file_path
        })
        
    except Exception as e:
        logger.error(f"上传视频时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*50)
    print("服务器启动配置:")
    print("="*50)
    
    # 获取所有可用的 IP 地址
    ip_addresses = get_all_ip_addresses()
    print("\n可用的网络接口和IP地址:")
    for interface, ip in ip_addresses:
        print(f"接口: {interface}")
        print(f"IP地址: {ip}")
        print("-" * 30)
    
    print("\n请尝试使用以上任一IP地址访问服务器")
    print(f"端口: 8000")
    print("\n提示:")
    print("1. 请确保手机和电脑在同一网络下")
    print("2. 依次尝试使用上述每个IP地址")
    print("3. 在手机浏览器中访问 http://[IP地址]:8000/health-check")
    print("4. 如果仍然无法访问，请检查防火墙设置")
    print("="*50 + "\n")
    
    try:
        # 启动 Flask 服务器
        app.run(
            host='0.0.0.0',
            port=8000,
            debug=True,
            threaded=True,
            use_reloader=True
        )
    except Exception as e:
        print(f"\n启动服务器时出错: {e}")
        print("请检查端口 8000 是否被占用") 