# 共轭智能全球投资策略平台

> Conjugate Intelligence Global Investment Strategy Platform

## 平台简介

共轭智能全球投资策略平台是一个专业的量化投资分析平台。用户只需上传带数据的 Excel 文件，选定相应的策略，即可一键生成该策略的可视化图形及核心分析指标展示。

## 核心功能

- **多策略覆盖**：涵盖股票、债券、期权、期货四大类共 65+ 种投资策略
- **一键分析**：上传 Excel 数据，选择策略，自动生成可视化分析报告
- **AI 智能问答**：集成智谱 GLM-4-Flash 大模型，随时解答策略相关问题
- **多用户支持**：前后端分离架构，支持多用户多实例

## 技术栈

### 后端
- **框架**：FastAPI (Python)
- **认证**：JWT (python-jose + passlib)
- **数据处理**：Pandas, NumPy, OpenPyXL
- **可视化**：Matplotlib
- **AI 模型**：智谱 GLM-4-Flash (zhipuai)

### 前端
- **框架**：原生 HTML/CSS/JavaScript (SPA)
- **图表**：Chart.js
- **设计**：深色主题，响应式布局

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端服务将在 `http://localhost:8000` 启动，API 文档地址：`http://localhost:8000/docs`

### 前端部署

前端为纯静态文件，可直接用任意 HTTP 服务器托管：

```bash
cd frontend
python -m http.server 3000
```

或使用 Nginx、Apache 等服务器。

前端访问地址：`http://localhost:3000`

## 策略分类

| 分类 | 策略数量 | 示例 |
|------|---------|------|
| 股票策略 | 20+ | 动量策略、价值投资、多因子模型、Smart Beta |
| 债券策略 | 15+ | 久期管理、收益率曲线交易、信用利差 |
| 期权策略 | 15+ | 跨式组合、铁鹰式、蝶式价差、日历价差 |
| 期货策略 | 15+ | 趋势跟踪、CTA策略、跨期套利、基差交易 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/register | 用户注册 |
| POST | /api/login | 用户登录 |
| GET | /api/strategies | 获取策略列表 |
| GET | /api/strategies/{id} | 获取策略详情 |
| POST | /api/upload | 上传 Excel 文件 |
| POST | /api/analyze | 执行策略分析 |
| POST | /api/chat | AI 智能问答 |

## 项目结构

```
conjugate-intelligence-platform/
├── backend/
│   ├── main.py          # FastAPI 主应用
│   ├── models.py        # 数据模型
│   ├── auth.py          # 认证模块
│   ├── strategies.py    # 策略引擎
│   ├── requirements.txt # Python 依赖
│   └── uploads/         # 文件上传目录
├── frontend/
│   ├── index.html       # 主页面
│   ├── css/
│   │   └── style.css    # 样式文件
│   └── js/
│       ├── app.js       # 核心应用逻辑
│       ├── charts.js    # 图表模块
│       └── strategies-data.js  # 策略数据
└── README.md
```

## License

MIT
