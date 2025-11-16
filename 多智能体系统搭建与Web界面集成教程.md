# 多智能体系统搭建与Web界面集成教程

本文档详细记录了从零开始搭建基于CrewAI的多智能体系统，并集成Web界面进行可视化展示的完整过程。

## 目录

1. [环境准备](#环境准备)
2. [基础多智能体系统实现](#基础多智能体系统实现)
3. [Web界面开发](#web界面开发)
4. [系统集成与部署](#系统集成与部署)
5. [使用说明](#使用说明)

## 环境准备

### 1.1 创建项目目录

```bash
mkdir -p crewAI
cd crewAI
```

### 1.2 虚拟环境搭建

使用Python虚拟环境隔离项目依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows
```

### 1.3 依赖安装

创建`requirements.txt`文件并添加必要依赖：

```txt
crewai
python-dotenv
flask
openai
```

安装依赖包：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.4 环境变量配置

创建`.env`文件，配置API密钥和环境变量：

```env
# 模型配置
OPENAI_API_KEY=your_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# 代理设置（可选，用于网络访问）
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

## 基础多智能体系统实现

### 2.1 模型初始化模块

首先实现Kimi模型的初始化函数，支持代理设置和超时配置：

```python
import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_kimi_llm(model_name: str = "moonshot-v1-8k", temperature: float = 0.1):
    """
    获取Kimi模型实例，支持代理设置和超时配置
    """
    # 配置代理
    proxies = None
    if os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY'):
        proxies = {
            'http': os.getenv('HTTP_PROXY'),
            'https': os.getenv('HTTPS_PROXY')
        }
    
    # 配置请求参数
    request_kwargs = {}
    if proxies:
        request_kwargs['proxies'] = proxies
    
    # 初始化并返回模型
    return ChatOpenAI(
        api_key=os.getenv('KIMI_API_KEY'),
        base_url="https://api.moonshot.cn/v1",
        model_name=model_name,
        temperature=temperature,
        timeout=300,  # 5分钟超时
        request_kwargs=request_kwargs
    )
```

### 2.2 智能体定义

创建不同角色的智能体，每个智能体具有特定的角色、目标和背景：

```python
from crewai import Agent

# 初始化Kimi模型
kimi_llm = get_kimi_llm()

# 创建产品经理智能体
product_manager = Agent(
    role="产品经理",
    goal="深入理解用户需求，制定详细的产品规划",
    backstory="""
    你是一位资深的产品经理，拥有丰富的产品规划和需求分析经验。
    你善于沟通，能够准确把握用户痛点，并将其转化为可执行的产品需求。
    """,
    verbose=True,
    llm=kimi_llm
)

# 创建开发工程师智能体
developer = Agent(
    role="开发工程师",
    goal="基于产品需求，设计并实现高效的技术解决方案",
    backstory="""
    你是一位经验丰富的全栈开发工程师，精通多种编程语言和框架。
    你善于解决复杂的技术问题，并能够快速实现功能需求。
    """,
    verbose=True,
    llm=kimi_llm
)

# 创建UI设计师智能体
ui_designer = Agent(
    role="UI设计师",
    goal="创建美观、易用的用户界面设计",
    backstory="""
    你是一位专业的UI设计师，注重用户体验和视觉效果。
    你能够创建既美观又实用的界面设计，提升产品的整体品质。
    """,
    verbose=True,
    llm=kimi_llm
)

# 创建测试工程师智能体
tester = Agent(
    role="测试工程师",
    goal="确保产品质量，发现并报告潜在问题",
    backstory="""
    你是一位严谨的测试工程师，拥有全面的测试经验。
    你善于设计测试用例，发现潜在的问题，并提供改进建议。
    """,
    verbose=True,
    llm=kimi_llm
)
```

### 2.3 任务定义

为每个智能体定义具体任务，明确任务目标、预期输出和任务优先级：

```python
from crewai import Task

# 产品需求分析任务
product_task = Task(
    description="""
    分析用户需求，制定详细的产品需求文档。
    1. 明确产品的核心功能和价值主张
    2. 定义目标用户群体和使用场景
    3. 创建详细的功能列表和优先级
    4. 制定产品开发路线图
    """,
    expected_output="详细的产品需求文档，包括功能规格、用户故事和验收标准",
    agent=product_manager,
    priority=1
)

# 技术架构设计任务
tech_task = Task(
    description="""
    基于产品需求，设计系统的技术架构和实现方案。
    1. 选择适合的技术栈和框架
    2. 设计系统的整体架构和模块划分
    3. 定义数据模型和API接口
    4. 制定开发规范和最佳实践
    """,
    expected_output="完整的技术架构文档，包括架构图、技术选型和实现方案",
    agent=developer,
    priority=2
)

# UI设计任务
ui_task = Task(
    description="""
    创建产品的用户界面设计。
    1. 设计整体界面布局和导航结构
    2. 创建关键页面的设计原型
    3. 定义设计系统和组件库
    4. 制定UI/UX设计规范
    """,
    expected_output="UI设计文档，包括线框图、原型和设计规范",
    agent=ui_designer,
    priority=3
)

# 测试计划任务
test_task = Task(
    description="""
    制定全面的测试计划和测试用例。
    1. 设计功能测试用例
    2. 制定性能测试和安全测试方案
    3. 创建测试环境和数据
    4. 设计缺陷管理和报告流程
    """,
    expected_output="详细的测试计划和测试用例文档",
    agent=tester,
    priority=4
)
```

### 2.4 智能体团队配置

配置智能体团队，设置任务执行流程和协作方式：

```python
from crewai import Crew
from crewai.process import Process

# 创建智能体团队
crew = Crew(
    agents=[product_manager, developer, ui_designer, tester],
    tasks=[product_task, tech_task, ui_task, test_task],
    process=Process.sequential,  # 顺序执行任务
    verbose=True
)
```

### 2.5 系统执行与重试机制

添加重试机制，确保系统在遇到临时问题时能够自动恢复：

```python
import time

def run_crew_with_retry(max_retries: int = 3):
    """
    运行智能体团队，包含重试机制
    """
    retries = 0
    while retries < max_retries:
        try:
            print(f"第 {retries + 1} 次尝试执行智能体团队任务...")
            result = crew.kickoff()
            print("\n智能体团队任务执行成功!")
            return result
        except Exception as e:
            retries += 1
            print(f"\n执行出错: {str(e)}")
            if retries < max_retries:
                print(f"{retries} 秒后进行第 {retries + 1} 次重试...")
                time.sleep(retries * 5)
            else:
                print("已达到最大重试次数，任务执行失败。")
                raise

# 执行智能体团队任务
if __name__ == "__main__":
    try:
        result = run_crew_with_retry()
        print("\n任务结果:")
        print(result)
    except Exception as e:
        print(f"\n任务执行失败: {str(e)}")
```

## Web界面开发

### 3.1 基础Web应用构建

创建一个基于Flask的Web应用，提供智能体系统的可视化界面：

```python
from flask import Flask, render_template, jsonify, Response
import json
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# 存储执行数据的变量
execution_data = {
    "status": "idle",
    "current_task": None,
    "progress": 0,
    "messages": [],
    "agents": []
}

# 事件监听器列表
listeners = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/execution-data')
def get_execution_data():
    return jsonify(execution_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

### 3.2 实时数据更新机制

实现Server-Sent Events (SSE)，支持实时数据推送：

```python
@app.route('/api/events')
def events():
    """
    提供Server-Sent Events接口，实时推送系统更新
    """
    def event_stream():
        # 创建一个新的事件监听器
        listener_id = str(time.time())
        listeners.append(listener_id)
        try:
            while True:
                # 这里应该有实际的事件生成逻辑
                # 暂时使用示例事件
                event = {
                    "type": "update",
                    "data": execution_data,
                    "timestamp": time.time()
                }
                yield f'data: {json.dumps(event)}

'
                time.sleep(1)  # 每秒发送一次更新
        except GeneratorExit:
            # 移除监听器
            listeners.remove(listener_id)
    
    return Response(event_stream(), content_type='text/event-stream')
```

### 3.3 响应式Web界面设计

创建HTML模板，包含响应式设计和交互功能：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI智能体协作系统</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3b82f6',
                        secondary: '#10b981',
                        accent: '#8b5cf6',
                        neutral: '#6b7280',
                        "neutral-content": '#f3f4f6',
                        "base-100": '#ffffff',
                        "base-200": '#f9fafb',
                        "base-300": '#e5e7eb',
                        "base-content": '#1f2937',
                    },
                    fontFamily: {
                        inter: ['Inter', 'sans-serif'],
                    },
                }
            }
        }
    </script>
    <style type="text/tailwindcss">
        @layer utilities {
            .content-auto {
                content-visibility: auto;
            }
            .text-shadow {
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .transition-all-ease {
                transition: all 0.3s ease;
            }
        }
    </style>
</head>
<body class="bg-base-200 font-inter text-base-content min-h-screen flex flex-col">
    <!-- 导航栏 -->
    <header class="bg-white shadow-md sticky top-0 z-50">
        <div class="container mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center space-x-2">
                <i class="fa fa-robot text-2xl text-primary"></i>
                <h1 class="text-xl font-bold text-primary">AI智能体协作系统</h1>
            </div>
            <div class="flex items-center space-x-4">
                <button id="start-btn" class="bg-primary hover:bg-primary/90 text-white py-2 px-4 rounded-md transition-all-ease flex items-center">
                    <i class="fa fa-play-circle mr-2"></i>
                    <span>启动智能体</span>
                </button>
                <button id="refresh-btn" class="bg-neutral hover:bg-neutral/90 text-white py-2 px-4 rounded-md transition-all-ease flex items-center">
                    <i class="fa fa-refresh mr-2"></i>
                    <span>刷新</span>
                </button>
            </div>
        </div>
    </header>

    <!-- 主内容区 -->
    <main class="flex-grow container mx-auto px-4 py-6">
        <!-- 状态卡片 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="bg-white rounded-xl shadow-lg p-6 transition-all-ease hover:shadow-xl">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-lg font-semibold text-neutral">系统状态</h3>
                    <span id="status-indicator" class="h-3 w-3 rounded-full bg-gray-400"></span>
                </div>
                <p id="status-text" class="text-2xl font-bold text-base-content">就绪</p>
            </div>
            
            <div class="bg-white rounded-xl shadow-lg p-6 transition-all-ease hover:shadow-xl">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-lg font-semibold text-neutral">当前任务</h3>
                    <i class="fa fa-tasks text-accent"></i>
                </div>
                <p id="current-task" class="text-2xl font-bold text-base-content">无</p>
            </div>
            
            <div class="bg-white rounded-xl shadow-lg p-6 transition-all-ease hover:shadow-xl">
                <div class="flex justify-between items-center mb-2">
                    <h3 class="text-lg font-semibold text-neutral">执行进度</h3>
                    <i class="fa fa-bar-chart text-secondary"></i>
                </div>
                <div class="flex items-center space-x-2">
                    <div class="w-full bg-gray-200 rounded-full h-4">
                        <div id="progress-bar" class="bg-secondary h-4 rounded-full" style="width: 0%"></div>
                    </div>
                    <span id="progress-text" class="text-2xl font-bold text-base-content">0%</span>
                </div>
            </div>
        </div>

        <!-- 选项卡 -->
        <div class="bg-white rounded-xl shadow-lg overflow-hidden mb-6">
            <div class="flex border-b">
                <button class="tab-btn active flex-1 py-4 px-6 font-medium text-primary border-b-2 border-primary" data-tab="agents">
                    <i class="fa fa-users mr-2"></i>智能体管理
                </button>
                <button class="tab-btn flex-1 py-4 px-6 font-medium text-neutral hover:text-primary transition-colors" data-tab="history">
                    <i class="fa fa-history mr-2"></i>交互历史
                </button>
                <button class="tab-btn flex-1 py-4 px-6 font-medium text-neutral hover:text-primary transition-colors" data-tab="logs">
                    <i class="fa fa-file-text-o mr-2"></i>系统日志
                </button>
            </div>
            
            <!-- 选项卡内容 -->
            <div class="p-6">
                <!-- 智能体管理选项卡 -->
                <div id="agents-tab" class="tab-content active">
                    <div id="agents-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <!-- 智能体卡片将通过JavaScript动态添加 -->
                    </div>
                </div>
                
                <!-- 交互历史选项卡 -->
                <div id="history-tab" class="tab-content hidden">
                    <div id="history-container" class="space-y-4 max-h-[500px] overflow-y-auto">
                        <!-- 交互历史将通过JavaScript动态添加 -->
                    </div>
                </div>
                
                <!-- 系统日志选项卡 -->
                <div id="logs-tab" class="tab-content hidden">
                    <div id="logs-container" class="font-mono text-sm bg-gray-50 p-4 rounded-lg max-h-[500px] overflow-y-auto">
                        <!-- 系统日志将通过JavaScript动态添加 -->
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-base-100 py-4 border-t">
        <div class="container mx-auto px-4 text-center text-neutral">
            <p>&copy; 2024 AI智能体协作系统 | 基于CrewAI和Flask构建</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script>
        // DOM元素
        const statusIndicator = document.getElementById('status-indicator');
        const statusText = document.getElementById('status-text');
        const currentTask = document.getElementById('current-task');
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        const agentsContainer = document.getElementById('agents-container');
        const historyContainer = document.getElementById('history-container');
        const logsContainer = document.getElementById('logs-container');
        const startBtn = document.getElementById('start-btn');
        const refreshBtn = document.getElementById('refresh-btn');
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        // 选项卡切换
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.getAttribute('data-tab');
                
                // 更新按钮状态
                tabBtns.forEach(b => {
                    b.classList.remove('active', 'text-primary', 'border-b-2', 'border-primary');
                    b.classList.add('text-neutral', 'hover:text-primary');
                });
                btn.classList.add('active', 'text-primary', 'border-b-2', 'border-primary');
                btn.classList.remove('text-neutral', 'hover:text-primary');
                
                // 更新内容显示
                tabContents.forEach(content => {
                    content.classList.add('hidden');
                    content.classList.remove('active');
                });
                document.getElementById(`${tabId}-tab`).classList.remove('hidden');
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });

        // 启动智能体
        startBtn.addEventListener('click', () => {
            fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    startBtn.disabled = true;
                    startBtn.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i><span>运行中...</span>';
                    startBtn.classList.remove('bg-primary', 'hover:bg-primary/90');
                    startBtn.classList.add('bg-gray-500');
                }
            });
        });

        // 刷新页面
        refreshBtn.addEventListener('click', () => {
            window.location.reload();
        });

        // 初始化SSE连接
        function initSSE() {
            const eventSource = new EventSource('/api/events');
            
            eventSource.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateUI(data.data);
            };
            
            eventSource.onerror = function(error) {
                console.error('SSE连接错误:', error);
                eventSource.close();
                // 5秒后尝试重新连接
                setTimeout(initSSE, 5000);
            };
        }

        // 更新UI
        function updateUI(data) {
            // 更新状态
            statusText.textContent = getStatusText(data.status);
            updateStatusIndicator(data.status);
            
            // 更新当前任务
            currentTask.textContent = data.current_task || '无';
            
            // 更新进度
            progressBar.style.width = `${data.progress}%`;
            progressText.textContent = `${data.progress}%`;
            
            // 更新智能体列表
            updateAgents(data.agents);
            
            // 更新交互历史
            updateHistory(data.messages);
            
            // 更新系统日志
            appendLog(`[${new Date().toLocaleTimeString()}] 状态: ${data.status}, 进度: ${data.progress}%, 当前任务: ${data.current_task || '无'}`);
            
            // 如果任务完成，启用启动按钮
            if (data.status === 'completed' || data.status === 'failed') {
                startBtn.disabled = false;
                startBtn.innerHTML = '<i class="fa fa-play-circle mr-2"></i><span>启动智能体</span>';
                startBtn.classList.add('bg-primary', 'hover:bg-primary/90');
                startBtn.classList.remove('bg-gray-500');
            }
        }

        // 获取状态文本
        function getStatusText(status) {
            const statusMap = {
                'idle': '就绪',
                'running': '运行中',
                'completed': '已完成',
                'failed': '失败',
                'paused': '已暂停'
            };
            return statusMap[status] || status;
        }

        // 更新状态指示器
        function updateStatusIndicator(status) {
            statusIndicator.className = 'h-3 w-3 rounded-full';
            
            switch(status) {
                case 'running':
                    statusIndicator.classList.add('bg-green-500');
                    statusIndicator.classList.add('animate-pulse');
                    break;
                case 'completed':
                    statusIndicator.classList.add('bg-blue-500');
                    break;
                case 'failed':
                    statusIndicator.classList.add('bg-red-500');
                    break;
                case 'paused':
                    statusIndicator.classList.add('bg-yellow-500');
                    break;
                default:
                    statusIndicator.classList.add('bg-gray-400');
            }
        }

        // 更新智能体列表
        function updateAgents(agents) {
            agentsContainer.innerHTML = '';
            
            agents.forEach(agent => {
                const card = document.createElement('div');
                card.className = 'bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-all-ease';
                
                card.innerHTML = `
                    <div class="flex items-center space-x-3 mb-3">
                        <div class="bg-primary/10 p-2 rounded-full">
                            <i class="fa fa-user-circle text-primary"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-base-content">${agent.name}</h3>
                            <p class="text-sm text-neutral">${agent.role}</p>
                        </div>
                    </div>
                    <p class="text-sm text-neutral mb-3 line-clamp-2">${agent.description || '无描述'}</p>
                    <div class="text-xs text-neutral">
                        <p>任务完成: ${agent.completed_tasks || 0}</p>
                    </div>
                `;
                
                agentsContainer.appendChild(card);
            });
        }

        // 更新交互历史
        function updateHistory(messages) {
            historyContainer.innerHTML = '';
            
            messages.forEach(msg => {
                const messageEl = document.createElement('div');
                messageEl.className = `p-4 rounded-lg ${msg.type === 'agent' ? 'bg-primary/5 border-l-4 border-primary' : 'bg-secondary/5 border-l-4 border-secondary'}`;
                
                const timestamp = new Date(msg.timestamp || Date.now()).toLocaleTimeString();
                
                messageEl.innerHTML = `
                    <div class="flex justify-between items-start mb-2">
                        <span class="font-semibold text-sm">${msg.sender}</span>
                        <span class="text-xs text-neutral">${timestamp}</span>
                    </div>
                    <p class="text-sm">${msg.content}</p>
                `;
                
                historyContainer.appendChild(messageEl);
            });
            
            // 滚动到底部
            historyContainer.scrollTop = historyContainer.scrollHeight;
        }

        // 添加日志
        function appendLog(log) {
            const logEl = document.createElement('div');
            logEl.className = 'py-1 border-b border-gray-200';
            logEl.textContent = log;
            logsContainer.appendChild(logEl);
            
            // 滚动到底部
            logsContainer.scrollTop = logsContainer.scrollHeight;
        }

        // 初始加载数据
        fetch('/api/execution-data')
            .then(response => response.json())
            .then(data => {
                updateUI(data);
                // 初始化SSE连接
                initSSE();
            });
    </script>
</body>
</html>
```

## 系统集成与部署

### 4.1 多智能体与Web界面集成

将多智能体系统与Web界面进行集成，实现完整的系统功能：

```python
# 在Flask应用中添加智能体执行API
@app.route('/api/start', methods=['POST'])
def start_execution():
    """
    启动智能体团队执行任务
    """
    global execution_data
    
    # 更新系统状态
    execution_data = {
        "status": "running",
        "current_task": "准备中...",
        "progress": 0,
        "messages": [],
        "agents": [
            {"name": "产品经理", "role": "产品经理", "description": "负责需求分析和产品规划"},
            {"name": "开发工程师", "role": "开发工程师", "description": "负责技术架构和实现"},
            {"name": "UI设计师", "role": "UI设计师", "description": "负责界面设计和用户体验"},
            {"name": "测试工程师", "role": "测试工程师", "description": "负责测试计划和质量保证"}
        ]
    }
    
    # 创建执行线程
    thread = threading.Thread(target=execute_crew)
    thread.daemon = True
    thread.start()
    
    return jsonify({"success": True, "message": "智能体团队已启动"})

def execute_crew():
    """
    在后台线程中执行智能体团队任务
    """
    global execution_data
    
    try:
        # 执行产品经理任务
        execution_data["current_task"] = "产品需求分析"
        execution_data["progress"] = 25
        execution_data["messages"].append({
            "type": "agent",
            "sender": "产品经理",
            "content": "开始分析产品需求，确定核心功能和用户故事。",
            "timestamp": time.time()
        })
        time.sleep(2)  # 模拟执行时间
        
        # 执行开发工程师任务
        execution_data["current_task"] = "技术架构设计"
        execution_data["progress"] = 50
        execution_data["messages"].append({
            "type": "agent",
            "sender": "开发工程师",
            "content": "基于产品需求，设计系统架构和技术方案。",
            "timestamp": time.time()
        })
        time.sleep(2)  # 模拟执行时间
        
        # 执行UI设计师任务
        execution_data["current_task"] = "UI界面设计"
        execution_data["progress"] = 75
        execution_data["messages"].append({
            "type": "agent",
            "sender": "UI设计师",
            "content": "创建用户界面设计，确保良好的用户体验。",
            "timestamp": time.time()
        })
        time.sleep(2)  # 模拟执行时间
        
        # 执行测试工程师任务
        execution_data["current_task"] = "测试计划制定"
        execution_data["progress"] = 100
        execution_data["messages"].append({
            "type": "agent",
            "sender": "测试工程师",
            "content": "完成测试计划和测试用例设计。",
            "timestamp": time.time()
        })
        time.sleep(2)  # 模拟执行时间
        
        # 任务完成
        execution_data["status"] = "completed"
        execution_data["messages"].append({
            "type": "system",
            "sender": "系统",
            "content": "所有任务已成功完成！",
            "timestamp": time.time()
        })
        
    except Exception as e:
        # 任务失败
        execution_data["status"] = "failed"
        execution_data["messages"].append({
            "type": "system",
            "sender": "系统",
            "content": f"任务执行失败: {str(e)}",
            "timestamp": time.time()
        })
```

### 4.2 完整系统部署

将多智能体系统和Web界面整合为一个完整的应用程序：

1. 创建完整的`crewai_web_app.py`文件，整合所有功能模块
2. 确保端口设置正确，避免端口冲突
3. 启动应用服务器

```bash
python crewai_web_app.py
```

## 使用说明

### 5.1 访问Web界面

启动服务后，通过浏览器访问以下地址：

```
http://localhost:5002
```

### 5.2 启动智能体系统

在Web界面中，点击"启动智能体"按钮开始执行多智能体任务。系统将：

1. 自动初始化并启动四个智能体（产品经理、开发工程师、UI设计师、测试工程师）
2. 按顺序执行产品需求分析、技术架构设计、UI界面设计和测试计划制定任务
3. 实时更新执行进度和状态信息

### 5.3 查看执行结果

在Web界面中，可以通过不同的选项卡查看：

- **智能体管理**：查看所有智能体的信息和状态
- **交互历史**：查看智能体之间的交互记录和对话内容
- **系统日志**：查看系统运行日志和状态更新

### 5.4 API访问

系统提供以下API接口：

- `GET /api/execution-data`：获取当前执行状态和数据
- `POST /api/start`：启动智能体团队执行任务
- `GET /api/events`：通过SSE接收实时更新事件

## 常见问题解决

### 端口占用问题

如果遇到端口被占用的情况，可以修改代码中的端口配置：

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)  # 修改端口号为其他可用端口
```

### 代理配置问题

如果需要通过代理访问API，可以在`.env`文件中设置代理配置：

```env
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

### 模型访问问题

确保正确配置了API密钥和模型地址：

```env
OPENAI_API_KEY=your_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
```

---

通过以上步骤，您已经成功搭建了一个完整的多智能体系统，并集成了Web界面进行可视化展示。系统支持实时数据更新、多智能体协作执行和交互式管理，为AI智能体应用提供了便捷的开发和展示平台。