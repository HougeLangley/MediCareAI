#!/usr/bin/env python3
"""
MediCare AI 前端代理服务器
使用纯 Python3 实现，将前端请求代理到后端 API
"""
import http.server
import socketserver
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlparse
import json
import threading
import time
import os
import sys

# 配置
BACKEND_HOST = '0.0.0.0'
BACKEND_PORT = 8000
FRONTEND_HOST = '0.0.0.0'
FRONTEND_PORT = 3000

# 代理路径配置
API_BASE_PATH = '/api'
STATIC_ROOT = '/home/houge/Dev/MediCare_AI/frontend'

class MediCareHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """MediCare AI 请求处理器"""
    
    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/health':
            return self.handle_health_check()
        elif parsed_path.path == '/api/health':
            return self.handle_api_health_check()
        elif parsed_path.path.startswith('/api/'):
            return self.proxy_to_backend(parsed_path)
        elif self.path == '/':
            return self.serve_file('/index.html')
        else:
            return self.serve_file(parsed_path.path.lstrip('/'))
    
    def do_POST(self):
        """处理 POST 请求 - 全部代理到后端"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
        else:
            post_data = b''
        
        parsed_path = urlparse(self.path)
        
        # 只代理 API 请求到后端
        if parsed_path.path.startswith('/api/'):
            return self.proxy_post_to_backend(parsed_path, post_data)
        else:
            return self.send_json_response({
                'error': 'Endpoint not found',
                'path': parsed_path.path
            }, 404)
    
    def handle_health_check(self):
        """前端健康检查"""
        try:
            # 检查后端健康状态
            backend_healthy = self.check_backend_health()
            
            response_data = {
                'status': 'healthy' if backend_healthy else 'degraded',
                'frontend': 'healthy',
                'backend': 'healthy' if backend_healthy else 'unhealthy',
                'timestamp': time.time()
            }
            
            return self.send_json_response(response_data)
        except Exception as e:
            return self.send_json_response({
                'error': str(e),
                'status': 'error'
            }, 500)
    
    def handle_api_health_check(self):
        """代理 API 健康检查到后端"""
        try:
            req = Request(f"http://{BACKEND_HOST}:{BACKEND_PORT}/health")

            with urlopen(req, timeout=10) as response:
                result = response.read().decode('utf-8')
                
            # 转发响应到客户端
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
            self.send_header('Access-Control-Allow-Credentials', 'true')
            self.end_headers()
            self.wfile.write(result.encode('utf-8'))
            
        except URLError as e:
            return self.send_json_response({
                'error': f'Backend unreachable: {e}',
                'status': 'error'
            }, 503)
        except Exception as e:
            return self.send_json_response({
                'error': f'Health check failed: {e}',
                'status': 'error'
            }, 500)
    
    def proxy_to_backend(self, parsed_path, get_params=''):
        """代理请求到后端 API"""
        api_path = parsed_path.path
        try:
            backend_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}{api_path}"

            if parsed_path.query:
                backend_url += '?' + parsed_path.query

            req = Request(backend_url, method='GET')

            for header in ['Authorization', 'Content-Type', 'User-Agent']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])

            with urlopen(req, timeout=60) as response:
                response_data = response.read().decode('utf-8')

                self.send_response(response.status)

                for header in ['Content-Type', 'Content-Length']:
                    if header in response:
                        self.send_header(header, response[header])

                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.end_headers()

                self.wfile.write(response_data.encode('utf-8'))

        except URLError as e:
            return self.send_json_response({
                'error': f'Backend proxy failed: {e}',
                'path': api_path
            }, 502)
        except Exception as e:
            return self.send_json_response({
                'error': f'Proxy error: {e}',
                'path': api_path
            }, 500)
    
    def proxy_post_to_backend(self, parsed_path, post_data=b''):
        """代理 POST 请求到后端"""
        api_path = parsed_path.path
        try:
            backend_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}{api_path}"

            req = Request(backend_url, data=post_data, method='POST')
            req.add_header('Content-Type', 'application/json')

            for header in ['Authorization', 'Content-Type', 'User-Agent']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])

            with urlopen(req, timeout=60) as response:
                response_data = response.read().decode('utf-8')

                self.send_response(response.status)

                for header in ['Content-Type', 'Content-Length']:
                    if header in response:
                        self.send_header(header, response[header])

                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.end_headers()

                self.wfile.write(response_data.encode('utf-8'))

        except URLError as e:
            return self.send_json_response({
                'error': f'Backend proxy failed: {e}',
                'path': api_path
            }, 502)
        except Exception as e:
            return self.send_json_response({
                'error': f'Proxy error: {e}',
                'path': api_path
            }, 500)
    
    def serve_file(self, relative_path):
        """提供静态文件"""
        try:
            file_path = os.path.join(STATIC_ROOT, relative_path.lstrip('/'))

            if not os.path.exists(file_path):
                return self.send_json_response({
                    'error': 'File not found',
                    'path': relative_path
                }, 404)

            content_type = 'text/html'
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.json'):
                content_type = 'application/json'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.svg'):
                content_type = 'image/svg+xml'

            with open(file_path, 'rb') as f:
                file_content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(file_content)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(file_content)

        except Exception as e:
            return self.send_json_response({
                'error': f'File serving error: {e}',
                'path': relative_path
            }, 500)

    def send_json_response(self, data, status_code=200):
        """发送 JSON 响应"""
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            response_body = json_data.encode('utf-8')

            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)

        except Exception as e:
            print(f"Error sending JSON response: {e}")

    def check_backend_health(self):
        """检查后端健康状态"""
        try:
            req = Request(f"http://{BACKEND_HOST}:{BACKEND_PORT}/health")
            with urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('status') == 'healthy'
        except Exception:
            return False

def check_backend_health():
    """检查后端健康状态"""
    try:
        req = Request(f"http://{BACKEND_HOST}:{BACKEND_PORT}/health")
        with urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('status') == 'healthy'
    except Exception:
        return False

def run_server():
    """启动代理服务器"""
    print("\n" + "="*60)
    print("MediCare AI 前端代理服务器")
    print("="*60)
    print(f"\n监听地址：{FRONTEND_HOST}:{FRONTEND_PORT}")
    print(f"后端代理：http://{BACKEND_HOST}:{BACKEND_PORT}")
    print(f"静态文件根：{STATIC_ROOT}")
    print(f"API 代理路径：/api/")
    print(f"\n" + "="*60)
    print("\n服务说明：")
    print("- 前端页面：http://192.168.50.115:3000/index.html")
    print("- API 代理：/api/* -> http://192.168.50.115:8000/api/*")
    print("- Swagger 文档：http://192.168.50.115:8000/docs")
    print("- 健康检查：http://192.168.50.115:3000/health")
    print("- CORS 已启用：*")
    print(f"\n按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    # 创建服务器
    try:
        server_address = (FRONTEND_HOST, FRONTEND_PORT)
        
        httpd = http.server.HTTPServer(
            server_address,
            MediCareHTTPRequestHandler
        )
        
        print("✅ 代理服务器启动成功！")
        print(f"\n{'='*60}")
        print("服务器正在运行中...")
        print(f"访问 http://192.168.50.115:3000/ 查看系统状态")
        print("="*60 + "\n")
        
        httpd.serve_forever()
        
    except OSError as e:
        print(f"\n❌ 启动失败：{e}")
        print(f"端口 {FRONTEND_PORT} 可能被占用")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == '__main__':
    run_server()
