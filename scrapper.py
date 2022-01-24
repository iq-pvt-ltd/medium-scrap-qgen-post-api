import re
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def scrap(inputLink):
    web = DesiredCapabilities.CHROME
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Remote(
        command_executor='https://selenium.vaathi.ai/wd/hub',
        desired_capabilities=web,
        options=options)

    driver.implicitly_wait(30)
    driver.delete_all_cookies()
    allContent = []
    driver.get(inputLink)

    try:
        article = driver.find_elements_by_xpath('//*[@id="root"]/div/div[3]/article/div/div/section[1]/div/div')
        if len(article)==1:
            article_title = article[0].find_elements_by_tag_name("h1")
        else:
            article = driver.find_elements_by_tag_name('section')
            article_title = driver.find_element_by_tag_name('h1')

        for data in range(len(article)):
            temp_data = article[data].find_elements_by_tag_name("p")
            for text in temp_data:
                allContent.append(text.text)
        allPara = "".join(allContent)

        '''
            The content is been formatted to JSON
        '''
        medium = {"Title":article_title[0].text,"Content":allPara}
        output = json.dumps(medium,indent=2)
        output_json = json.loads(output)
        '''
            Returns the JSON data
        '''
        return output_json
    finally:
        print("......Exiting Medium.....")
        driver.quit()


''''
1)implememt Exception handling
2)If x_path failed try section
'''