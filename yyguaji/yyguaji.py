from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 指定 Edge WebDriver 路径
driver_path = "D:\\MPNN\\yyguaji\\edgedriver_win32\\msedgedriver.exe"
if not os.path.exists(driver_path):
    raise FileNotFoundError(f"找不到 WebDriver: {driver_path}")

# 启动 WebDriver
service = Service(driver_path)
driver = webdriver.Edge(service=service)

# 让用户手动登录
driver.get("https://smartcourse.hust.edu.cn")  # 进入课程首页
input("请手动登录并完成验证码输入后，进入课程页面后按回车继续...")

# 等待用户手动进入视频播放页面
input("登录后请手动进入视频播放页面，然后按回车键继续...")

# 打印整个页面的 HTML，查看是否存在 iframe
print(driver.page_source)

# 通过 JavaScript 获取 iframe 元素
iframes = driver.execute_script("return document.getElementsByTagName('iframe');")
print(f"找到 {len(iframes)} 个 iframe")

if len(iframes) == 0:
    print("未找到 iframe 元素，请检查页面结构或动态加载情况。")
    driver.quit()
    exit()

video_found = False  # 标记是否找到视频

# 遍历所有 iframe
for index, iframe in enumerate(iframes):
    driver.switch_to.default_content()  # 确保切回主页面
    driver.switch_to.frame(iframe)  # 切换到 iframe
    print(f"切换到 iframe {index}，等待加载完成...")

    # 等待 iframe 加载完成，通过监听 load 事件
    driver.execute_script("""
        var iframe = arguments[0];
        return new Promise(function(resolve) {
            iframe.onload = function() {
                resolve();
            };
        });
    """, iframe)

    # 等待视频元素加载完成，最多等待 10 秒
    try:
        video = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )
        print(f"在 iframe {index} 找到视频")
        video_found = True
        break  # 找到就停止
    except:
        print(f"iframe {index} 未找到视频")

# 没找到视频，退出
if not video_found:
    print("未找到视频，请检查 iframe 结构")
    driver.quit()
    exit()

# 监控视频播放进度
def wait_for_video_complete(driver):
    """等待视频播放完成"""
    while True:
        try:
            video = driver.find_element(By.TAG_NAME, "video")
            current_time = driver.execute_script("return arguments[0].currentTime", video)
            duration = driver.execute_script("return arguments[0].duration", video)

            print(f"播放进度: {current_time:.1f}/{duration:.1f} 秒")
            if duration - current_time <= 1:
                print("视频播放完成")
                return True

            is_playing = driver.execute_script("return !arguments[0].paused && !arguments[0].ended", video)
            if not is_playing:
                print("检测到视频暂停，尝试继续播放...")
                play_button = driver.find_element(By.CLASS_NAME, "vjs-play-button")
                play_button.click()

            time.sleep(5)  # 每 5 秒检查一次
        except Exception as e:
            print(f"检查视频状态时出错: {e}")
            time.sleep(5)

# 等待视频播放完成
wait_for_video_complete(driver)

print("任务完成，即将关闭浏览器")
driver.quit()
