from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import wait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as match

driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())

driver.get('http://duckduckgo.com/')

query = driver.find_element_by_xpath('//input[@name="q"]')
assert query.text == ''
assert query.get_attribute('value') == ''

query.send_keys('github yashaka selene' + Keys.ENTER)

results = driver.find_elements(By.CSS_SELECTOR, '.result__body')
assert len(results) > 5
assert 'User-oriented Web UI' in results[0].text

results[0].find_element(By.CSS_SELECTOR, '.result__title').click()
wait(driver, 4).until(match.title_contains('yashaka/selene'))

