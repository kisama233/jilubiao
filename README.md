## 记录应用（Vue3 + Flask + MySQL）

本项目包含一个用于日常记录的 Web 应用：
- 前端：`Vue 3` + `Element Plus` + `@kangc/v-md-editor`
- 后端：`Flask` + `PyMySQL`，Markdown 文件本地存储 + 表格记录存数据库

### 功能概览
- **Markdown 记录撰写页**（进行中）
  - Markdown 文本编辑与预览
  - 常用格式按钮（加粗、斜体、标题、列表、链接）
  - 保存为本地 `.md` 文件（后端存于 `jilu_bd/documents/`）
  - 列出已有 `.md` 文件并支持加载编辑（导入/选择逻辑待完善）
  - 导出当前内容（浏览器下载或后端下载接口，待完善）
  - 自定义命名与目录结构、索引（待完善）

- **记录表页**（进行中）
  - 现代样式的表格、添加/编辑/删除对话框
  - 对接数据库 CRUD 的逻辑待接线

### 代码结构
```
jiluqi/
  ├─ jilu/                # 前端（Vue3）
  │  ├─ src/
  │  │  ├─ views/
  │  │  │  ├─ MarkdownView.vue   # Markdown 撰写页
  │  │  │  └─ TableView.vue      # 记录表页
  │  │  └─ components/
  │  │     ├─ MarkdownEditor.vue # Markdown 编辑器组件
  │  │     └─ RecordTable.vue    # 记录表组件
  │  └─ ...
  └─ jilu_bd/             # 后端（Flask）
     ├─ app.py            # 后端服务、API 定义
     ├─ requirements.txt  # 后端依赖
     └─ documents/        # Markdown 文件存储目录（首次运行自动创建）
```

### 前置要求
- Node.js 16+（建议 18+）
- Python 3.9+
- 本地 MySQL 实例（或远程 MySQL 连接）

### 快速开始

#### 1. 启动后端（Flask）
在 PowerShell 或终端中：
```powershell
cd jilu_bd

# 可选：创建虚拟环境
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 确保存在 Markdown 存储目录（程序会自动创建）
# jilu_bd/documents/

# 配置数据库（默认 app.py 使用以下设置）
# host=localhost, user=root, password="", database=jilu_db
# 如需修改，请编辑 app.py 中的 DB_CONFIG

# 创建数据库与数据表（首次）
mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS jilu_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE jilu_db;

CREATE TABLE IF NOT EXISTS records (
  id INT PRIMARY KEY AUTO_INCREMENT,
  date DATE NOT NULL,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```powershell
# 运行后端（默认 5000 端口）
python app.py
```

#### 2. 启动前端（Vue 3）
在另一个终端：
```powershell
cd jilu

# 使用 pnpm（推荐）或 npm/yarn
# pnpm i
npm install

# 开发启动
npm run serve
```

启动成功后，访问开发地址（通常为 `http://localhost:8080`）。

### 页面与路由
- `/markdown`：Markdown 撰写页
- `/table`：记录表页
- `/`：示例首页

### 后端 API（当前已实现）
- Markdown 文件
  - `POST /api/save-document`
    - body: `{ filename?: string, content: string }`
    - 作用：保存为 `jilu_bd/documents/{filename || 时间戳}.md`
  - `GET /api/load-document?filename=xxx.md`
    - 作用：读取指定 Markdown 文件内容
  - `GET /api/list-documents`
    - 作用：列出所有 `.md` 文件名

- 记录表 CRUD
  - `POST /api/add-record`
    - body: `{ date: 'YYYY-MM-DD', title: string, content: string, status: string }`
  - `GET /api/get-records`
  - `PUT /api/update-record/<id>`
  - `DELETE /api/delete-record/<id>`

### 与需求对照
- 已满足：
  - Vue3 前端、Flask 后端、MySQL 支撑
  - Markdown 编辑/预览、保存、列出文件
  - 表格页的 UI 框架
- 待完善：
  - Markdown 工具栏的文本插入逻辑（`insertText`）
  - 导入（文件选择与加载）、导出（浏览器下载/后端下载接口）
  - 自定义文件名、命名模式（日期/自定义）与目录结构、索引
  - 表格页对接 CRUD（`refreshTable`/`submitForm`/`handleDelete`）
  - 后端：目录/子目录支持、安全校验、错误处理与下载接口

### 常见问题（FAQ）
- 访问接口跨域？
  - 已启用 CORS；确保前端访问 `http://localhost:5000` 后端地址。
- 数据库连接失败？
  - 检查 `jilu_bd/app.py` 中 `DB_CONFIG`，确认 MySQL 用户/密码/库名无误；确保已建表。
- Markdown 文件保存在哪里？
  - 默认在 `jilu_bd/documents/` 目录下，按文件名（或时间戳）保存为 `.md`。

### 构建与发布
```powershell
# 前端构建产物
cd jilu
npm run build

# 产物位于 jilu/dist，可配合 Nginx/静态服务器部署
```

### 后续规划（TODO）
- 前端：完善 Markdown 工具栏插入逻辑、导入/导出、命名与目录选择 UI、表格 CRUD 对接、分页与搜索
- 后端：增加目录/子目录管理、下载接口（含 zip 打包）、参数校验与错误码规范化
- 配置：使用环境变量/`.env` 管理数据库与运行配置

### 许可证
本项目仅供学习与内部使用，实际商用请先完善合规与安全策略。


# jilubiao
