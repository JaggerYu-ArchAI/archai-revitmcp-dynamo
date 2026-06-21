import sys
import os
import json


# 必须和Packages下的包文件夹名完全一致（大小写敏感）
PACKAGE_NAME = "ArchAI"
OUT = ""  # 初始化OUT，避免未定义

# ===================== 1. 自动定位节点包的根路径 =====================
# 获取APPDATA路径
appdata = os.environ.get("APPDATA")
# 定位Dynamo Revit根目录
dynamo_root = os.path.join(appdata, "Dynamo", "Dynamo Revit")
if not os.path.isdir(dynamo_root):
    print(f"Dynamo根目录不存在 - {dynamo_root}")
# 遍历版本目录，查找包路径
lib_path = None
try:
    for version_dir in os.listdir(dynamo_root):
        version_path = os.path.join(dynamo_root, version_dir)
        # 跳过非目录
        if not os.path.isdir(version_path):
            continue
        temp_lib = os.path.join(version_path, "Packages", PACKAGE_NAME)
        # 找到第一个有效路径就停止
        if os.path.exists(temp_lib):
            lib_path = temp_lib
            break
except OSError as e:
    print(f"遍历目录时出错：{str(e)}")

def get_package_lib_path():
    if lib_path not in sys.path:
        sys.path.append(lib_path)
    return lib_path, f"lib路径：{lib_path}" if lib_path else "未找到包的节点包目录"


# 加载路径
get_package_lib_path()

# 将 ./extra/lib 第三方模块也加入系统路径
module_path = os.path.join(lib_path, "extra", "lib")
if module_path not in sys.path:
        sys.path.append(module_path)
        

# ================================2. 主程序===========================
# MCP多轮调用主入口
from revit_mcp_tools.mcp_handler import multi_round_mcp_engine

# Dynamo输入端口
API_KEY = IN[0] if len(IN) > 0 else None
USER_QUERY = IN[1] if len(IN) > 1 else None
MAX_ROUNDS = IN[2] if len(IN) > 2 and IN[2] else 10

def format_execution_history(history):
    """格式化执行历史为可读文本"""
    result = []
    result.append("=" * 60)
    result.append("【多轮MCP执行历史】")
    result.append("=" * 60)
    
    for item in history:
        round_num = item['round']
        call_type = item['type']
        
        if call_type == 'ai_error':
            result.append(f"\n第 {round_num} 轮 - AI错误")
            result.append(f"  错误信息: {item['content'].get('error_info', '未知错误')}")
        else:
            result.append(f"\n第 {round_num} 轮 - {call_type}")
            try:
                ai_cmd = json.loads(item['ai_command'])
                if ai_cmd.get('type') == 'finish':
                    result.append(f"  状态: 任务完成")
                    result.append(f"  消息: {ai_cmd.get('message', '')}")
                else:
                    result.append(f"  工具: {ai_cmd.get('tool_name', 'unknown')}")
                    result.append(f"  参数: {ai_cmd.get('parameters', {})}")
            except:
                result.append(f"  AI命令: {item['ai_command'][:100]}...")
            
            tool_result = item['tool_result']
            if tool_result.get('status') == 'success':
                result.append(f"  结果: 执行成功")
            elif tool_result.get('status') == 'finish':
                result.append(f"  结果: {tool_result.get('message', '任务完成')}")
            else:
                result.append(f"  结果: 失败 - {tool_result.get('error_info', '')}")
    
    result.append("\n" + "=" * 60)
    return "\n".join(result)

def main():
    # 1. 基础必填项校验
    if not API_KEY or not USER_QUERY:
        return ["错误: API密钥和用户需求为必填项", [], ""]
    
    # 2. 调用多轮MCP引擎
    try:
        result = multi_round_mcp_engine(USER_QUERY, API_KEY, MAX_ROUNDS)
    except Exception as e:
        return [f"多轮引擎调用失败: {str(e)}", [], ""]
    
    # 3. 格式化输出结果
    execution_log = format_execution_history(result['execution_history'])
    
    # 4. 收集所有创建的元素（如果有）
    created_elements = []
    for item in result['execution_history']:
        if item.get('tool_result', {}).get('status') == 'success':
            data = item['tool_result'].get('data')
            if isinstance(data, list):
                created_elements.extend(data)
            elif data is not None:
                created_elements.append(data)
    
    # 5. 构建最终输出
    summary = f"多轮MCP执行完成 - 共 {result['total_rounds']} 轮"
    
    final_result = result.get('final_result', {})
    if final_result.get('status') == 'finish':
        output_message = [summary, final_result.get('message', '')]
    elif final_result.get('status') == 'success':
        output_message = [summary, "工具执行成功"]
    else:
        output_message = [summary, f"执行异常: {final_result.get('error_info', '')}"]
    
    # 返回格式: [消息列表, 元素列表, 执行日志]
    return [output_message, created_elements, execution_log]


# 执行主程序
try:
    OUT = main()
except Exception as e:
    OUT = [[f"程序异常: {str(e)}"], [], ""]