import os
import time
import logging
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 设置API密钥和代理配置
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
moonshot_model_name = os.getenv("MOONSHOT_MODEL_NAME", "moonshot-v1-8k")

if not moonshot_api_key or moonshot_api_key == "sk-your-actual-api-key-here":
    logger.warning("警告: 未设置有效的Kimi API密钥，请在.env文件中配置您的实际MOONSHOT_API_KEY")
    logger.warning("示例: MOONSHOT_API_KEY=sk-abcdef1234567890abcdef1234567890abcdef1234567890")

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
        return kimi_llm
    except Exception as e:
        logger.error(f"初始化Kimi模型失败: {str(e)}")
        raise

# 初始化模型
kimi_llm = get_kimi_llm()

# 创建产品经理智能体
product_manager = Agent(
    role="产品经理",
    goal="设计一个创新的AI助手产品",
    backstory="你是一位经验丰富的产品经理，擅长将复杂需求转化为清晰的产品规划。",
    verbose=True,
    llm=kimi_llm
)

# 创建开发工程师智能体
developer = Agent(
    role="资深开发工程师",
    goal="实现高质量的AI产品功能",
    backstory="你是一位技术精湛的开发工程师，精通多种编程语言和AI技术栈。",
    verbose=True,
    llm=kimi_llm
)

# 创建UI设计师智能体
designer = Agent(
    role="UI/UX设计师",
    goal="设计美观且易用的产品界面",
    backstory="你是一位创意十足的UI/UX设计师，专注于用户体验和视觉设计。",
    verbose=True,
    llm=kimi_llm
)

# 创建测试工程师智能体
tester = Agent(
    role="测试工程师",
    goal="确保产品质量和稳定性",
    backstory="你是一位细致入微的测试工程师，擅长发现潜在问题并提出改进建议。",
    verbose=True,
    llm=kimi_llm
)

# 定义任务
task1 = Task(
    description="设计一个AI助手产品的功能规划和路线图，包括核心功能、目标用户和市场定位。",
    expected_output="一份详细的产品需求文档，包含功能列表、用户故事和产品路线图。",
    agent=product_manager
)

task2 = Task(
    description="基于产品需求，设计后端系统架构和API接口，选择合适的技术栈。",
    expected_output="技术架构文档，包含系统设计图、API规范和技术选型说明。",
    agent=developer,
    context=[task1]
)

task3 = Task(
    description="设计产品的用户界面和交互流程，创建关键页面的设计稿。",
    expected_output="UI设计稿和交互流程图，包含色彩方案和组件库建议。",
    agent=designer,
    context=[task1]
)

task4 = Task(
    description="制定全面的测试计划，包括功能测试、性能测试和用户体验测试。",
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

# 运行团队
if __name__ == "__main__":
    print("启动多智能体协作系统 (使用Kimi大模型)...")
    print(f"当前使用模型: {moonshot_model_name}")
    print("提示: 如果遇到连接问题，请检查：")
    print("1. .env文件中是否设置了有效的Kimi API密钥 (MOONSHOT_API_KEY)")
    print("2. 是否需要配置代理环境变量：HTTP_PROXY和HTTPS_PROXY")
    print("3. 网络连接是否稳定\n")
    
    max_retries = 3
    retry_count = 0
    result = None
    
    while retry_count < max_retries:
        try:
            result = crew.kickoff()
            break  # 成功执行，退出重试循环
        except Exception as e:
            retry_count += 1
            error_msg = str(e)
            logger.error(f"执行出错 (第{retry_count}/{max_retries}次尝试): {error_msg}")
            
            # 提供更友好的错误提示
            if "timeout" in error_msg.lower():
                print(f"\n错误: 连接超时，请检查网络连接或API密钥是否正确")
                print("提示: 如果您在需要代理的环境中，可以在.env文件中添加代理配置：")
                print("HTTP_PROXY=http://your-proxy-server:port")
                print("HTTPS_PROXY=http://your-proxy-server:port")
            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                print(f"\n错误: API密钥认证失败，请检查.env文件中的API密钥是否正确")
            
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # 指数退避
                print(f"\n{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print("\n已达到最大重试次数，请解决上述问题后重试")
    
    if result:
        print("\n任务完成！以下是协作结果：")
        print(result)