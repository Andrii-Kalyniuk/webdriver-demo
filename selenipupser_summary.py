from typing import Callable, Any

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
wait = WebDriverWait(
    driver,
    timeout=4,
    poll_frequency=0.1,
    ignored_exceptions=(WebDriverException,)
)

'''
# driver.get('https://google.com')

# option 1
assert driver.find_element('[name=q]').get_attribute('value') == ''


# option 2: with wait and function
def element_have_empty_value(driver):
    return driver.find_element('[name=q]').get_attribute('value') == ''


wait.until(element_have_empty_value)


# option 3: with wait and lambda
wait.until(lambda driver: driver.find_element('[name=q]')
           .get_attribute('value') == '')


# option 4: with wait and object-function
class element_have_empty_value:
    def __init__(self):
        ...

    def __call__(self, driver):
        return driver.find_element('[name=q]').get_attribute('value') == ''


wait.until(element_have_empty_value)
'''


# option 5: with wait and object-function with pre-saved parameters
class empty_value_in_element:

    def __init__(self, selector):
        self.selector = selector

    def __call__(self):
        return driver.find_element_by_css_selector(self.selector).\
                   get_attribute('value') == ''

    def __str__(self):
        return f'empty_value_in_element({self.selector})'


# wait.until(empty_value_in_element('[name=q]'))


# option 6: with wait and function-builder
def empty_value_in_element_vs_func_builder(selector):
    def call(driver):
        return driver.find_element(selector).get_attribute('value') == ''

    # call.__str__ = lambda: f'empty_value_in_element({self.selector})'

    return call


# wait.until(empty_value_in_element('[name=q]'))


# ----

class element_exact_text:
    def __init__(self, selector, value):
        self.selector = selector
        self.value = value

    def __call__(self, driver):
        return driver.find_element_by_css_selector(self.selector).text == self.value

    def __str__(self):
        return f'search_in_element({self.selector}) text == {self.value}'


class element_attribute:
    def __init__(self, selector, name, value):
        self.selector = selector
        self.name = name
        self.value = value

    def __call__(self, driver):
        return driver.find_element_by_css_selector(self.selector) \
                   .get_attribute(self.name) == self.value


class element_command_passed:
    def __init__(self, selector, command: Callable[[WebElement], Any]):
        self.selector = selector
        self.command = command

    def __call__(self, driver):
        value = self.command(driver.find_element_by_css_selector(self.selector))
        if value:
            return value
        return True


class Element:
    def __init__(self, selector):
        self.selector = selector

    def should_be_blank(self):
        # wait.until(empty_value_in_element(self.selector))
        return self.should_have_exact_text('') \
            .should_have_attribute('value', '')

    def should_have_exact_text(self, value):
        wait.until(element_exact_text(self.selector, value))
        return self

    def should_have_attribute(self, name, value):
        wait.until(element_attribute(self.selector, name, value))
        return self

    def clear(self):
        wait.until(element_command_passed(
            self.selector,
            lambda webelement: webelement.clear()
        ))
        return self

    def type(self, value):
        wait.until(element_command_passed(
            self.selector,
            lambda webelement: webelement.send_keys(value + Keys.ENTER)
        ))
        return self

    def set_value(self, value):
        self.clear()
        self.type(value)
        # 2:53:10 we not use self.clear() and self.type() here?
        # def clear_and_send_keys(webelement):
        #     webelement.clear()
        #     webelement.send_keys(value + Keys.ENTER)

        # wait.until(element_command_passed(
        #     self.selector,
        #     clear_and_send_keys
        # ))
        return self
