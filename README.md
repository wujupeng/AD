# Htkis-Cloud-ADCS

企业级AD基础设施管理平台（Htkis-Cloud Active Directory Cloud Service），面向约3000→10000+台终端的跨国制造企业，覆盖十五层架构的统一数字身份与基础设施管理。

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│                   React + Ant Design                 │
│              (TypeScript / Vite / i18n)              │
├─────────────────────────────────────────────────────┤
│                    FastAPI Backend                    │
│         (Python 3.13 / asyncpg / ldap3)              │
├──────────┬──────────┬──────────┬────────────────────┤
│PostgreSQL│  Redis   │  Nginx   │   Samba4 AD DC     │
│   17     │   8      │  1.26    │   4.22             │
└──────────┴──────────┴──────────┴────────────────────┘
```

## 十五层架构

| 层级 | 功能 | 状态 |
|------|------|------|
| 1. AD | Active Directory 域服务 | ✅ |
| 2. DNS | 域名解析服务 | ✅ |
| 3. OU | 组织单元管理 | ✅ |
| 4. 权限 | 细粒度权限控制 | ✅ |
| 5. 文件服务器 | SMB/CIFS 文件共享 | ✅ |
| 6. DFS-R | 分布式文件系统复制 | ✅ |
| 7. 打印 | Follow-Me Printing | ✅ |
| 8. 邮件 | 邮件通讯录集成 | ✅ |
| 9. 统一认证 | Kerberos / NTLM / SAML / OIDC | ✅ |
| 10. PKI | 证书管理 | ✅ |
| 11. 补丁 | 补丁管理 | ✅ |
| 12. 监控 | 系统监控仪表盘 | ✅ |
| 13. 备份 | Veeam 备份集成 | ✅ |
| 14. 安全 | Tier Security / Defender | ✅ |
| 15. 网络/云化 | SD-WAN / Entra ID 混合 | ✅ |

## 核心功能

### 多域集成
- **company.local** — Samba4 AD DC（Linux，本地域）
- **cii.sh.cn** — Windows Server AD DC（dcser1 + dc4 额外DC）
- 自动站点识别、多DC健康监控、FSMO角色管理

### 企业统一数字身份中心
- HR 入职/离职/调岗全生命周期管理
- 自动创建/禁用 AD 账户（samba-tool → rpcclient → winexe/PowerShell 三级降级）
- 工牌管理、WiFi 802.1x、Autopilot、条件访问、SAML/OIDC 应用
- 身份来源策略、生命周期审计

### 系统监控仪表盘
- AD / PostgreSQL / Redis / Nginx / 后端服务 五面板实时监控
- 健康状态、连接数、慢查询、缓存命中率等关键指标

### DFS 文件浏览
- 多站点 SMB 共享浏览（smbclient 集成）
- 复制链接监控、冲突文件管理

## 技术栈

### 后端
- **FastAPI** + Uvicorn（异步 Web 框架）
- **SQLAlchemy** + asyncpg（异步 ORM + PostgreSQL 驱动）
- **Redis** 缓存（redis-py）
- **ldap3**（LDAP 协议）
- **python-jose**（JWT 令牌）
- **Pydantic v2**（数据验证与配置）

### 前端
- **React 18** + TypeScript
- **Ant Design 5** 组件库
- **Vite** 构建工具
- **i18n** 国际化（中/英/匈/越/西）

### 基础设施
- **Samba 4.22** AD DC（Debian 13）
- **PostgreSQL 17** 数据库
- **Redis 8** 缓存
- **Nginx 1.26** 反向代理 + HTTPS
- **Windows Server 2022** AD DC（cii.sh.cn 域）

## 目录结构

```
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── adapters/         # 外部系统适配器（LDAP/DFS/PKI/监控等）
│   │   ├── core/             # 配置、数据库、依赖注入、中间件
│   │   ├── interfaces/       # 接口定义（I前缀）
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── repositories/     # 数据访问层
│   │   ├── routers/          # API 路由
│   │   ├── schemas/          # 请求/响应模式
│   │   └── services/         # 业务逻辑层
│   ├── tests/                # 单元测试
│   └── seed_*.py             # 数据初始化脚本
├── frontend/                 # React 前端
│   └── src/
│       ├── api/              # API 客户端
│       ├── components/       # 通用组件
│       ├── i18n/             # 国际化资源
│       ├── layouts/          # 布局组件
│       ├── pages/            # 页面组件
│       └── stores/           # 状态管理
├── deploy/                   # 部署脚本
│   ├── linux/                # Linux 部署（Shell + systemd）
│   └── *.ps1                 # Windows 部署脚本
├── scripts/                  # 运维与验证脚本
└── .codeartsdoer/specs/      # 需求/设计/任务规格文档
```

## API 端点

| 模块 | 前缀 | 说明 |
|------|------|------|
| 认证 | `/api/auth` | 登录/登出/令牌刷新 |
| 组织架构 | `/api/org` | OU树/用户列表/搜索 |
| 权限检查 | `/api/permission` | 权限验证 |
| DFS 文件浏览 | `/api/dfs` | SMB共享浏览 |
| 打印管理 | `/api/print` | Follow-Me Print |
| 邮件通讯录 | `/api/mail` | 通讯录查询 |
| 审计日志 | `/api/audit` | 操作审计 |
| DC 管理 | `/api/v1/dc` | 多DC注册/健康/FSMO |
| 身份中心 | `/api/v1/enterprise/identity` | HR入职/离职/调岗/生命周期 |
| 系统配置 | `/api/v1/enterprise/settings` | 站点/LDAP目录/集成配置 |
| 系统监控 | `/api/health` | AD/PG/Redis/Nginx/后端监控 |

## 部署

### 前置条件
- Debian 13 服务器
- Samba4 AD DC 已配置
- PostgreSQL 17 + Redis 8 已安装

### 快速部署

```bash
# 1. 配置环境变量
cp deploy/linux/deploy.env deploy/linux/.env
# 编辑 .env 填入实际密码和IP

# 2. 执行部署脚本
cd deploy/linux
bash deploy-all.sh
```

### 手动部署

```bash
# 后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # 需联网环境
python init_db.py
python seed_enterprise.py
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2

# 前端
cd frontend
npm install
npm run build
# 将 dist/ 目录部署到 Nginx
```

## 登录

访问 `https://<server-ip>/`，使用 AD 域账户登录：
- 格式：`username@company.local` 或 `username`
- 默认测试账户：`zhangwei@company.local`

## 注意事项

- 所有密码和敏感 IP 在代码仓库中已用 `*****` / `******` 脱敏
- 生产部署前需在 `deploy.env` 和 `backend.env` 中填入实际凭据
- Samba4 AD 的 Administrator 密码需通过 `samba-tool user setpassword` 设置
- Windows AD DC（cii.sh.cn）LDAP 需要 SSL/TLS，但 rpcclient/winexe 可通过 NTLM 认证工作
- 前端构建需要 Node.js 18+，构建产物为静态文件

## License

Proprietary - Internal Use Only