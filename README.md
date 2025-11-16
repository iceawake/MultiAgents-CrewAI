# crewAI 多智能体系统项目

基于crewAI框架构建的多智能体协作系统，具备Web界面可视化和实时结果展示功能。

## 项目概述

本项目实现了一个基于crewAI的多智能体协作系统，包含以下核心功能：

- 多智能体任务分配与协作
- Web界面可视化展示
- 实时结果显示
- RESTful API支持
- 灵活的配置和扩展性

## 项目结构

```
├── .gitignore                # Git忽略文件配置
├── advanced_multi_agent.py   # 高级多智能体实现
├── crewai_ui.py              # 图形用户界面实现
├── crewai_web_app.py         # Web应用服务端
├── multi_agent_system.py     # 基础多智能体系统
├── requirements.txt          # 项目依赖列表
├── test_kimi.py              # 测试脚本
└── README.md                 # 项目说明文档
```

## 安装与部署

### 环境要求

- Python 3.10+
- pip 23.0+

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/iceawake/MultiAgents-CrewAI.git
cd MultiAgents-CrewAI
```

2. 创建并激活虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入必要的API密钥和配置项
```

## 使用方法

### 启动Web应用

```bash
python crewai_web_app.py
```

Web应用将在 http://localhost:5003 启动，您可以通过以下路径访问：
- 主页：http://localhost:5003
- API接口：http://localhost:5003/api/execution-data

### 启动GUI界面

```bash
python crewai_ui.py
```

GUI界面将在 http://localhost:5001/a.html 打开。

### 直接运行多智能体系统

```bash
python multi_agent_system.py
# 或者高级版本
python advanced_multi_agent.py
```

## API文档

### 获取执行数据

**GET /api/execution-data**

返回当前多智能体系统的执行状态和结果。

**响应格式：**
```json
{
  "execution_data": [
    {
      "agent_name": "Agent名称",
      "action": "执行的操作",
      "result": "执行结果",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  ]
}
```

## 自定义配置

可以通过修改相应的Python文件来自定义多智能体的行为、任务分配和协作方式。主要配置点包括：

- 智能体定义和角色
- 任务分解和优先级
- 协作策略
- Web界面参数

## 测试

```bash
python test_kimi.py
```

## 贡献指南

欢迎提交Issue和Pull Request来改进项目。提交PR前请确保代码风格一致，并添加必要的测试。

## 许可证

[MIT License](https://opensource.org/licenses/MIT)