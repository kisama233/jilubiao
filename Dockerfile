# 多阶段构建：前端 (Vue) + 后端 (Python) + 生产环境 Nginx

########################
# 1) 构建前端
########################
FROM node:latest AS fe-build
WORKDIR /app/frontend
COPY jilu/package.json jilu/package-lock.json* jilu/pnpm-lock.yaml* ./
RUN npm ci --registry=https://registry.npmmirror.com || npm install --registry=https://registry.npmmirror.com
COPY jilu/ ./
RUN npm run build

########################
# 2) 构建后端
########################
FROM python:3.9 AS be
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app/backend

# 更换 apt-get 的软件源为国内源
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources

# 现在执行 apt-get update
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY jilu_bd/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY jilu_bd/ ./

########################
# 3) 最终生产镜像 (Nginx + 后端)
########################
FROM nginx:stable-alpine3.21
WORKDIR /app

COPY --from=fe-build /app/frontend/dist/ /usr/share/nginx/html/

COPY --from=be /app/backend/ /app/backend/

COPY --from=be /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=be /usr/local/bin/gunicorn /usr/local/bin/

COPY nginx.conf /etc/nginx/conf.d/default.conf

ENV DB_HOST=localhost \
    DB_USER=root \
    DB_PASSWORD= \
    DB_NAME=jilu_db \
    API_PORT=5000

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "jilu-app:app"]