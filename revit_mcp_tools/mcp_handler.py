# -*- coding:utf-8 -*-
# MCP核心管控文件
import json
import os
import extra.lib.yaml
from extra.lib.openai import OpenAI

# 导入配置文件和工具库
from revit_mcp_tools.config import BASE_URL, MODEL, MCP_TOOL_WHITELIST, get_mcp_tool_prompt
import revit_mcp_tools.revit_basic_tools as rbt


# ==================================================
# 函数1：调用AI指令（支持对话历史）
# ==================================================
def get_ai_mcp_command(messages, api_key):
    try:
        # 初始化客户端
        client = OpenAI(api_key=api_key, base_url=BASE_URL)
        system_prompt = get_mcp_tool_prompt()

        # 构建完整消息列表
        full_messages = [{"role":"system","content":system_prompt}] + messages

        response = client.chat.completions.create(
            model = MODEL,
            messages = full_messages,
            temperature = 0.1,
            stream = False
        )

        ai_output = response.choices[0].message.content.strip()
        
        try:
            json.loads(ai_output)
        except json.JSONDecodeError:
            return {"status": "fail", "error_info": f"AI输出非合法JSON：{ai_output}"}
        
        return ai_output

    except Exception as e:
        return {"status": "fail", "error_info": f"大模型调用失败：{str(e)}"}

# ==================================================
# 函数2：MCP结果解析
# ==================================================
def mcp_dispatch(ai_json):
    try:
        # 第一层校验
        try:
            command = json.loads(ai_json)
        except json.JSONDecodeError:
            return {"status": "fail", "error_info": "AI输出不是合法的JSON格式，已拒绝执行"}
        
        # 检查是否为finish类型
        if "type" in command and command["type"] == "finish":
            return {
                "status": "finish",
                "message": command.get("message", "任务已完成"),
                "error_info": ""
            }
        
        # 支持两种JSON格式：有type字段和无type字段
        if "type" in command and command["type"] == "tool":
            tool_name = command["tool_name"]
            parameters = command["parameters"]
        elif "tool_name" in command and "parameters" in command:
            tool_name = command["tool_name"]
            parameters = command["parameters"]
        else:
            return {"status": "fail", "error_info": "AI输出缺少tool_name或parameters字段"}
        
        # 第三层校验
        target_tool = next((t for t in MCP_TOOL_WHITELIST if t["tool_name"] == tool_name), None)
        
        if not target_tool:
            return {"status": "fail", "error_info": f"工具「{tool_name}」不在白名单中"}
        
        # 第四层校验
        required_params = target_tool["required_params"]
        missing_params = [p for p in required_params if p not in parameters]
        if missing_params:
            return {"status": "fail", "error_info": f"缺少必填参数：{','.join(missing_params)}"}
        
        # 第五层校验
        function_name = target_tool["function_name"]
        if not hasattr(rbt, function_name):
            return {"status": "fail", "error_info": f"未找到函数：{function_name}"}
        
        # 执行函数
        target_function = getattr(rbt, function_name)
        function_result = target_function(**parameters)
        
        return {
            "status": "success",
            "data": function_result,
            "error_info": "",
            "tool_used": tool_name
        }

    except Exception as e:
        return {"status": "fail", "error_info": f"MCP调度失败：{str(e)}"}


# ==================================================
# 函数3：多轮工具调用引擎
# ==================================================
def multi_round_mcp_engine(user_query, api_key, max_rounds=6):
    """
    多轮MCP调用引擎
    :param user_query: 用户自然语言查询
    :param api_key: API密钥
    :param max_rounds: 最大调用轮次，防止无限循环
    :return: 执行历史和最终结果
    """
    execution_history = []
    messages = [{"role": "user", "content": user_query}]
    final_result = None
    
    for round_idx in range(max_rounds):
        # 1. 获取AI命令
        ai_response = get_ai_mcp_command(messages, api_key)
        
        # 检查是否失败
        if isinstance(ai_response, dict) and ai_response.get("status") == "fail":
            execution_history.append({
                "round": round_idx + 1,
                "type": "ai_error",
                "content": ai_response
            })
            final_result = ai_response
            break
        
        # 2. 执行工具
        tool_result = mcp_dispatch(ai_response)
        
        # 记录执行历史
        execution_history.append({
            "round": round_idx + 1,
            "type": "tool_call" if tool_result["status"] in ["success", "fail"] else "finish",
            "ai_command": ai_response,
            "tool_result": tool_result
        })
        
        final_result = tool_result
        
        # 3. 检查是否需要继续
        if tool_result["status"] == "finish":
            # AI认为任务已完成，结束循环
            break
        elif tool_result["status"] == "success":
            # 将工具执行结果反馈给AI，用于下一轮决策
            result_summary = f"工具「{tool_result.get('tool_used', 'unknown')}」执行成功，结果：{str(tool_result['data'])}"
            messages.append({"role": "assistant", "content": ai_response})
            messages.append({"role": "user", "content": result_summary})
        else:
            # 工具执行失败，记录并停止
            result_summary = f"工具执行失败：{tool_result['error_info']}"
            messages.append({"role": "assistant", "content": ai_response})
            messages.append({"role": "user", "content": result_summary})
            break
    
    # 返回完整执行历史
    return {
        "status": "completed",
        "total_rounds": len(execution_history),
        "execution_history": execution_history,
        "final_result": final_result
    }


# ==================================================
# 兼容旧版的单轮调用函数（保持向后兼容）
# ==================================================
def get_ai_mcp_command_single(user_query, api_key):
    """
    兼容旧版的单轮调用函数
    """
    return get_ai_mcp_command([{"role": "user", "content": user_query}], api_key)