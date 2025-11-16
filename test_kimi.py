import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 获取Kimi模型配置
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
moonshot_model_name = os.getenv("MOONSHOT_MODEL_NAME", "moonshot-v1-8k")

# 打印配置信息（不打印API密钥）
print(f"测试Kimi模型连接: {moonshot_model_name}")
print(f"API密钥已加载: {'是' if moonshot_api_key else '否'}")

# 设置环境变量
os.environ["OPENAI_API_KEY"] = moonshot_api_key
os.environ["OPENAI_BASE_URL"] = "https://api.moonshot.cn/v1"

# 初始化ChatOpenAI实例
chat = ChatOpenAI(
    model_name=moonshot_model_name,
    api_key=moonshot_api_key,
    base_url="https://api.moonshot.cn/v1",
    temperature=0.7
)

# 测试简单的对话
print("\n发送测试消息...")
try:
    response = chat.invoke([{"role": "user", "content": "请说一句简短的中文问候语"}])
    print(f"收到回复: {response}")
    print("\nKimi模型连接测试成功!")
except Exception as e:
    print(f"\n测试失败: {str(e)}")
    print("请检查API密钥和网络连接")