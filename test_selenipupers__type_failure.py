import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from givenpage import GivenPage
import selenipupser

options = ChromeOptions()
options.headless = False
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),
                          options=options)

selenipupser.driver = driver
page = GivenPage(driver)
page.opened_with_body(
    '''
    <input value="before"></input>
    <div 
        id='overlay' 
        style='
            display:block;
            position: fixed;
            display: block;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0,0,0,0.1);
            z-index: 2;
            cursor: pointer;
        '
    >
    </div>
    '''
)


before = time.time()
try:
    selenipupser.element('input').type(' after')
except TimeoutException as error:
    time_spent_ms = (time.time() - before) * 1000
    assert time_spent_ms > 4000
    assert 'Message: \n\tfailed trying to:type( after)' in str(error)
    assert ('Reason: element <input value="before"> '
            'is overlapped by <div id="overlay"'
            in str(error))
