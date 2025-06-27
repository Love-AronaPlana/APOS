# APOS 部署指南

本文档详细介绍了如何在不同环境中部署 APOS 项目。

## 📋 部署前准备

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+) / macOS / Windows
- **Python**: 3.11 或更高版本
- **Node.js**: 20.0 或更高版本
- **内存**: 最少 2GB RAM
- **存储**: 最少 5GB 可用空间

### 依赖检查

```bash
# 检查 Python 版本
python3 --version

# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version
```

## 🚀 开发环境部署

### 1. 获取项目代码

```bash
# 如果有 Git 仓库
git clone <repository-url>
cd APOS

# 或者直接使用现有代码
cd /path/to/APOS
```

### 2. 后端部署

```bash
cd backend

# 创建虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-3.5-turbo
DEBUG=True
LOG_LEVEL=INFO
MAX_HISTORY_LENGTH=100
```

### 3. 前端部署

```bash
cd frontend/apos-frontend

# 安装依赖
npm install
# 或使用 pnpm (推荐)
pnpm install
```

### 4. 启动服务

#### 启动后端 (终端 1)

```bash
cd backend
python3 app.py
```

#### 启动前端 (终端 2)

```bash
cd frontend/apos-frontend
npm run dev -- --host
```

### 5. 验证部署

- 后端服务: http://localhost:8880/api/health
- 前端应用: http://localhost:5173
- 运行测试: `python3 test_api.py`

## 🏭 生产环境部署

### 1. 使用 Docker 部署 (推荐)

#### 创建 Dockerfile (后端)

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8880

CMD ["python", "app.py"]
```

#### 创建 Dockerfile (前端)

```dockerfile
# frontend/apos-frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
```

#### 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8880:8880"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_API_BASE=${OPENAI_API_BASE}
      - OPENAI_API_MODEL=${OPENAI_API_MODEL}
    volumes:
      - ./backend/.env:/app/.env

  frontend:
    build: ./frontend/apos-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

#### 部署命令

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 使用 PM2 部署

#### 安装 PM2

```bash
npm install -g pm2
```

#### 创建 PM2 配置文件

```javascript
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: 'apos-backend',
      script: 'app.py',
      cwd: './backend',
      interpreter: 'python3',
      env: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'apos-frontend',
      script: 'npm',
      args: 'run preview -- --host --port 3000',
      cwd: './frontend/apos-frontend',
      env: {
        NODE_ENV: 'production'
      }
    }
  ]
};
```

#### 部署命令

```bash
# 构建前端
cd frontend/apos-frontend
npm run build

# 启动服务
pm2 start ecosystem.config.js

# 查看状态
pm2 status

# 查看日志
pm2 logs

# 重启服务
pm2 restart all

# 停止服务
pm2 stop all
```

### 3. 使用 Nginx 反向代理

#### 创建 Nginx 配置

```nginx
# /etc/nginx/sites-available/apos
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/APOS/frontend/apos-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8880;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/apos /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

## 🔧 环境变量配置

### 必需的环境变量

```env
# OpenAI API 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-3.5-turbo

# 应用配置
DEBUG=False
LOG_LEVEL=INFO
MAX_HISTORY_LENGTH=100
SECRET_KEY=your-secret-key-here
```

### 可选的环境变量

```env
# 数据库配置 (如果使用数据库)
DATABASE_URL=postgresql://user:password@localhost/apos

# Redis 配置 (如果使用 Redis)
REDIS_URL=redis://localhost:6379/0

# 其他配置
CORS_ORIGINS=https://your-domain.com
MAX_WORKERS=4
```

## 📊 监控和日志

### 1. 日志配置

APOS 使用内置的彩色日志系统，生产环境建议配置日志文件：

```python
# 在 utils/logger.py 中添加文件处理器
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    # ... 现有代码 ...
    
    # 添加文件处理器
    file_handler = RotatingFileHandler(
        'logs/apos.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    ))
    logger.addHandler(file_handler)
```

### 2. 健康检查

设置定期健康检查：

```bash
# 创建健康检查脚本
cat > health_check.sh << 'EOF'
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8880/api/health)
if [ $response -eq 200 ]; then
    echo "$(date): APOS is healthy"
else
    echo "$(date): APOS is unhealthy (HTTP $response)"
    # 可以添加重启逻辑
fi
EOF

chmod +x health_check.sh

# 添加到 crontab
echo "*/5 * * * * /path/to/health_check.sh >> /var/log/apos_health.log" | crontab -
```

## 🔒 安全配置

### 1. HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # SSL 配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # ... 其他配置 ...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. 防火墙配置

```bash
# 使用 ufw (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 或使用 iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -j DROP
```

## 🚨 故障排除

### 常见问题

1. **后端启动失败**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep 8880
   
   # 检查 Python 依赖
   pip3 list
   
   # 查看详细错误
   python3 app.py
   ```

2. **前端构建失败**
   ```bash
   # 清除缓存
   npm cache clean --force
   
   # 重新安装依赖
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **API 调用失败**
   ```bash
   # 测试 API 连接
   curl -v http://localhost:8880/api/health
   
   # 检查环境变量
   echo $OPENAI_API_KEY
   ```

### 性能优化

1. **后端优化**
   - 使用 Gunicorn 作为 WSGI 服务器
   - 配置连接池
   - 启用缓存

2. **前端优化**
   - 启用 Gzip 压缩
   - 配置 CDN
   - 优化静态资源

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看日志文件
2. 运行 `python3 test_api.py` 进行诊断
3. 检查环境变量配置
4. 确认网络连接正常

---

**祝您部署顺利！** 🎉

