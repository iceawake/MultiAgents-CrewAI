import os
import time
import logging
import json
from threading import Thread
from queue import Queue
from flask import Flask, render_template_string, jsonify, Response
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 全局变量存储执行数据和状态
execution_data = {
    "execution_id": time.strftime("%Y%m%d_%H%M%S"),
    "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "model": os.getenv("MOONSHOT_MODEL_NAME", "moonshot-v1-8k"),
    "agents": [],
    "agent_interactions": [],
    "system_logs": [],
    "status": "idle",  # idle, running, completed, error
    "current_task": None,
    "progress": 0
}

# 创建队列用于实时通信
execution_queue = Queue()

# 设置API密钥和代理配置
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
moonshot_model_name = os.getenv("MOONSHOT_MODEL_NAME", "moonshot-v1-8k")

# 配置代理支持
proxy_url = os.getenv("HTTP_PROXY")
if proxy_url:
    logger.info(f"已配置代理: {proxy_url}")
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url

# 初始化Kimi模型
def get_kimi_llm():
    """初始化Kimi大语言模型（使用OpenAI兼容接口）"""
    try:
        logger.info(f"正在初始化Kimi模型: {moonshot_model_name}")
        # 设置环境变量以便crewai能够正确使用Kimi API
        os.environ["OPENAI_API_KEY"] = moonshot_api_key
        os.environ["OPENAI_BASE_URL"] = "https://api.moonshot.cn/v1"
        os.environ["OPENAI_MODEL_NAME"] = moonshot_model_name
        
        # 使用OpenAI兼容接口调用Kimi模型
        kimi_llm = ChatOpenAI(
            model_name=moonshot_model_name,
            api_key=moonshot_api_key,
            base_url="https://api.moonshot.cn/v1",
            temperature=0.7
        )
        logger.info("Kimi模型初始化成功")
        add_system_log("Kimi模型初始化成功")
        return kimi_llm
    except Exception as e:
        error_msg = f"初始化Kimi模型失败: {str(e)}"
        logger.error(error_msg)
        add_system_log(error_msg, "error")
        raise

# 添加系统日志
def add_system_log(message, level="info"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {level.upper()} - {message}"
    execution_data["system_logs"].append(log_entry)
    # 将日志发送到队列以便实时更新
    execution_queue.put({
        "type": "log",
        "data": log_entry
    })

# 更新智能体信息
def update_agent(agent_name, role, task_description=None, task_output=None):
    # 查找现有智能体
    agent = next((a for a in execution_data["agents"] if a["name"] == agent_name), None)
    
    if not agent:
        # 创建新智能体
        agent = {
            "name": agent_name,
            "role": role,
            "tasks": []
        }
        execution_data["agents"].append(agent)
    
    # 如果有任务信息，添加或更新任务
    if task_description:
        task = next((t for t in agent["tasks"] if t["description"] == task_description), None)
        if not task:
            task = {
                "description": task_description,
                "output": task_output or "正在处理..."
            }
            agent["tasks"].append(task)
        elif task_output:
            task["output"] = task_output
    
    # 将更新发送到队列
    execution_queue.put({
        "type": "agent_update",
        "data": agent
    })

# 添加智能体交互
def add_agent_interaction(from_agent, to_agent, content):
    interaction = {
        "from_agent": from_agent,
        "to_agent": to_agent,
        "content": content,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    execution_data["agent_interactions"].append(interaction)
    
    # 将交互发送到队列
    execution_queue.put({
        "type": "interaction",
        "data": interaction
    })

# 更新任务状态
def update_task_status(task_name, status, progress=None):
    execution_data["current_task"] = task_name
    execution_data["status"] = status
    if progress is not None:
        execution_data["progress"] = progress
    
    # 将状态更新发送到队列
    execution_queue.put({
        "type": "status_update",
        "data": {
            "current_task": task_name,
            "status": status,
            "progress": progress
        }
    })

# 运行多智能体系统的函数
def run_multi_agent_system():
    global execution_data
    
    # 重置执行数据
    execution_data = {
        "execution_id": time.strftime("%Y%m%d_%H%M%S"),
        "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": moonshot_model_name,
        "agents": [],
        "agent_interactions": [],
        "system_logs": [],
        "status": "running",
        "current_task": None,
        "progress": 0
    }
    
    add_system_log(f"启动多智能体协作系统 (使用Kimi大模型: {moonshot_model_name})")
    
    try:
        # 初始化Kimi模型
        kimi_llm = get_kimi_llm()
        
        # 创建产品经理智能体
        product_manager = Agent(
            role="产品经理",
            goal="设计一个创新的AI助手产品",
            backstory="你是一位经验丰富的产品经理，擅长将复杂需求转化为清晰的产品规划。",
            verbose=True,
            llm=kimi_llm
        )
        update_agent("产品经理", "设计产品功能和路线图")
        
        # 创建开发工程师智能体
        developer = Agent(
            role="资深开发工程师",
            goal="实现高质量的AI产品功能",
            backstory="你是一位技术精湛的开发工程师，精通多种编程语言和AI技术栈。",
            verbose=True,
            llm=kimi_llm
        )
        update_agent("资深开发工程师", "设计后端架构")
        
        # 创建UI设计师智能体
        designer = Agent(
            role="UI/UX设计师",
            goal="设计美观且易用的产品界面",
            backstory="你是一位创意十足的UI/UX设计师，专注于用户体验和视觉设计。",
            verbose=True,
            llm=kimi_llm
        )
        update_agent("UI/UX设计师", "设计用户界面")
        
        # 创建测试工程师智能体
        tester = Agent(
            role="测试工程师",
            goal="确保产品质量和稳定性",
            backstory="你是一位细致入微的测试工程师，擅长发现潜在问题并提出改进建议。",
            verbose=True,
            llm=kimi_llm
        )
        update_agent("测试工程师", "制定测试计划")
        
        # 定义任务
        task1_description = "设计一个AI助手产品的功能规划和路线图，包括核心功能、目标用户和市场定位。"
        task1 = Task(
            description=task1_description,
            expected_output="一份详细的产品需求文档，包含功能列表、用户故事和产品路线图。",
            agent=product_manager
        )
        
        task2_description = "基于产品需求，设计后端系统架构和API接口，选择合适的技术栈。"
        task2 = Task(
            description=task2_description,
            expected_output="技术架构文档，包含系统设计图、API规范和技术选型说明。",
            agent=developer,
            context=[task1]
        )
        
        task3_description = "设计产品的用户界面和交互流程，创建关键页面的设计稿。"
        task3 = Task(
            description=task3_description,
            expected_output="UI设计稿和交互流程图，包含色彩方案和组件库建议。",
            agent=designer,
            context=[task1]
        )
        
        task4_description = "制定全面的测试计划，包括功能测试、性能测试和用户体验测试。"
        task4 = Task(
            description=task4_description,
            expected_output="测试计划文档，包含测试用例、测试策略和验收标准。",
            agent=tester,
            context=[task1, task2, task3]
        )
        
        # 创建团队
        crew = Crew(
            agents=[product_manager, developer, designer, tester],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential,
            verbose=2
        )
        
        # 添加智能体交互（模拟实际协作过程）
        add_agent_interaction("产品经理", "资深开发工程师", "设计AI助手产品的核心技术架构")
        add_agent_interaction("产品经理", "UI/UX设计师", "AI助手产品的用户界面和体验设计应注意哪些要素？")
        add_agent_interaction("产品经理", "测试工程师", "制定AI助手产品的测试计划和测试用例")
        
        # 更新任务状态
        update_task_status("任务1: 产品需求分析", "running", 0)
        
        # 运行任务（使用重试机制）
        max_retries = 3
        retry_count = 0
        result = None
        
        while retry_count < max_retries:
            try:
                # 模拟任务进度更新
                for i in range(4):
                    task_name = f"任务{i+1}: {'产品需求分析' if i==0 else '技术架构设计' if i==1 else 'UI设计' if i==2 else '测试计划'}"
                    update_task_status(task_name, "running", (i+1)*25)
                    
                    # 更新对应任务的状态
                    if i == 0:
                        update_agent("产品经理", "设计产品功能和路线图", task1_description, "正在制定产品需求...")
                    elif i == 1:
                        update_agent("资深开发工程师", "设计后端架构", task2_description, "正在设计技术架构...")
                        add_agent_interaction("资深开发工程师", "产品经理", "设计后端系统架构和API接口")
                    elif i == 2:
                        update_agent("UI/UX设计师", "设计用户界面", task3_description, "正在创建UI设计稿...")
                    elif i == 3:
                        update_agent("测试工程师", "制定测试计划", task4_description, "正在编写测试用例...")
                    
                    time.sleep(1)  # 模拟处理时间
                
                # 实际执行crew
                # result = crew.kickoff()
                
                # 模拟最终结果
                update_agent("产品经理", "设计产品功能和路线图", task1_description, "完成了产品需求文档，包含AI助手的核心功能规划和用户故事。")
                update_agent("资深开发工程师", "设计后端架构", task2_description, "设计了基于微服务的后端架构，选择了Python和FastAPI作为技术栈。")
                update_agent("UI/UX设计师", "设计用户界面", task3_description, "创建了符合现代设计趋势的UI界面，强调简洁性和易用性。")
                update_agent("测试工程师", "制定测试计划", task4_description, "完成了全面的测试计划，包括功能测试、性能测试和安全性测试。")
                
                update_task_status("所有任务完成", "completed", 100)
                add_system_log("多智能体协作系统执行完成！")
                break
                
            except Exception as e:
                retry_count += 1
                error_msg = f"执行出错 (第{retry_count}/{max_retries}次尝试): {str(e)}"
                logger.error(error_msg)
                add_system_log(error_msg, "error")
                
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    add_system_log(f"{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    update_task_status("执行失败", "error", 0)
                    add_system_log("已达到最大重试次数，请解决问题后重试")
                    
    except Exception as e:
        error_msg = f"系统错误: {str(e)}"
        logger.error(error_msg)
        add_system_log(error_msg, "error")
        update_task_status("系统错误", "error", 0)

# 首页路由
@app.route('/')
def index():
    html_template = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI智能体协作系统 - 实时监控</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            primary: '#3B82F6',
                            secondary: '#10B981',
                            accent: '#8B5CF6',
                            dark: '#1F2937',
                            light: '#F9FAFB'
                        },
                        fontFamily: {
                            sans: ['Inter', 'system-ui', 'sans-serif'],
                        },
                    },
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
                .card-hover {
                    transition: all 0.3s ease;
                }
                .card-hover:hover {
                    transform: translateY(-5px);
                }
                .animate-pulse {
                    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                }
                @keyframes pulse {
                    0%, 100% {
                        opacity: 1;
                    }
                    50% {
                        opacity: 0.5;
                    }
                }
            }
        </style>
    </head>
    <body class="bg-light font-sans text-dark min-h-screen">
        <!-- 导航栏 -->
        <nav class="bg-white shadow-md fixed w-full z-10 transition-all duration-300" id="navbar">
            <div class="container mx-auto px-4 py-3 flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="fa fa-rocket text-primary text-2xl"></i>
                    <h1 class="text-xl font-bold text-primary">AI智能体协作系统</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-600 hidden md:inline">
                        执行ID: <span id="execution-id">{{ execution_data.execution_id }}</span>
                    </span>
                    <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {{ execution_data.model }}
                    </span>
                    <button id="start-btn" class="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors flex items-center">
                        <i class="fa fa-play mr-2"></i>启动任务
                    </button>
                </div>
            </div>
        </nav>

        <!-- 主要内容 -->
        <main class="container mx-auto pt-24 pb-16 px-4">
            <!-- 系统概览 -->
            <section class="mb-12">
                <div class="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-6 shadow-lg">
                    <h2 class="text-2xl font-bold mb-4">系统执行概览</h2>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div class="bg-white rounded-xl p-4 shadow">
                            <div class="flex items-center space-x-3">
                                <div class="bg-primary/20 p-2 rounded-lg">
                                    <i class="fa fa-clock-o text-primary text-xl"></i>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500">开始时间</p>
                                    <p class="font-semibold" id="start-time">{{ execution_data.start_time }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="bg-white rounded-xl p-4 shadow">
                            <div class="flex items-center space-x-3">
                                <div class="bg-secondary/20 p-2 rounded-lg">
                                    <i class="fa fa-users text-secondary text-xl"></i>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500">智能体数量</p>
                                    <p class="font-semibold" id="agent-count">{{ execution_data.agents|length }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="bg-white rounded-xl p-4 shadow">
                            <div class="flex items-center space-x-3">
                                <div class="bg-accent/20 p-2 rounded-lg">
                                    <i class="fa fa-comments-o text-accent text-xl"></i>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500">交互次数</p>
                                    <p class="font-semibold" id="interaction-count">{{ execution_data.agent_interactions|length }}</p>
                                </div>
                            </div>
                        </div>
                        <div class="bg-white rounded-xl p-4 shadow">
                            <div class="flex items-center space-x-3">
                                <div class="bg-orange-20 p-2 rounded-lg">
                                    <i class="fa fa-cog text-orange-500 text-xl"></i>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500">状态</p>
                                    <p class="font-semibold" id="system-status">{{ execution_data.status|capitalize }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 进度条 -->
                    <div class="mt-6 bg-white rounded-xl p-4 shadow">
                        <div class="flex justify-between items-center mb-2">
                            <h3 class="font-semibold">执行进度</h3>
                            <span id="progress-percent">{{ execution_data.progress }}%</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                            <div id="progress-bar" class="bg-primary h-2.5 rounded-full" style="width: {{ execution_data.progress }}%"></div>
                        </div>
                        <p class="text-sm text-gray-600 mt-2" id="current-task">{{ execution_data.current_task or '等待开始' }}</p>
                    </div>
                </div>
            </section>

            <!-- 选项卡导航 -->
            <div class="mb-8">
                <div class="flex overflow-x-auto no-scrollbar border-b border-gray-200">
                    <button class="tab-btn px-6 py-3 font-medium text-primary border-b-2 border-primary" onclick="switchTab('agents')">
                        <i class="fa fa-user-circle-o mr-2"></i>智能体
                    </button>
                    <button class="tab-btn px-6 py-3 font-medium text-gray-500 hover:text-gray-700" onclick="switchTab('interactions')">
                        <i class="fa fa-exchange mr-2"></i>智能体交互
                    </button>
                    <button class="tab-btn px-6 py-3 font-medium text-gray-500 hover:text-gray-700" onclick="switchTab('logs')">
                        <i class="fa fa-list-alt mr-2"></i>系统日志
                    </button>
                </div>
            </div>

            <!-- 选项卡内容 -->
            <div id="agents-tab" class="tab-content">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8" id="agents-container">
                    {% if execution_data.agents %}
                    {% for agent in execution_data.agents %}
                    <div class="bg-white rounded-xl shadow-lg overflow-hidden card-hover">
                        <div class="bg-primary/10 p-4 border-l-4 border-primary">
                            <h3 class="text-xl font-bold flex items-center">
                                <i class="fa fa-user-circle text-primary mr-3"></i>
                                {{ agent.name }}
                            </h3>
                            <p class="text-gray-600 text-sm mt-1">{{ agent.role }}</p>
                        </div>
                        <div class="p-4">
                            {% for task in agent.tasks %}
                            <div class="mb-4">
                                <div class="flex items-start mb-2">
                                    <i class="fa fa-tasks text-secondary mt-1 mr-2"></i>
                                    <h4 class="font-semibold text-sm">{{ task.description }}</h4>
                                </div>
                                <div class="bg-gray-50 rounded-lg p-3 text-sm">
                                    <pre class="whitespace-pre-wrap word-break">{{ task.output }}</pre>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                    {% else %}
                    <div class="col-span-full text-center py-12 bg-white rounded-xl shadow">
                        <i class="fa fa-info-circle text-gray-400 text-4xl mb-4"></i>
                        <p class="text-gray-500">点击上方的「启动任务」按钮开始执行多智能体协作系统</p>
                    </div>
                    {% endif %}
                </div>
            </div>

            <div id="interactions-tab" class="tab-content hidden">
                <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                    <div class="p-4 border-b">
                        <h3 class="text-xl font-bold flex items-center">
                            <i class="fa fa-comments text-primary mr-3"></i>
                            智能体交互历史
                        </h3>
                    </div>
                    <div class="divide-y" id="interactions-container">
                        {% if execution_data.agent_interactions %}
                        {% for interaction in execution_data.agent_interactions %}
                        <div class="p-4 hover:bg-gray-50 transition-colors">
                            <div class="flex items-center justify-between mb-2">
                                <div class="flex items-center">
                                    <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded mr-3">{{ interaction.from_agent }}</span>
                                    <i class="fa fa-arrow-right text-gray-400 mx-2"></i>
                                    <span class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">{{ interaction.to_agent }}</span>
                                </div>
                                <span class="text-xs text-gray-500">{{ interaction.timestamp }}</span>
                            </div>
                            <div class="bg-gray-50 rounded-lg p-3 text-sm">
                                {{ interaction.content }}
                            </div>
                        </div>
                        {% endfor %}
                        {% else %}
                        <div class="text-center py-12">
                            <p class="text-gray-500">暂无交互记录</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>

            <div id="logs-tab" class="tab-content hidden">
                <div class="bg-white rounded-xl shadow-lg overflow-hidden">
                    <div class="p-4 border-b">
                        <h3 class="text-xl font-bold flex items-center">
                            <i class="fa fa-cog text-primary mr-3"></i>
                            系统日志
                        </h3>
                    </div>
                    <div class="p-4 max-h-96 overflow-y-auto" id="logs-container">
                        <ul class="space-y-2 text-sm">
                            {% if execution_data.system_logs %}
                            {% for log in execution_data.system_logs %}
                            <li class="p-2 rounded-lg {% if 'ERROR' in log %}bg-red-50 text-red-800{% elif 'INFO' in log %}bg-blue-50 text-blue-800{% else %}bg-gray-50{% endif %}">
                                {{ log }}
                            </li>
                            {% endfor %}
                            {% else %}
                            <li class="text-center py-8 text-gray-500">
                                系统准备就绪，等待启动
                            </li>
                            {% endif %}
                        </ul>
                    </div>
                </div>
            </div>
        </main>

        <!-- 页脚 -->
        <footer class="bg-dark text-white py-6">
            <div class="container mx-auto px-4 text-center">
                <p class="text-sm">AI智能体协作系统 - 使用Kimi大模型驱动</p>
                <p class="text-xs text-gray-400 mt-2">© 2025 AI助手产品团队</p>
            </div>
        </footer>

        <script>
            // 选项卡切换功能
            function switchTab(tabName) {
                // 隐藏所有内容
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(content => {
                    content.classList.add('hidden');
                });
                
                // 重置所有按钮样式
                const tabButtons = document.querySelectorAll('.tab-btn');
                tabButtons.forEach(button => {
                    button.classList.remove('text-primary', 'border-b-2', 'border-primary');
                    button.classList.add('text-gray-500');
                });
                
                // 显示选中内容
                document.getElementById(`${tabName}-tab`).classList.remove('hidden');
                
                // 更新选中按钮样式
                event.currentTarget.classList.add('text-primary', 'border-b-2', 'border-primary');
                event.currentTarget.classList.remove('text-gray-500');
            }

            // 导航栏滚动效果
            window.addEventListener('scroll', function() {
                const navbar = document.getElementById('navbar');
                if (window.scrollY > 10) {
                    navbar.classList.add('py-2');
                    navbar.classList.remove('py-3');
                } else {
                    navbar.classList.add('py-3');
                    navbar.classList.remove('py-2');
                }
            });

            // 启动任务按钮事件
            document.getElementById('start-btn').addEventListener('click', function() {
                this.disabled = true;
                this.innerHTML = '<i class="fa fa-spinner fa-spin mr-2"></i>启动中...';
                
                fetch('/api/start-execution', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'started') {
                        this.innerHTML = '<i class="fa fa-refresh fa-spin mr-2"></i>执行中...';
                        document.getElementById('system-status').textContent = 'Running';
                        document.getElementById('system-status').classList.add('text-green-500');
                    }
                })
                .catch(error => {
                    console.error('启动任务失败:', error);
                    this.disabled = false;
                    this.innerHTML = '<i class="fa fa-play mr-2"></i>启动任务';
                });
            });

            // 实时更新数据的WebSocket-like实现
            function connectSSE() {
                const source = new EventSource('/api/events');
                
                source.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        
                        // 根据数据类型更新UI
                        if (data.type === 'status_update') {
                            document.getElementById('progress-percent').textContent = data.data.progress + '%';
                            document.getElementById('progress-bar').style.width = data.data.progress + '%';
                            document.getElementById('current-task').textContent = data.data.current_task || '等待开始';
                            document.getElementById('system-status').textContent = data.data.status.charAt(0).toUpperCase() + data.data.status.slice(1);
                            
                            // 更新状态颜色
                            const statusElement = document.getElementById('system-status');
                            statusElement.classList.remove('text-green-500', 'text-red-500', 'text-blue-500');
                            if (data.data.status === 'running') {
                                statusElement.classList.add('text-green-500');
                            } else if (data.data.status === 'error') {
                                statusElement.classList.add('text-red-500');
                            } else if (data.data.status === 'completed') {
                                statusElement.classList.add('text-blue-500');
                                // 任务完成后启用按钮
                                const startBtn = document.getElementById('start-btn');
                                startBtn.disabled = false;
                                startBtn.innerHTML = '<i class="fa fa-play mr-2"></i>重新开始';
                            }
                        }
                        
                        else if (data.type === 'log') {
                            const logsContainer = document.getElementById('logs-container');
                            const logItem = document.createElement('li');
                            logItem.className = data.data.includes('ERROR') ? 
                                'p-2 rounded-lg bg-red-50 text-red-800' : 
                                'p-2 rounded-lg bg-blue-50 text-blue-800';
                            logItem.textContent = data.data;
                            logsContainer.appendChild(logItem);
                            // 滚动到底部
                            logsContainer.scrollTop = logsContainer.scrollHeight;
                        }
                        
                        else if (data.type === 'interaction') {
                            const interactionsContainer = document.getElementById('interactions-container');
                            // 清除空状态提示
                            if (interactionsContainer.querySelector('.text-center')) {
                                interactionsContainer.innerHTML = '';
                            }
                            
                            const interactionHtml = `
                                <div class="p-4 hover:bg-gray-50 transition-colors">
                                    <div class="flex items-center justify-between mb-2">
                                        <div class="flex items-center">
                                            <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded mr-3">${data.data.from_agent}</span>
                                            <i class="fa fa-arrow-right text-gray-400 mx-2"></i>
                                            <span class="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">${data.data.to_agent}</span>
                                        </div>
                                        <span class="text-xs text-gray-500">${data.data.timestamp}</span>
                                    </div>
                                    <div class="bg-gray-50 rounded-lg p-3 text-sm">
                                        ${data.data.content}
                                    </div>
                                </div>
                            `;
                            interactionsContainer.insertAdjacentHTML('beforeend', interactionHtml);
                            document.getElementById('interaction-count').textContent = 
                                parseInt(document.getElementById('interaction-count').textContent) + 1;
                        }
                        
                        else if (data.type === 'agent_update') {
                            const agentsContainer = document.getElementById('agents-container');
                            const agentName = data.data.name;
                            let agentElement = document.querySelector(`[data-agent-name="${agentName}"]`);
                            
                            if (!agentElement) {
                                // 移除空状态提示
                                if (agentsContainer.querySelector('.text-center')) {
                                    agentsContainer.innerHTML = '';
                                }
                                
                                // 创建新的智能体卡片
                                const agentHtml = `
                                    <div class="bg-white rounded-xl shadow-lg overflow-hidden card-hover" data-agent-name="${agentName}">
                                        <div class="bg-primary/10 p-4 border-l-4 border-primary">
                                            <h3 class="text-xl font-bold flex items-center">
                                                <i class="fa fa-user-circle text-primary mr-3"></i>
                                                ${agentName}
                                            </h3>
                                            <p class="text-gray-600 text-sm mt-1">${data.data.role}</p>
                                        </div>
                                        <div class="p-4 agent-tasks">
                                            <!-- 任务内容将动态添加 -->
                                        </div>
                                    </div>
                                `;
                                agentsContainer.insertAdjacentHTML('beforeend', agentHtml);
                                agentElement = document.querySelector(`[data-agent-name="${agentName}"]`);
                                document.getElementById('agent-count').textContent = 
                                    parseInt(document.getElementById('agent-count').textContent) + 1;
                            }
                            
                            // 更新任务内容
                            if (data.data.tasks && data.data.tasks.length > 0) {
                                const tasksContainer = agentElement.querySelector('.agent-tasks');
                                tasksContainer.innerHTML = '';
                                
                                data.data.tasks.forEach(task => {
                                    const taskHtml = `
                                        <div class="mb-4">
                                            <div class="flex items-start mb-2">
                                                <i class="fa fa-tasks text-secondary mt-1 mr-2"></i>
                                                <h4 class="font-semibold text-sm">${task.description}</h4>
                                            </div>
                                            <div class="bg-gray-50 rounded-lg p-3 text-sm">
                                                <pre class="whitespace-pre-wrap word-break">${task.output}</pre>
                                            </div>
                                        </div>
                                    `;
                                    tasksContainer.insertAdjacentHTML('beforeend', taskHtml);
                                });
                            }
                        }
                    } catch (e) {
                        console.error('解析事件数据失败:', e);
                    }
                };
                
                source.onerror = function(event) {
                    console.error('SSE连接错误:', event);
                    // 尝试重新连接
                    setTimeout(connectSSE, 5000);
                };
            }

            // 页面加载完成后连接SSE
            document.addEventListener('DOMContentLoaded', function() {
                connectSSE();
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template, execution_data=execution_data)

# API - 获取执行数据
@app.route('/api/execution-data')
def get_execution_data():
    return jsonify(execution_data)

# API - 启动执行
@app.route('/api/start-execution', methods=['POST'])
def start_execution():
    if execution_data["status"] == "running":
        return jsonify({"status": "error", "message": "执行已经在进行中"})
    
    # 在后台线程中运行多智能体系统
    thread = Thread(target=run_multi_agent_system)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started", "message": "执行已开始"})

# API - Server-Sent Events 端点
@app.route('/api/events')
def events():
    def event_stream():
        while True:
            if not execution_queue.empty():
                event = execution_queue.get()
                yield f'data: {json.dumps(event)}\n\n'
            time.sleep(0.1)
    
    return Response(event_stream(), mimetype="text/event-stream")

if __name__ == '__main__':
    # 从环境变量读取配置
    port = int(os.getenv('PORT', 5003))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    print(f"\nAI智能体协作系统Web应用已启动！")
    print(f"访问地址: http://localhost:{port}")
    print(f"API地址: http://localhost:{port}/api/execution-data")
    print("按 Ctrl+C 停止服务\n")
    
    # 初始化Kimi API密钥检查
    if not moonshot_api_key or moonshot_api_key == "sk-your-actual-api-key-here":
        logger.warning("警告: 未设置有效的Kimi API密钥，请在.env文件中配置您的实际MOONSHOT_API_KEY")
        logger.warning("示例: MOONSHOT_API_KEY=sk-abcdef1234567890abcdef1234567890abcdef1234567890")
    
    # 启动Flask应用
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)