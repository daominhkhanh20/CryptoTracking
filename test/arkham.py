import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import concurrent
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict

opt = webdriver.ChromeOptions()
opt.add_argument("--start-maximized")

chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=opt)
driver.get('https://platform.arkhamintelligence.com/explorer/token/ethereum/0xd1d2Eb1B1e90B638588728b4130137D262C87cae')
# driver.get('https://platform.arkhamintelligence.com/explorer/address/0x6cC5F688a315f3dC28A7781717a9A798a59fDA7b')
# driver.implicitly_wait(10)
time.sleep(4)

start_time = time.time()
# ------------ TOP HOLDERS ----------------------
name_holder = driver.find_elements(by=By.XPATH,
                                   value="//div[@class='TokenTopHolders_topHolderCounterparty__xspM5']/span[@class='Address_container__0RUv1']")
values = driver.find_elements(by=By.XPATH,
                              value="//*[@class='TokenTopHolders_alignRight__Rto6f TokenTopHolders_topHolderBalance__TV5_a']")
pct = driver.find_elements(by=By.XPATH,
                           value="//*[@class='TokenTopHolders_alignRight__Rto6f TokenTopHolders_topHolderPercent__o_RIG']")
money = driver.find_elements(by=By.XPATH,
                             value="//*[@class='TokenTopHolders_alignRight__Rto6f TokenTopHolders_topHolderUSD__dpa54']")
list_top_holders = []
if len(name_holder) == len(values) == len(pct) == len(money):
    for i in range(len(name_holder)):
        soup = BeautifulSoup(name_holder[i].get_attribute('innerHTML'), 'html.parser')
        address = None
        for a in soup.find_all('a'):
            if 'address' in a.get('href'):
                address = a.get('href').rsplit('/', 1)[-1]
        list_top_holders.append({
            'name': soup.get_text(),
            "address": address,
            "count": values[i].text,
            "pct": pct[i].text,
            "money": money[i].text
        })
        # break
print(list_top_holders)

# ---------------------- INFLOW OUTFLOW ----------------------
name_holder = driver.find_elements(by=By.XPATH,
                                   value="//span[@class='Address_container__0RUv1 TokenTopFlows_topFlowItemAddress__7DNYO']")
values = driver.find_elements(by=By.XPATH, value="//span[@class='TokenTopFlows_alignRight__qKOqi']")
money = driver.find_elements(by=By.XPATH,
                             value="//span[@class='TokenTopFlows_alignRight__qKOqi TokenTopFlows_topFlowUSD__sertA']")
list_inflows = []
if len(name_holder) == len(values) == len(money):
    for i in range(len(name_holder)):
        soup = BeautifulSoup(name_holder[i].get_attribute('innerHTML'), 'html.parser')
        address = None
        for a in soup.find_all('a'):
            if 'address' in a.get('href'):
                address = a.get('href').rsplit('/', 1)[-1]
        list_inflows.append({
            'name': soup.get_text(),
            "address": address,
            "count": values[i].text,
            "money": money[i].text
        })
        # break
print(list_inflows)

outflow_element = driver.find_element(by=By.XPATH,
                                      value="//div[@class='TokenTopFlows_topFlowsOptionUnselected___LwVF']")
outflow_element.click()

name_holder = driver.find_elements(by=By.XPATH,
                                   value="//span[@class='Address_container__0RUv1 TokenTopFlows_topFlowItemAddress__7DNYO']")
values = driver.find_elements(by=By.XPATH, value="//span[@class='TokenTopFlows_alignRight__qKOqi']")
money = driver.find_elements(by=By.XPATH,
                             value="//span[@class='TokenTopFlows_alignRight__qKOqi TokenTopFlows_topFlowUSD__sertA']")
list_outflows = []
if len(name_holder) == len(values) == len(money):
    for i in range(len(name_holder)):
        soup = BeautifulSoup(name_holder[i].get_attribute('innerHTML'), 'html.parser')
        address = None
        for a in soup.find_all('a'):
            if 'address' in a.get('href'):
                address = a.get('href').rsplit('/', 1)[-1]
        list_outflows.append({
            'name': soup.get_text(),
            "address": address,
            "count": values[i].text,
            "money": money[i].text
        })
        # break
print(list_outflows)

driver.quit()
list_address = [item['address'] for item in list_top_holders][:20]


def crawling(url):
    driver = webdriver.Chrome(options=opt)
    driver.get(url)
    time.sleep(5)
    tokens = driver.find_elements(by=By.XPATH,
                                  value="//a[@class='Portfolio_start__DpEuq']/div[@class='Icon_container__0d8ok']")
    prices = driver.find_elements(by=By.XPATH, value="//span[@class='Portfolio_end____PNL']")
    counts = driver.find_elements(by=By.XPATH,
                                  value="//div[@class='Portfolio_holdingsContainer__UxDkz Portfolio_end____PNL']/span[1]")
    money = driver.find_elements(by=By.XPATH, value="//div[@class='Portfolio_valueCol__Y24fI']/span")
    list_portfolios = []
    if len(tokens) == len(prices) == len(counts) == len(money):
        for i in range(len(tokens)):
            list_portfolios.append({
                "token": tokens[i].text,
                "price": prices[i].text,
                "count": counts[i].text,
                "money": money[i].text
            })
    return (list_portfolios, url)


with ThreadPoolExecutor(max_workers=) as executor:
    list_address = [f"https://platform.arkhamintelligence.com/explorer/address/{address}" for address in list_address]
    futures = [executor.submit(crawling, address) for address in list_address]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if len(result[0]) == 0:
            print(result[1])
            print('\n')

print(time.time() - start_time)
