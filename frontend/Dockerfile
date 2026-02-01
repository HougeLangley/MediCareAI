FROM node:22-alpine

WORKDIR /app

# 复制静态HTML文件到根目录
COPY ./*.html /app/

# 暴露端口
EXPOSE 3000

# 启动简单HTTP服务器（从/app目录提供静态文件）
CMD ["npx", "http-server", ".", "-p", "3000", "-c", "1", "--cors"]
