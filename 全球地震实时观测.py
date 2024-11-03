import requests
import winsound
import time
from datetime import datetime
import pyttsx3
import keyboard  # 导入 keyboard 库

# 初始化文本转语音引擎
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # 设置朗读速度

is_reading = True  # 标记朗读状态

def play_alert(level):
    if level < 3:
        winsound.Beep(1000, 500)
    else:
        for _ in range(level - 2):
            winsound.Beep(1000, 500)
            time.sleep(0.5)

def get_log_filename():
    today = datetime.now().strftime('%Y-%m-%d')
    return f"{today} 地震日志.txt"

def log_event(time_now, location, coords, magnitude):
    log_filename = get_log_filename()
    with open(log_filename, "a", encoding="utf-8") as log_file:
        log_file.write(f"时间：{time_now}    地点：{location}    经纬度：{coords[0]},{coords[1]}    震级：{magnitude}\n")

def fetch_earthquake_data():
    response = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson")
    return response.json()

def process_earthquake_data(data, report_counts, fetch_count):
    print(f"第 {fetch_count} 次获取地震数据")
    
    for feature in data['features']:
        magnitude = feature['properties']['mag']
        if magnitude >= 1:
            time_event = datetime.fromtimestamp(feature['properties']['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            location = feature['properties']['place']
            coords = feature['geometry']['coordinates']

            time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
            log_event(time_now, location, coords, magnitude)

            # 为每个不同的地点维护独立的报告计数
            report_count = report_counts.get(location, 0) + 1
            report_counts[location] = report_count

            message = f"地震报告：震中：{location}，震级：{magnitude}，经度：{coords[0]}，纬度：{coords[1]}，时间：{time_now}"
            print(message)

            global is_reading
            if is_reading:
                engine.say(message)  # 朗读地震信息
                engine.runAndWait()  # 等待朗读完成

def toggle_reading():
    global is_reading
    is_reading = not is_reading  # 切换朗读状态
    if is_reading:
        print("已恢复朗读")
    else:
        print("已暂停朗读")

def main():
    print("开始实时监控全球地震")
    
    report_counts = {}
    fetch_count = 1  # 初始化获取计数

    # 在一个单独的线程中监听 Alt 键
    keyboard.add_hotkey('alt', toggle_reading)  # 监听 Alt 键

    while True:
        data = fetch_earthquake_data()
        process_earthquake_data(data, report_counts, fetch_count)
        fetch_count += 1  # 更新获取次数
        time.sleep(60)  # 每60秒更新一次

if __name__ == "__main__":
    main()
