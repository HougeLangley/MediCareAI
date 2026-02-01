#!/usr/bin/python3
import socket
import json
import time

HOST = '0.0.0.0'
PORT = 3000
BACKEND_URL = 'http://0.0.0.0:8000'
HTML_FILE = '/home/houge/Dev/MediCare_AI/frontend/index.html'

def handle_request(client_socket):
    """处理 HTTP 请求"""
    try:
        request = client_socket.recv(4096).decode('utf-8')
        request_lines = request.split('\n')
        request_line = request_lines[0].strip()
        
        # 解析请求方法
        if ' ' in request_line:
            method = request_line.split(' ')[0]
            path = request_line.split(' ')[1].split(' ')[0]
            
            if path == '/':
                # 返回主页面
                with open(HTML_FILE, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                headers = "HTTP/1.1 200 OK\r\n"
                headers += "Content-Type: text/html; charset=utf-8\r\n"
                headers += f"Content-Length: {len(html_content)}\r\n"
                headers += "Connection: close\r\n"
                client_socket.sendall(headers.encode('utf-8') + html_content.encode('utf-8'))
            
            elif path == '/health':
                # 健康检查端点（代理到后端）
                try:
                    import urllib.request
                    req = urllib.request.Request(f"{BACKEND_URL}/health", timeout=3)
                    with urllib.request.urlopen(req) as response:
                        data = response.read().decode('utf-8')
                        result = json.loads(data)
                        json_response = json.dumps(result, ensure_ascii=False)
                        
                        headers = "HTTP/1.1 200 OK\r\n"
                        headers += "Content-Type: application/json\r\n"
                        headers += f"Content-Length: {len(json_response)}\r\n"
                        headers += "Connection: close\r\n"
                        client_socket.sendall(headers.encode('utf-8') + json_response.encode('utf-8'))
                except:
                    result = {'status': 'error', 'error': 'Backend unreachable'}
                    json_response = json.dumps(result, ensure_ascii=False)
                    
                    headers = "HTTP/1.1 200 OK\r\n"
                    headers += "Content-Type: application/json\r\n"
                    headers += f"Content-Length: {len(json_response)}\r\n"
                    headers += "Connection: close\r\n"
                    client_socket.sendall(headers.encode('utf-8') + json_response.encode('utf-8'))
            
            elif path == '/api/health':
                # API 健康检查
                try:
                    import urllib.request
                    req = urllib.request.Request(f"{BACKEND_URL}/api/v1/health", timeout=3)
                    with urllib.request.urlopen(req) as response:
                        data = response.read().decode('utf-8')
                        result = json.loads(data)
                        json_response = json.dumps(result, ensure_ascii=False)
                        
                        headers = "HTTP/1.1 200 OK\r\n"
                        headers += "Content-Type: application/json\r\n"
                        headers += f"Content-Length: {len(json_response)}\r\n"
                        headers += "Connection: close\r\n"
                        client_socket.sendall(headers.encode('utf-8') + json_response.encode('utf-8'))
                except:
                    result = {'status': 'error', 'error': 'Backend API unreachable'}
                    json_response = json.dumps(result, ensure_ascii=False)
                    
                    headers = "HTTP/1.1 200 OK\r\n"
                    headers += "Content-Type: application/json\r\n"
                    headers += f"Content-Length: {len(json_response)}\r\n"
                    headers += "Connection: close\r\n"
                    client_socket.sendall(headers.encode('utf-8') + json_response.encode('utf-8'))
            
            else:
                # 其他请求返回 404
                response = 'HTTP/1.1 404 Not Found\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += 'Content-Length: 22\r\n'
                response += 'Connection: close\r\n'
                response += '\r\n'
                client_socket.sendall(response.encode('utf-8'))
                
    except Exception as e:
        print(f"Error handling request: {e}")
        try:
            response = 'HTTP/1.1 500 Internal Server Error\r\n'
            response += 'Content-Type: text/plain\r\n'
            response += 'Content-Length: 27\r\n'
            response += 'Connection: close\r\n'
            response += '\r\n'
            response += f'Error: {str(e)}\r\n'
            client_socket.sendall(response.encode('utf-8'))

def run_server():
    """启动 HTTP 服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    server_socket.settimeout(1)
    
    print(f"\n{'='*60}")
    print(f"MediCare AI 前端服务器启动成功！")
    print(f"{'='*60}")
    print(f"监听地址：http://{HOST}:{PORT}")
    print(f"{'='*60}")
    print(f"静态文件：{HTML_FILE}")
    print(f"{'='*60}")
    print(f"后端代理：{BACKEND_URL}")
    print(f"{'='*60}")
    print(f"{'='*60}")
    print("按 Ctrl+C 停止服务器")
    print(f"{'='*60}\n")
    
    print("等待连接...")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(30)
            print(f"\n新连接来自：{client_address[0]}:{client_address[1]}")
            handle_request(client_socket)
            client_socket.close()
            
    except KeyboardInterrupt:
        print(f"\n\n{'='*60}")
        print("收到停止信号，正在关闭服务器...")
        print(f"{'='*60}\n")
        server_socket.close()
    except Exception as e:
        print(f"\n\n{'='*60}")
        print(f"服务器错误：{e}")
        print(f"{'='*60}\n")
        server_socket.close()

if __name__ == '__main__':
    run_server()
