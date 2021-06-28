"""
From webdriver with wait to the class Element - summary
QAACodaW22.mp4
"""

import google

# option 1
# ________
# driver = Chrome()

# driver.get('https://google.com')

# invalid locator when use just find_element without BY
# assert driver.find_element('[name=q]').get_attribute('value') == ''

# assert driver.find_element_by_css_selector(
#     '[name=q]').get_attribute('value') == ''

# option 5: with wait and object-function with pre-saved parameters
# ________
google.visit()
google.query.should_be_blank()
google.query.set_value('yashaka python selene')
