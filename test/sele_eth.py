import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
opt = webdriver.ChromeOptions()
opt.add_argument("--start-maximized")

start_time = time.time()
chromedriver_autoinstaller.install()
driver = webdriver.Chrome(options=opt)


# driver.get('https://etherscan.io/token/generic-tokenholders2?a=0xaea46A60368A7bD060eec7DF8CBa43b7EF41Ad85&sid=&m=light&p=1')
# driver.switch_to.frame(driver.find_element(by=By.ID, value='ContentPlaceHolder1_tabHolders'))
driver.get('https://etherscan.io/address/0xbe0eb53f46cd790cd13851d5eff43d12404d33e8#multichain-portfolio')
# driver.implicitly_wait(10)
time.sleep(30)
# with open("page_source.txt", "w", encoding="utf-8") as file:
#     file.write(driver.page_source)
select_dropdown = driver.find_element(By.NAME, "js-chain-table_length")

# Create a Select object
dropdown = Select(select_dropdown)

# Select the option with value "100"
dropdown.select_by_value("100")
# page_link = driver.find_element(By.XPATH, value="//span[@class='page-link']").text
# n_pages = int(page_link.split('of')[-1]) - 1
while True:
    table_element = driver.find_elements(by=By.XPATH, value="//tbody[@class='js-assets text-nowrap align-middle']")[0]
    # print(table_element.text)
    # Extract table rows
    rows = table_element.find_elements(by=By.TAG_NAME, value='tr')
    # Extract data from each row
    for row in rows:
        # Extract cells from each row
        cells = row.find_elements(by=By.TAG_NAME, value="td")
        # Extract text from each cell
        row_data = [cell.text for cell in cells]
        # Do something with the row data (e.g., print it)
        print(row_data)
    element = driver.find_element(By.ID, 'js-chain-table_next')
    class_value = element.get_attribute("class")
    if 'disable' in class_value:
        break
    ActionChains(driver).click(element).perform()
# driver.quit()
print(time.time() - start_time)
