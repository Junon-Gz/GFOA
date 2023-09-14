from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium import webdriver
import os
import time
from selenium.webdriver.common.by import By
#TODO:用Service代替option
from selenium.webdriver.chrome.service import Service as ChromeService
from utils.log_record import logger
class specialBrowser:
    def __init__(self,chromedriverPath="",chromepath="",headless=False):

        option = webdriver.ChromeOptions()

        # 根据操作系统类型区分配置
        if os.name == "nt":
            # windows
            option.binary_location = chromepath
            option.add_argument("--start-maximized")
            if headless:
                option.add_argument("--headless") #后台模式
        else:
            # linux
            option.add_argument("--start-maximized")
            option.add_argument("--headless")
            option.add_argument('--no-sandbox')  # 必须添加此选项
            option.add_argument('--disable-dev-shm-usage')  # 必须添加此选项

        self.driver:ChromiumDriver = webdriver.Chrome(executable_path=chromedriverPath,options=option)

    def get_url(self,url:str):
        try:
            self.driver.get(url)
        except Exception as e:
            logger.info("访问链接失败")
    
    def find_ele(self,xpath:str,retry:int,way = By.XPATH):
        for i in range(retry):
            # 定位元素
            try:
                element = self.driver.find_element(by=By.XPATH,value=xpath)
                if element:
                    break
            except:
                element = None
            time.sleep(0.5)
        return element


    def click(self,xpath:str):
        #对xpath元素点击
        try:
            self.driver.find_element(by=By.XPATH,value=xpath).click()
        except Exception as e:
            logger.info("点击失败")

    def input_text(self,xpath:str,text:str):
        #对xpath元素输入文本
        try:
            ele = self.driver.find_element(by=By.XPATH,value=xpath)
            ele.clear()
            ele.send_keys(text)
        except Exception as e:
            logger.info("输入失败")
    
    def get_text(self,xpath:str,retry):
        for i in range(retry):
            time.sleep(0.1)
            # 获取元素文本内容
            try:
                ele = self.driver.find_element(by=By.XPATH,value=xpath)
                return ele.text
            except Exception as e:
                logger.info("获取失败")
            time.sleep(0.5)
        else:
            return ""

    def switch_iframe(self,xpath:str):
        #切换iframe
        try:
            if xpath == "default":
                self.driver.switch_to.default_content()
            else:
                iframe_element = self.driver.find_element(by=By.XPATH,value=xpath)
                self.driver.switch_to.frame(iframe_element)
        except Exception as e:
            logger.info("切换iframe失败")

    def get_xpath_base64(self,xpath:str):
        #截取xpath元素的图片为base64
        try:
            image_element = self.driver.find_element(by=By.XPATH,value=xpath)
            b64 = image_element.screenshot_as_base64
            return b64
        except Exception as e:
            return ""

    def get_screenshot(self,path):
        try:
            self.driver.get_screenshot_as_file(path)
        except Exception as e:
            logger.info("截屏失败")
        
    def get_cookie(self,name:str=''):
        try:
            if name == '':
                cookie = self.driver.get_cookies()
            else:
                cookie = self.driver.get_cookie(name)
        except Exception as e:
            logger.info(f"获取cooike失败{e}")
        finally:
            return cookie

    def close(self):
        #关闭浏览器
        try:
            self.driver.quit()
        except Exception as e:
            logger.info("关闭浏览器失败")

if __name__ == "__main__":
    driver_path = r"D:\工作\流程易\机器人V8.4.2\release\Python\python3_lib\chromedriver.exe"
    chr_path = r"D:\工作\流程易\机器人V8.4.2\release\Python\python3_lib\GoogleChrome\Chrome\chrome.exe"
    a = specialBrowser(chromedriverPath=driver_path,chromepath=chr_path)
    a.get_url("https://www.baidu.com")
    b = a.get_text("(//span[@class='title-content-title'])[1]",retry=5)
    logger.info(b)
    a.close()
    time.sleep(2)

