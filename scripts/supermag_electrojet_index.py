from pathlib import Path
import pandas as pd


FILE_NAME = "20250508-08-47-supermag.csv"
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
print("project root:",PROJECT_ROOT)
DATA_DIR = PROJECT_ROOT / "data"
print("data dir:", DATA_DIR)
FILE_PATH = DATA_DIR / FILE_NAME
print("file path:", FILE_PATH)


try:
    df = pd.read_csv(FILE_PATH)
    print("success read csv, the head of DataFrame is:")
    print(df.head())

except FileNotFoundError:
    print(f"错误：文件未找到，请检查路径 '{FILE_PATH}' 是否正确。")
except pd.errors.EmptyDataError:
    print(f"错误：文件 '{FILE_PATH}' 为空。")
except pd.errors.ParserError:
    print(f"错误：解析文件 '{FILE_PATH}' 时发生错误，请检查文件格式是否正确。")
except Exception as e:
    print(f"读取CSV文件时发生未知错误：{e}")
