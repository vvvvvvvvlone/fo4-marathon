import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import logging
import colored
from colored import stylize

class Logger:
    @staticmethod
    def setup(name, file, level=logging.INFO, format = logging.Formatter("%(asctime)s (%(levelname)s): %(message)s")):
        handler = logging.FileHandler(file)        
        handler.setFormatter(format)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

error_logger = Logger.setup("error", "error.log", logging.ERROR, logging.Formatter("%(asctime)s (%(levelname)s): [%(funcName)s:%(lineno)d] %(message)s"))

class Config:
    def __init__(self):
        self.__cfg = None
        self.__data = {}
        try:
            self.__cfg = open("data.txt", 'r')
        except OSError:
            error_logger.error("Cannot open the configuration file.")
            sys.exit("An error has occurred, see the log file. ('{}')".format(error_logger.handlers[0].baseFilename))
    def __del__(self):
        if self.__cfg is not None: 
            self.__cfg.close()
    def parse(self):
        self.__data.clear() 
        for line in self.__cfg.read().splitlines():
            if line:
                try:
                    elements = line.split(':', 1)
                    self.__data[elements[0]] = elements[1]
                except (ValueError, IndexError):
                    continue
    @property
    def data(self):
        return self.__data

class ChromeDriver:
    def __init__(self):
        self.__driver = None
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--log-level=3')
            self.__driver = webdriver.Chrome(options = chrome_options)
        except WebDriverException:
            error_logger.error("Unable to start a WebDriver session.")
            sys.exit("An error has occurred, see the log file. ('{}')".format(error_logger.handlers[0].baseFilename))
    def __del__(self):
        if self.__driver is not None:
            #self.__driver.quit()
            pass
    def open_url(self, url):
        try:
            self.__driver.get(url)
        except WebDriverException as error:
            error_logger.error("Error opening url. (Url: {}, Error: {})".format(url, error.msg))
            return False
        return True
    def execute_script(self, script, *args):
        try:
            self.__driver.execute_script(script, *args)
        except WebDriverException as error:
            error_logger.error("Something went wrong during script execution. (Error: {})".format(error.msg))
            return False
        return True
    def find_element(self, method, query):
        try:
            element = self.__driver.find_element(method, query)
        except WebDriverException as error:
            error_logger.error("Element not found. (Error: {}, Query: {})".format(error.msg, query))
            return None
        return element
    def find_elements(self, method, query):
        try:
            elements = self.__driver.find_elements(method, query)
        except WebDriverException as error:
            error_logger.error("Elements not found. (Error: {}, Query: {})".format(error.msg, query))
            return None
        return elements
    def refresh_tab(self):
        return self.execute_script("window.location.reload();")
    def wait_until(self, timeout, method):
        try:
            wait = WebDriverWait(self.__driver, timeout).until(method)
        except WebDriverException as error:
            error_logger.error("WebDraiver wait error. (Error: {})".format(error.msg))
            return None
        return wait
    @property
    def get(self):
        return self.__driver

class WebDriverObject:
    __driver = None
    def __init__(self):
        if self.__class__.__driver is None:
            self.__class__.__driver = ChromeDriver()
    @property
    def driver(self):
        return self.__class__.__driver

class _101xpXPath:
    marathon_button = "/html/body/div[2]/header/div/div/nav/div[1]/ul/li[2]/a"
    login_popup = "/html/body/app-root/div/xp-header/div/div/div[3]/div[2]/button[1]"
    user_control_panel = "//*[@class='user-controls-body']"
    login_control_panel = "//*[contains(@class, 'user-controls-login-btns')]"
    login_popup_username_field = "/html/body/app-root/div/xp-popup/div/ng-component/div/div[2]/div/div[2]/form/div[3]/label/input"
    login_popup_password_field = "/html/body/app-root/div/xp-popup/div/ng-component/div/div[2]/div/div[2]/form/div[4]/label/input"
    login_popup_button = "/html/body/app-root/div/xp-popup/div/ng-component/div/div[2]/div/div[2]/form/div[6]/button"
    logout_button = "/html/body/app-root/div/xp-header/div/div/div[4]/button"
    reward_button = "//*[@id='rewards']/div[2]/div/div[2]/div/button"
    reward_button_new = "/html/body/main/div[2]/div[1]/div[1]/div[2]/div[1]/div/button"
    rewards_balance = "//*[@id='rewards']/div[2]/div/div[2]/p"
    rewards_balance_new = "/html/body/main/div[2]/div[1]/div[2]/div[1]/div[1]/span[1]"

class _101xp(WebDriverObject):
    def __init__(self, login, password):
        WebDriverObject.__init__(self)
        self.__login = login
        self.__password = password
        self.__logged_in = False
        self.__balance = "0"
        self.__looted = False
        self.__href = "https://fo4.101xp.com/shop/firstautumnmarathon"
        if self.__search_for_marathon_link() is False:
            error_logger.error("Could not find a link to FO4 marathon.")
    def __search_for_marathon_link(self):
        if self.driver.open_url("https://fo4.101xp.com/") is True:
            marathon_button = self.driver.find_element(By.XPATH, _101xpXPath.marathon_button)
            if marathon_button is not None:
                self.__href = marathon_button.get_attribute("href")
                return True
        return False
    def __is_user_logged_in(self):
        if self.driver.wait_until(5, EC.presence_of_element_located((By.XPATH, _101xpXPath.user_control_panel))) \
           is not None:
            return True
        return False
    def __is_user_logged_out(self):
        if self.driver.wait_until(5, EC.presence_of_element_located((By.XPATH, _101xpXPath.login_control_panel))) \
           is not None:
            return True
        return False
    def __try_login(self):
        login_popup = self.driver.wait_until(15, EC.element_to_be_clickable((By.XPATH, _101xpXPath.login_popup)))
        if login_popup is not None:
            login_popup.click()
            username_field = self.driver.find_element(By.XPATH, _101xpXPath.login_popup_username_field)
            password_field = self.driver.find_element(By.XPATH, _101xpXPath.login_popup_password_field)
            sign_in_button = self.driver.find_element(By.XPATH, _101xpXPath.login_popup_button)
            if username_field is not None and \
               password_field is not None and \
               sign_in_button is not None:
                    username_field.send_keys(self.__login)
                    password_field.send_keys(self.__password)
                    sign_in_button.click()
                    return True
        return False
    def __try_logout(self):
        logout_button = self.driver.wait_until(15, EC.element_to_be_clickable((By.XPATH, _101xpXPath.logout_button)))
        if logout_button is not None:
            logout_button.click()
            return True
        return False
    def __load_balance(self):
        balance = self.driver.find_element(By.XPATH, _101xpXPath.rewards_balance)
        if balance is not None:
            return balance
        return None
    def login(self):
        if self.driver.open_url("https://101xp.com/") is True:
            if self.__is_user_logged_out():
                if self.__try_login():
                    if self.__is_user_logged_in():
                        self.__logged_in = True
                        return True
            else:
                self.__try_logout()
        return False
    def logout(self):
        if self.driver.open_url("https://101xp.com/") is True:
            if self.__is_user_logged_in():
                if self.__try_logout():
                    if self.__is_user_logged_out():
                        self.__logged_in = False
                        return True
            else:
                self.__logged_in = False
                return True
        return False
    def loot(self):
        if self.driver.open_url(self.__href) is True:
            reward_button = self.driver.wait_until(5, EC.element_to_be_clickable((By.XPATH, _101xpXPath.reward_button)))
            if reward_button is not None:
                if reward_button.get_property('disabled') is False:
                    reward_button.click()
                    return True
        return False
    def check_balance(self):
        if self.driver.open_url(self.__href) is True:
            balance = self.__load_balance() 
            if balance is not None:
                self.__balance = balance.text
        return self.__balance
    def check_balance_new(self):
        if self.driver.open_url(self.__href) is True:
            balance = self.__load_balance() 
            if balance is not None:
                self.__balance = balance.text
        return self.__balance
    @property
    def is_logged_in(self):
        return self.__logged_in
    @property
    def balance(self):
        return self.__balance
    @property
    def is_looted(self):
        return self.__looted

class PrintEx:
    @staticmethod
    def info(msg):
        print(stylize(msg, colored.fg("green")))
    @staticmethod
    def warn(msg):
        print(stylize(msg, colored.fg("yellow")))
    @staticmethod
    def error(msg):
        print(stylize(msg, colored.fg("red")))

class Bot:
    def __init__(self):
        self.__logger = Logger.setup("result", "result.log", logging.INFO, logging.Formatter("%(asctime)s (%(levelname)s): %(message)s"))
        self.__data = None
    def __loot(self, account, d):
        if account.loot() is True:
            PrintEx.info("Successfully looted")
            return True
        else:
            PrintEx.warn("Something went wrong or account already looted!")
            self.__logger.warning("{}: Something went wrong or account already looted.".format(d))
        return False
    def read_config(self):
        cfg = Config()
        cfg.parse()
        self.__data = cfg.data
    def start(self):
        self.__logger.info("Session started.")
        for d in self.__data:
            account = _101xp(d, self.__data[d])
            PrintEx.info("Login: {}".format(d))
            tries = 0
            while account.login() is False:
                tries += 1
                PrintEx.error("Unsuccessful login")
                if tries > 5:
                    PrintEx.error("Failed to login after 5 tries")
                    self.__logger.error("{}: Login failed, account not looted.".format(d)) 
                    break
            else:
                PrintEx.info("Successfully logged in")
                PrintEx.info("Looting..")
                if self.__loot(account, d) is False:
                    PrintEx.info("Trying again..")
                    self.__loot(account, d)
                time.sleep(3)
                account.check_balance()
                PrintEx.info("Balance: {}".format(account.balance))
                self.__logger.info("{}: {} badge(s).".format(d, account.balance)) 
                PrintEx.info("Logout..")
                while account.logout() is False:
                    PrintEx.error("Unsuccessful logout")
                else:
                    PrintEx.info("Successfully logged out")
                PrintEx.info("")
        self.__logger.info("Session ended.")

def main():
    FO4_bot = Bot()
    FO4_bot.read_config()
    FO4_bot.start()

main()