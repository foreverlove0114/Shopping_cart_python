import os
import sys

def run_tests_simple():
    """简单版本的测试运行器"""
    print("🚀 开始运行测试...")

    # 直接使用os.system运行命令
    command = f"{sys.executable} -m pytest end_to_end.py -v --html=test_report.html"
    exit_code = os.system(command)

    print(f"✅ 测试完成，退出码: {exit_code}")
    return exit_code


if __name__ == "__main__":
    run_tests_simple()