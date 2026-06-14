"""
DeepSeek AI 客户端
用于连接 DeepSeek API 进行智能问答
"""
import requests
import os
import json

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-a4b678718ce04b14afacd46a9d3bbc17")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

class DeepSeekClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, messages, model="deepseek-chat", temperature=0.7, max_tokens=2000):
        """
        发送对话请求到 DeepSeek API
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 使用的模型，默认为 deepseek-chat
            temperature: 生成温度，0-1之间，越低越确定性
            max_tokens: 最大生成的token数量
        
        Returns:
            API响应内容
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            return "请求超时，请稍后重试。"
        except requests.exceptions.RequestException as e:
            return f"API请求错误: {str(e)}"
        except Exception as e:
            return f"发生错误: {str(e)}"
    
    def ask_recipe_question(self, question, recipe_context):
        """
        基于食谱知识图谱的上下文回答问题
        
        Args:
            question: 用户的问题
            recipe_context: 从知识图谱获取的相关食谱信息
        
        Returns:
            AI生成的回答
        """
        system_prompt = """你是一个专业的食谱助手，负责回答关于美食烹饪的问题。

你的知识来源于一个详细的食谱知识图谱数据库，里面包含：
- 80道各种家常菜、川菜、粤菜等
- 每道菜的原材料、用量、制作步骤
- 菜的难度、烹饪时间、口味等信息

请根据提供的知识图谱信息回答用户的问题。如果知识图谱中有相关信息，请基于那些信息回答。
如果知识图谱中没有相关信息，请说明暂时无法回答，并建议用户尝试其他问题。

回答要：
1. 详细且实用
2. 使用中文
3. 如果有具体的步骤或配料，要清晰列出
4. 适当加入一些烹饪技巧
"""
        
        user_prompt = f"""
## 用户问题
{question}

## 知识图谱相关信息
{recipe_context}

请根据上述知识图谱信息回答用户的问题。
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.chat(messages, temperature=0.7)
    
    def ask_cooking_tips(self, recipe_name, ingredients):
        """
        获取烹饪技巧建议
        
        Args:
            recipe_name: 菜名
            ingredients: 原材料列表
        
        Returns:
            AI生成的烹饪技巧
        """
        system_prompt = """你是一个经验丰富的厨师，擅长给出实用的烹饪技巧。请根据菜品和原材料给出3-5条实用的烹饪技巧。"""
        
        user_prompt = f"菜名: {recipe_name}\n原材料: {', '.join(ingredients)}\n请给出一些实用的烹饪技巧："
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.chat(messages, temperature=0.8)
    
    def generate_shopping_list(self, recipe_name, ingredients, servings=1):
        """
        生成采购清单
        
        Args:
            recipe_name: 菜名
            ingredients: 原材料列表
            servings: 份数
        
        Returns:
            整理后的采购清单
        """
        system_prompt = """你是一个专业的食谱助手，擅长整理采购清单。请根据给出的原材料信息，整理一份清晰的采购清单，按类别分组（蔬菜、肉类、调料等）。"""
        
        user_prompt = f"菜名: {recipe_name}\n需要的份数: {servings}\n原材料:\n" + "\n".join([f"- {item}" for item in ingredients])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        return self.chat(messages, temperature=0.5)


# 全局客户端实例
_client = None

def get_deepseek_client():
    """获取全局 DeepSeek 客户端实例"""
    global _client
    if _client is None:
        _client = DeepSeekClient()
    return _client
