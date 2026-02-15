#!/usr/bin/env python3

import http.server
import json
import socket
import urllib.request
import urllib.parse
import threading
import subprocess
import os

HOST = os.getenv('FRONTEND_HOST', '0.0.0.0')
PORT = int(os.getenv('FRONTEND_PORT', '3000'))
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend:8000')
LOG_FILE = os.getenv('LOG_FILE', 'frontend.log')

class MediCareHandler(http.server.SimpleHTTPRequestHandler):
    """MediCare AI 请求处理器"""
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        if self.path == '/health':
            # 前端健康检查
            try:
                req = urllib.request.Request(f"{BACKEND_URL}/health", timeout=5)
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(result)
            except Exception as e:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}))
        
        elif self.path == '/api/health':
            # 代理到后端 API 健康检查
            try:
                req = urllib.request.Request(f"{BACKEND_URL}/health", timeout=5)
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(result)
            except Exception as e:
                self.send_response(503)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}))
        
        elif self.path == '/':
            # 主页 - 返回静态文件
            self.path = '/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        else:
            # 静态文件
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

def log_with_timestamp(message):
    """带时间戳的日志记录"""
    timestamp = subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S'], 
                                       text=True).decode().strip()
    log_line = f"[{timestamp}] {message}\n"
    print(log_line)
    
    # 写入日志文件
    with open(LOG_FILE, 'a') as f:
        f.write(log_line)

def get_server_ip():
    """获取服务器 IP 地址"""
    try:
        # 连接到公共 IP 服务
        with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('ip', '127.0.0.1')
    except:
        return '127.0.0.1'

def run_server():
    """启动 HTTP 服务器"""
    server_address = (HOST, PORT)
    
    local_ip = get_server_ip()
    
    log_with_timestamp(f"MediCare AI 前端服务启动中...")
    log_with_timestamp(f"监听地址: {HOST}:{PORT}")
    log_with_timestamp(f"服务器IP: {local_ip}")
    log_with_timestamp(f"后端API: {BACKEND_URL}")
    
    try:
        handler_class = MediCareHandler
        
        httpd = http.server.HTTPServer(server_address, handler_class)
        log_with_timestamp(f"HTTP 服务器启动成功！")
        
        print(f"\n{'='*80}")
        print(f"MediCare AI 前端服务已启动")
        print(f"访问地址：")
        print(f"  http://127.0.0.1:3000")
        print(f"  http://{local_ip}:3000")
        print(f"  http://0.0.0.0:3000")
        print(f"后端 API: {BACKEND_URL}")
        print(f"{'='*80}")
        print(f"按 Ctrl+C 停止服务")
        print(f"{'='*80}\n")
        
        httpd.serve_forever()
    except KeyboardInterrupt:
        log_with_timestamp("接收到停止信号，正在关闭服务器...")
        print("\n正在关闭服务器...")
        httpd.server_close()
    except OSError as e:
        log_with_timestamp(f"启动失败: {e}")
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        log_with_timestamp(f"未预期的错误: {e}")
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_server()
