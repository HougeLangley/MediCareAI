# 生产环境 Dockerfile
# 构建前端静态文件并使用 serve 提供服务

# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install && npm cache clean --force

COPY . .

# 构建生产环境静态文件
RUN npm run build

# 运行阶段 - 使用 serve 提供静态文件
FROM node:20-alpine

WORKDIR /app

# 安装 serve
RUN npm install -g serve

# 从构建阶段复制生成的静态文件
COPY --from=builder /app/dist ./dist

EXPOSE 3000

# 使用 serve 提供静态文件
CMD ["serve", "-s", "dist", "-l", "3000"]
