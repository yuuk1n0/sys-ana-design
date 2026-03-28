<p align="center">
  <a href="https://github.com/mizhexiaoxiao/vue-fastapi-admin">
    <img alt="Vue FastAPI Admin Logo" width="200" src="https://github.com/mizhexiaoxiao/vue-fastapi-admin/blob/main/deploy/sample-picture/logo.svg">
  </a>
</p>

<h1 align="center">课程设计：超市管理系统</h1>

[English](./README-en.md) | 简体中文

本项目为课程设计超市管理系统，基于 FastAPI + Vue3 + Naive UI 前后端分离架构开发，在原有权限管理能力基础上，扩展了商品、分类、库存等业务模块，面向“商品流转与库存管理”的教学场景。

### 课程设计定位
- **项目目标**：完成一个可运行的超市管理后台，支撑管理员进行商品、库存、角色权限等核心操作。
- **面向角色**：系统管理员、运营人员（课程演示时可按角色分配功能）。
- **核心能力**：登录鉴权、RBAC 权限控制、业务模块管理、接口文档联调。

### 已实现模块（可按课程进度继续扩展）
- **系统管理**：用户管理、角色管理、菜单管理、API 权限管理、审计日志。
- **商品管理**：商品分类管理、商品信息管理。
- **库存管理**：库存记录与库存变动查询。
- **基础能力**：JWT 鉴权、动态路由、接口级权限控制。

### 默认测试账号
- username: admin
- password: 123456

### 快速开始
#### 方法一：dockerhub拉取镜像

```sh
docker pull mizhexiaoxiao/vue-fastapi-admin:latest 
docker run -d --restart=always --name=vue-fastapi-admin -p 9999:80 mizhexiaoxiao/vue-fastapi-admin
```

#### 方法二：dockerfile构建镜像
##### docker安装(版本17.05+)

```sh
yum install -y docker-ce
systemctl start docker
```

##### 构建镜像

```sh
git clone https://github.com/mizhexiaoxiao/vue-fastapi-admin.git
cd vue-fastapi-admin
docker build --no-cache . -t vue-fastapi-admin
```

##### 启动容器

```sh
docker run -d --restart=always --name=vue-fastapi-admin -p 9999:80 vue-fastapi-admin
```

##### 访问

http://localhost:9999

username：admin

password：123456

### 本地启动
#### 后端
启动项目需要以下环境：
- Python 3.11
- MySQL 8.0+（默认连接 mysql）
- Redis 6.0+（用于缓存/会话等能力）

#### 方法一（推荐）：使用 uv 安装依赖
1. 安装 uv
```sh
pip install uv
```

2. 创建并激活虚拟环境
```sh
uv venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate  # Windows
```

3. 安装依赖
```sh
uv sync
```

4. 启动服务
```sh
python run.py
```

#### 方法二：使用 Pip 安装依赖
1. 创建虚拟环境
```sh
python3 -m venv venv
```

2. 激活虚拟环境
```sh
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```sh
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

4. 启动服务
```sh
python run.py
```

服务启动后可访问：
- 后端接口文档：http://localhost:9999/docs
- 后端服务地址：http://127.0.0.1:9999

#### 前端
启动项目需要以下环境：
- node v18.8.0+

1. 进入前端目录
```sh
cd web
```

2. 安装依赖(建议使用pnpm: https://pnpm.io/zh/installation)
```sh
npm i -g pnpm # 已安装可忽略
pnpm i # 或者 npm i
```

3. 启动
```sh
pnpm dev
```

4. 访问前端
```text
http://127.0.0.1:3100
```

### 项目启动配置说明

#### 后端配置（根目录 `.env`）
```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=Root@123456
MYSQL_DATABASE=vue_fastapi_admin

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
```

#### 前端配置（`web/.env` 与 `web/.env.development`）
```env
VITE_PORT = 3100
VITE_USE_PROXY = true
VITE_BASE_API = '/api/v1'
```

#### 端口与代理关系
- 前端开发端口：`3100`
- 后端服务端口：`9999`
- 代理规则：`/api/v1` -> `http://127.0.0.1:9999`

### 课程设计注意事项
- 首次运行前请确认 MySQL、Redis 服务已启动，且 `.env` 与本机环境一致。
- 首次启动后端会执行数据库初始化与迁移，如遇迁移异常可检查 `migrations` 目录与数据库连接权限。
- 前后端联调时保持后端先启动，再启动前端，避免代理请求失败。
- 团队开发建议统一分支命名、接口返回结构和数据库字段命名规则。
- 提交前至少执行一次前端 `pnpm lint`，避免低级格式与规范问题。

### 目录说明

```
├── app                   // 应用程序目录
│   ├── api               // API接口目录
│   │   └── v1            // 版本1的API接口
│   │       ├── apis      // API相关接口
│   │       ├── base      // 基础信息接口
│   │       ├── menus     // 菜单相关接口
│   │       ├── roles     // 角色相关接口
│   │       └── users     // 用户相关接口
│   ├── controllers       // 控制器目录
│   ├── core              // 核心功能模块
│   ├── log               // 日志目录
│   ├── models            // 数据模型目录
│   ├── schemas           // 数据模式/结构定义
│   ├── settings          // 配置设置目录
│   └── utils             // 工具类目录
├── deploy                // 部署相关目录
│   └── sample-picture    // 示例图片目录
└── web                   // 前端网页目录
    ├── build             // 构建脚本和配置目录
    │   ├── config        // 构建配置
    │   ├── plugin        // 构建插件
    │   └── script        // 构建脚本
    ├── public            // 公共资源目录
    │   └── resource      // 公共资源文件
    ├── settings          // 前端项目配置
    └── src               // 源代码目录
        ├── api           // API接口定义
        ├── assets        // 静态资源目录
        │   ├── images    // 图片资源
        │   ├── js        // JavaScript文件
        │   └── svg       // SVG矢量图文件
        ├── components    // 组件目录
        │   ├── common    // 通用组件
        │   ├── icon      // 图标组件
        │   ├── page      // 页面组件
        │   ├── query-bar // 查询栏组件
        │   └── table     // 表格组件
        ├── composables   // 可组合式功能块
        ├── directives    // 指令目录
        ├── layout        // 布局目录
        │   └── components // 布局组件
        ├── router        // 路由目录
        │   ├── guard     // 路由守卫
        │   └── routes    // 路由定义
        ├── store         // 状态管理(pinia)
        │   └── modules   // 状态模块
        ├── styles        // 样式文件目录
        ├── utils         // 工具类目录
        │   ├── auth      // 认证相关工具
        │   ├── common    // 通用工具
        │   ├── http      // 封装axios
        │   └── storage   // 封装localStorage和sessionStorage
        └── views         // 视图/页面目录
            ├── error-page // 错误页面
            ├── login      // 登录页面
            ├── profile    // 个人资料页面
            ├── system     // 系统管理页面
            └── workbench  // 工作台页面
```

### 小组成员负责模块（模板）

| 序号 | 成员姓名 | 负责模块 | 具体内容 | 完成状态 |
|---|---|---|---|---|
| 1 | 待填写 | 系统管理 | 用户/角色/菜单/权限 | 待开始 |
| 2 | 待填写 | 商品管理 | 商品分类、商品信息、商品查询 | 待开始 |
| 3 | 待填写 | 库存管理 | 入库、出库、库存盘点、预警 | 待开始 |
| 4 | 待填写 | 前端页面 | 页面交互、表单校验、联调适配 | 待开始 |
| 5 | 待填写 | 测试与文档 | 用例设计、测试记录、答辩材料 | 待开始 |

### 小组成员留名

- 组长：`待填写`
- 成员1：`待填写`
- 成员2：`待填写`
- 成员3：`待填写`
- 成员4：`待填写`
- 指导教师：`待填写`
