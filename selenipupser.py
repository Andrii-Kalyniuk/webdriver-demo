from __future__ import annotations

import re
from typing import Callable, List, Union

from selenium.common.exceptions import WebDriverException, \
    ElementNotInteractableException
from selenium.webdriver.android.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as match
from selenium.webdriver.support.wait import WebDriverWait

driver: WebDriver = ...


class match_element_is_visible():

    def __call__(self, webelement: WebElement):
        actual = webelement.is_displayed()
        if not actual:
            raise WebDriverException(
                stacktrace=[f'Reason: actual element is not displayed']
            )


class match_value_of_element(object):
    def __init__(self, text_):
        self.expected = text_

    def __call__(self, webelement: WebElement):
        actual = webelement.get_attribute('value')
        if not self.expected == actual:
            raise WebDriverException(
                stacktrace=[f'Reason:'
                            f'\n\texpected value: "{self.expected}"'
                            f'\n\tis not equal to'
                            f'\n\tactual value:   "{actual}"']
            )


class match_count_more_than(object):
    def __init__(self,  value):
        self.expected = value

    def __call__(self, webelements: List[WebElement]):
        actual = len(webelements)
        if not self.expected < actual:
            raise WebDriverException(
                stacktrace=[f'Reason:'
                            f'\n\tactual amount: {actual}'
                            f'\n\tis less than'
                            f'\n\texpected amount: {self.expected}']
            )


class match_element_text_containing(object):
    def __init__(self, text_):
        self.expected = text_

    def __call__(self, webelement: WebElement):
        actual = webelement.text
        if self.expected not in actual:
            raise WebDriverException(
                stacktrace=[f'Reason: expected text "{self.expected}"'
                            f' is not present in "{actual}" text']
            )


class match_passed(object):
    def __init__(
             self,
             entity: Union[Element, Elements],
             command: Callable[[Union[WebElement, List[WebElement]]], None]
    ):
        self.entity = entity
        self.command = command

    # TODO: 01:41:50 IS __call__ - syntax sugar?
    # TODO: should we remove driver param from __call__
    #  in all our match conditions?
    def __call__(self, driver):
        try:
            raw_entity = self.entity.locate()
            self.command(raw_entity)
            return True
        except Exception as error:
            reason = getattr(error, 'msg', str(error)) or str(error)
            raise WebDriverException(stacktrace=[
                f'On:\n\t{self.entity}\n'
                f'Reason:\n\t{reason}\n'])


def actions():
    return ActionChains(driver)


def wait():
    return WebDriverWait(driver, timeout=4, poll_frequency=0.1,
                ignored_exceptions=(WebDriverException,))


def should_have_title(value: str):
    return wait().until(match.title_contains(value))


def quit_():
    driver.quit()


def _wait_until_passed(element: Element,
                       command: Callable[[WebElement, None], None],
                       description=''):
    return wait().until(match_passed(element, command),
                        message=f'\n\tfailed trying to:{description}')


def by(css_selector: str):
    return By.CSS_SELECTOR, css_selector


def visit(url):
    return driver.get(url)


def _actual_not_overlapped_element(webelement):
    maybe_cover: WebElement = driver.execute_script(
        '''
            var element = arguments[0];
            
            var isVisible = !!( 
                element.offsetWidth 
                || element.offsetHeight 
                || element.getClientRects().length 
            ) && window.getComputedStyle(element).visibility !== 'hidden'
            if (!isVisible) {
                throw 'element is not visible'
            }
            var rect = element.getBoundingClientRect();
            var x = rect.left + rect.width/2;
            var y = rect.top + rect.height/2;
            var elementByXnY = document.elementFromPoint(x,y);
            if (elementByXnY == null) {
                return [element, null];
            }
            var isNotOverlapped = element.isSameNode(elementByXnY);
            return isNotOverlapped 
                   ? null
                   : elementByXnY;
            ''',
        webelement
    )
    if maybe_cover is not None:
        element_html = re.sub('\\s+', ' ',
                              webelement.get_attribute("outerHTML"))
        cover_html = re.sub('\\s+', ' ',
                            maybe_cover.get_attribute("outerHTML"))
        raise ElementNotInteractableException(
            stacktrace=[f'Reason: element {element_html} is overlapped by '
                        f'{cover_html}']
        )
    return webelement


# TODO: try to convert selector to func in __init__ of Locator
"""
class Locator:

    def __init__(self, selector: str, description: str):
        if 'elements(' in description:
            self._func = lambda: driver.find_elements(*by(selector))
        elif 'element(' in description:
            self._func = lambda: driver.find_element(*by(selector))
        self._description = description
        self.selector = selector
"""


class Locator(Callable[[], Union[WebElement, List[WebElement]]]):
    def __init__(self,
                 func: Callable[[], Union[WebElement, List[WebElement]]],
                 description: str):
        self._func = func
        self._description = description

    def __call__(self) -> Union[WebElement, List[WebElement]]:
        return self._func()

    def __str__(self):
        return self._description


class Element:
    def __init__(self, locate: Locator):
        # self.selector = selector
        # self._element = self.should_be_visible()
        self.locate = locate

    def __str__(self):
        return str(self.locate)

    def element(self, selector) -> Element:
        # return Element(f'{self.selector} {selector}')
        return Element(Locator(
            func=lambda: self.locate().find_element(*by(selector)),
            description=f'{self}.element({selector})'
        ))
    """
    def element(self, selector) -> Element:
        # return Element(f'{self.selector} {selector}')
        return Element(Locator(
            selector,
            description=f'{self}.element({selector})'
        ))
    """
    # --- Asserts ---

    # TODO: 53:10 should_be_visible() where we use it?
    def should_be_visible(self) -> Element:
        wait().until(match_passed(self, match_element_is_visible()))
        return self

    def should_have_text(self, text) -> Element:
        # wait().until(match.text_to_be_present_in_element(
        # wait().until(match_element_text_containing(self, text))
        # wait().until(match_passed(self, match_element_text_containing(text)))
        _wait_until_passed(
            self,
            match_element_text_containing(text),
            f'assert match_element_text_containing({text})'
        )
        return self

    def should_have_value(self, value) -> Element:
        # wait().until(match_value_of_element(self, value))
        wait().until(match_passed(self, match_value_of_element(value)))
        return self

    # def type(self, text):
    #     wait_visible(self.selector).send_keys(text)
    #     return self
    #
    # def press_enter(self):
    #     wait_visible(self.selector).send_keys(Keys.ENTER)
    #     return self

    # --- Commands ---

    def send_keys(self, keys) -> Element:
        # wait().until(match.presence_of_element_located(by(self.selector))
        #              ).send_keys(keys)
        _wait_until_passed(
            self,
            lambda its: its.send_keys(keys),
            description=f'type({keys})'
        )
        return self

    def type(self, text) -> Element:
        # self.element.send_keys(text)
        # self.click().send_keys(text)
        _wait_until_passed(
            self,
            lambda its: _actual_not_overlapped_element(its).send_keys(text),
            description=f'type({text})'
        )
        return self

    def press_enter(self) -> Element:
        # self.element.send_keys(Keys.ENTER)
        # self.click().send_keys(Keys.ENTER)
        self.type(Keys.ENTER)
        return self

    def click(self) -> Element:
        _wait_until_passed(
            self,
            lambda its: its.click(),
            description='click'
        )
        return self

    def clear(self) -> Element:
        _wait_until_passed(
            self,
            lambda its: _actual_not_overlapped_element(its).clear(),
            description='clear'
        )
        return self

    def double_click(self) -> Element:
        _wait_until_passed(
            self,
            lambda its: actions().double_click(its).perform(),
            description='double click'
        )
        return self

    def hover(self) -> Element:
        _wait_until_passed(
            self,
            lambda its: actions().move_to_element(its).perform(),
            description='hover'
        )
        return self

    def should_be_blank(self) -> Element:
        return self.should_have_value('').should_have_text('')


class Elements:
    # def __init__(self, selector):
    #     self.selector = selector
    # change class realization from selector-wrapper to webelement-wrapper

    def __init__(self, locate: Locator):
        self.locate = locate

    def __str__(self):
        return str(self.locate)

    # --- Element builders ---

    @property
    def first(self) -> Element:
        return self[0]

    @property
    def second(self) -> Element:
        return self[1]

    def __getitem__(self, index: int) -> Element:
        # return Element(f'{self.selector}:nth-of-type({index+1})')
        return Element(Locator(
            func=lambda: self.locate()[index],
            description=f'{self}[{index}]'
        ))

    """
    def __getitem__(self, index: int):
        # return Element(f'{self.selector}:nth-of-type({index+1})')
        return Element(Locator(
            selector=self.locate.selector,
            description=f'elements({self})[{index}]')).locate()[index]
    """

    # --- Asserts ---

    def should_have_amount_more_than(self, value: int) -> Elements:
        wait().until(match_passed(self, match_count_more_than(value)))
        return self


def element(selector) -> Element:
    # return Element(selector)
    return Element(Locator(
        func=lambda: driver.find_element(*by(selector)),
        description=f'element({selector})'
    ))


def elements(selector) -> Elements:
    return Elements(Locator(
        func=lambda: driver.find_elements(*by(selector)),
        description=f'elements({selector})'
    ))

"""
def elements(selector) -> Elements:
    return Elements(Locator(
        selector,
        description=f'elements({selector})'
    ))
"""
