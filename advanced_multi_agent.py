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

# 创建专业领域专家智能体
researcher = Agent(
    role="AI研究员",
    goal="深入研究前沿AI技术并提供创新解决方案",
    backstory="你是一位在人工智能领域拥有10年经验的资深研究员，发表过20+篇学术论文。",
    verbose=True,
    allow_delegation=True,
    llm=kimi_llm
)

content_strategist = Agent(
    role="内容策略专家",
    goal="创建有影响力的AI产品内容策略",
    backstory="你曾在多家科技公司担任内容总监，擅长将复杂技术转化为吸引人的内容。",
    verbose=True,
    allow_delegation=True,
    llm=kimi_llm
)

marketing_expert = Agent(
    role="市场营销专家",
    goal="制定有效的产品推广策略",
    backstory="你是一位屡获殊荣的营销专家，擅长AI产品的市场定位和用户获取。",
    verbose=True,
    allow_delegation=True,
    llm=kimi_llm
)

data_analyst = Agent(
    role="数据分析师",
    goal="通过数据分析驱动产品决策",
    backstory="你是一位精通数据科学的分析师，善于从复杂数据中提取有价值的洞见。",
    verbose=True,
    allow_delegation=True,
    llm=kimi_llm
)

# 定义高级任务
task_research = Task(
    description="研究2024年AI领域的最新趋势和技术突破，重点关注多模态AI、自主AI代理和行业应用。",
    expected_output="一份详细的研究报告，包含关键技术趋势、主要研究机构进展和商业应用机会。",
    agent=researcher
)

task_content = Task(
    description="基于研究报告，设计一个全面的内容策略，包括目标受众、内容形式和分发渠道。",
    expected_output="内容策略文档，包含内容日历、关键信息点和内容创作指南。",
    agent=content_strategist,
    context=[task_research]
)

task_marketing = Task(
    description="制定针对不同市场的AI产品推广策略，包括定价模型、合作伙伴计划和用户增长策略。",
    expected_output="市场营销计划，包含市场细分分析、竞争对手分析和推广活动时间表。",
    agent=marketing_expert,
    context=[task_research, task_content]
)

task_analytics = Task(
    description="设计数据分析框架，用于跟踪产品性能、用户行为和市场反馈。",
    expected_output="数据分析方案，包含关键绩效指标、数据收集方法和报告模板。",
    agent=data_analyst,
    context=[task_marketing]
)

# 创建高级团队
advanced_crew = Crew(
    agents=[researcher, content_strategist, marketing_expert, data_analyst],
    tasks=[task_research, task_content, task_marketing, task_analytics],
    process=Process.hierarchical,
    manager_llm=kimi_llm,
    verbose=2
)

# 运行高级团队
if __name__ == "__main__":
    print("启动高级多智能体协作系统 (使用Kimi大模型)...")
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
            result = advanced_crew.kickoff()
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
        print("\n高级协作任务完成！")
        print(result)