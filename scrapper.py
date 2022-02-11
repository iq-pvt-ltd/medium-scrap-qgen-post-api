import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def scrap(inputLink, urlId):
    Error = None
    '''
    ENVIORNMENT VARIABLES
    '''
    SELENIUM_API_ENDPOINT = os.getenv('SELENIUM_URL')
    DATABASE_API_ENDPOINT = os.getenv('CLOUD_TRIGGER_URL')

    web = DesiredCapabilities.CHROME
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    # Create a new instance of the Chrome driver

    driver = webdriver.Remote(
        command_executor=SELENIUM_API_ENDPOINT,
        desired_capabilities=web,
        options=options)

    driver.implicitly_wait(30)
    driver.delete_all_cookies()
    allContent = []
    driver.get(inputLink)

    try:
        '''
        SCRAPING MEDIUM USING SECTION TAG
        '''
        print("Scrapping using SectionTag")
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
        medium = {"Title": article_title.text, "Content": allPara}
        output = json.dumps(medium, indent=2)
        output_json = json.loads(output)
        '''
            Returns the JSON data
        '''
        return output_json

    except Exception as error_1:
        ''''
        EXCEPTION HANDLING
        '''
        print("Sorry", error_1.__class__, "Occured")
        Error = True

        if Error:
            try:
                '''
                SCRAPPING MEDIUM USING X_PATH
                '''
                print("Scrapping using XPath")
                article = driver.find_elements_by_xpath(
                    '//*[@id="root"]/div/div[3]/article/div/div/section[1]/div/div')
                article_title = article[0].find_elements_by_tag_name("h1")

                for data in range(len(article)):
                    temp_data = article[data].find_elements_by_tag_name("p")
                    for text in temp_data:
                        allContent.append(text.text)

                allPara = "".join(allContent)
                '''
                    The content is been formatted to JSON
                '''
                medium = {"Title": article_title[0].text, "Content": allPara}
                output = json.dumps(medium, indent=4)
                output_json = json.loads(output)
                '''
                    Returns the JSON data
                '''
                return output_json

            except Exception as error_2:
                '''
                HANDLING EXCEPTION
                UPDATE LINK STATUS IN DATABASE
                '''
                API_ENDPOINT = "{}/core/urls/{id}/scrappable"
                linkStatus = API_ENDPOINT.format(
                    DATABASE_API_ENDPOINT, id=urlId)
                req = requests.put(url=linkStatus,data={"isScrappable": False})
                print(req.text)
                print(req.status_code)
                print("Cannot be Scrapped!")
                print("Sorry", error_2.__class__, "Occured")
                return None
        else:
            pass
    finally:
        print("......Exiting Medium......")
        driver.quit()
