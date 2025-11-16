from flask import Flask, render_template_string, jsonify
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 模拟执行结果数据（从terminal输出生成）
execution_data = {
    "execution_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
    "start_time": "2025-11-15 21:37:53",
    "model": "moonshot-v1-8k",
    "agents": [
        {
            "name": "产品经理",
            "role": "设计产品功能和路线图",
            "tasks": [
                {
                    "description": "设计一个AI助手产品的功能规划和路线图，包括核心功能、目标用户和市场定位。",
                    "output": "一份详细的产品需求文档，包含功能列表、用户故事和产品路线图。\n\n核心功能规划：\n- 自然语言处理（NLP）模块：用于语言理解、意图识别和实体提取。\n- 对话管理器：管理对话流程，选择合适的响应策略。\n- 用户习惯学习模块：通过机器学习算法分析用户行为，个性化助手功能。\n- 知识库和推荐系统：存储相关信息，并提供个性化推荐。\n- 集成开发环境（IDE）：统一平台，用于构建、测试和部署AI模型。\n- API和微服务架构：确保系统可扩展性和模块化。\n- 数据管理和隐私保护：确保用户数据安全和符合数据隐私法规。\n- 语音和视觉交互能力：可选模块，增强交互体验。\n- 监控和日志系统：跟踪系统性能和用户反馈，持续改进。"
                }
            ]
        },
        {
            "name": "资深开发工程师",
            "role": "设计后端架构",
            "tasks": [
                {
                    "description": "基于产品需求，设计后端系统架构和API接口，选择合适的技术栈。",
                    "output": "后端系统架构设计正在进行中..."
                }
            ]
        },
        {
            "name": "UI/UX设计师",
            "role": "设计用户界面",
            "tasks": [
                {
                    "description": "设计AI助手产品的用户界面和体验设计",
                    "output": "设计AI助手产品的用户界面和体验时，应注意以下要素：\n\n1. 简洁明了的布局：界面应简洁，避免过多复杂的元素，让用户能够快速找到所需功能。\n2. 一致性：保持统一的设计风格和交互模式，减少用户的学习成本。\n3. 可访问性：确保界面对所有用户（包括色盲、视力不佳等）都易于使用。\n4. 反馈机制：提供清晰的反馈，让用户知道他们的操作已被系统识别和处理。\n5. 适应性：界面应能适应不同屏幕尺寸和分辨率，确保在各种设备上都能提供良好的体验。"
                }
            ]
        },
        {
            "name": "测试工程师",
            "role": "制定测试计划",
            "tasks": [
                {
                    "description": "制定AI助手产品的测试计划和测试用例",
                    "output": "[AI助手产品测试计划和测试用例]\n\n测试计划：\n- 测试目标：确保AI助手产品的功能全面覆盖和用户习惯学习模块的准确性。\n- 测试范围：覆盖所有AI助手的核心功能，如语音识别、语义理解、智能推荐等。\n- 测试类型：包括功能测试、性能测试、兼容性测试、安全性测试等。\n- 测试周期：根据项目进度制定详细的测试周期和里程碑。\n- 测试资源：明确测试人员分工、测试环境搭建、测试工具准备等。\n- 风险评估：识别可能的风险因素，并制定相应的应对措施。\n\n测试用例：\n- 功能测试用例：针对AI助手的每个功能点编写详细的测试用例，包括正向测试和异常测试。\n- 性能测试用例：评估AI助手在不同负载下的性能表现，如响应时间、并发处理能力等。\n- 兼容性测试用例：测试AI助手在不同操作系统、浏览器、设备上的兼容性表现。\n- 安全性测试用例：检查AI助手在数据传输、存储、处理等环节的安全防护措施。\n- 用户习惯学习测试用例：模拟用户使用AI助手的过程，验证学习模块的准确性和效果。"
                }
            ]
        }
    ],
    "agent_interactions": [
        {
            "from_agent": "产品经理",
            "to_agent": "资深开发工程师",
            "content": "设计AI助手产品的核心技术架构",
            "timestamp": "2025-11-15 21:37:57"
        },
        {
            "from_agent": "产品经理",
            "to_agent": "UI/UX设计师",
            "content": "AI助手产品的用户界面和体验设计应注意哪些要素？",
            "timestamp": "2025-11-15 21:38:06"
        },
        {
            "from_agent": "产品经理",
            "to_agent": "测试工程师",
            "content": "制定AI助手产品的测试计划和测试用例",
            "timestamp": "2025-11-15 21:38:16"
        },
        {
            "from_agent": "资深开发工程师",
            "to_agent": "产品经理",
            "content": "设计后端系统架构和API接口",
            "timestamp": "2025-11-15 21:38:38"
        }
    ],
    "system_logs": [
        "2025-11-15 21:37:53 - INFO - 正在初始化Kimi模型: moonshot-v1-8k",
        "2025-11-15 21:37:53 - INFO - Kimi模型初始化成功",
        "2025-11-15 21:37:56 - INFO - HTTP Request: POST https://api.moonshot.cn/v1/chat/completions \"HTTP/1.1 200 OK\"",
        "2025-11-15 21:38:49 - ERROR - 执行出错 (第1/3次尝试): Error code: 429 - {'error': {'message': 'Your account request reached organization max RPM: 20'}}"
    ]
}

# 首页 - 显示执行结果
def index():
    html_template = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI智能体协作系统 - 执行结果</title>
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
                        执行ID: {{ execution_data.execution_id }}
                    </span>
                    <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {{ execution_data.model }}
                    </span>
                </div>
            </div>
        </nav>

        <!-- 主要内容 -->
        <main class="container mx-auto pt-24 pb-16 px-4">
            <!-- 系统概览 -->
            <section class="mb-12">
                <div class="bg-gradient-to-r from-primary/10 to-accent/10 rounded-2xl p-6 shadow-lg">
                    <h2 class="text-2xl font-bold mb-4">系统执行概览</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div class="bg-white rounded-xl p-4 shadow">
                            <div class="flex items-center space-x-3">
                                <div class="bg-primary/20 p-2 rounded-lg">
                                    <i class="fa fa-clock-o text-primary text-xl"></i>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500">开始时间</p>
                                    <p class="font-semibold">{{ execution_data.start_time }}</p>
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
                                    <p class="font-semibold">{{ execution_data.agents|length }}</p>
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
                                    <p class="font-semibold">{{ execution_data.agent_interactions|length }}</p>
                                </div>
                            </div>
                        </div>
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
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
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
                    <div class="divide-y">
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
                    <div class="p-4 max-h-96 overflow-y-auto">
                        <ul class="space-y-2 text-sm">
                            {% for log in execution_data.system_logs %}
                            <li class="p-2 rounded-lg {% if 'ERROR' in log %}bg-red-50 text-red-800{% elif 'INFO' in log %}bg-blue-50 text-blue-800{% else %}bg-gray-50{% endif %}">
                                {{ log }}
                            </li>
                            {% endfor %}
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

            // 添加简单的动画效果
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.card-hover');
                cards.forEach((card, index) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 100 + index * 100);
                });
            });
        </script>
    </body>
    </html>
    '''
    return render_template_string(html_template, execution_data=execution_data)

# API - 获取执行数据
def get_execution_data():
    return jsonify(execution_data)

# 配置路由
app.add_url_rule('/', 'index', index)
app.add_url_rule('/api/execution-data', 'get_execution_data', get_execution_data)

if __name__ == '__main__':
    # 从环境变量读取配置，默认使用端口5001
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"\nAI智能体协作系统UI已启动！")
    print(f"访问地址: http://localhost:{port}")
    print(f"API地址: http://localhost:{port}/api/execution-data")
    print("按 Ctrl+C 停止服务\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)