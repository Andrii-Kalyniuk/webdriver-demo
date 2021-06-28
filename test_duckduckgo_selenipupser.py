from selene import have, be
from selene.support.shared import browser
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

import selenipupser as selenipupser_browser


options = ChromeOptions()
options.headless = False
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                          options=options)

selenipupser_browser.driver = driver
selenipupser_browser.visit('http://duckduckgo.com')
selenipupser_browser.element('[name=q]').should_be_blank()\
    .type('github yashaka selene').press_enter()

selenipupser_browser.elements('.result__body').should_have_amount_more_than(5)\
    .first.should_have_text('User-oriented Web UI')\
    .element('.result__title').click()
selenipupser_browser.should_have_title('yashaka/selene')

selenipupser_browser.quit_()

# selenipupser code above
# ----------------------------------------------
# selene code below

# browser.config.driver = driver
# browser.open('http://duckduckgo.com/')
# browser.element('[name=q]')\
#     .should(be.blank)\
#     .type('yashaka selene python').press_enter()
# browser.all('.result__body')\
#     .should(have.size_greater_than(5))\
#     .first.should(have.text('User-oriented Web UI browser tests in Python'))
# browser.all('.result__body').first.element('.result__title').click()
# browser.should(have.title_containing('yashaka/selene'))
