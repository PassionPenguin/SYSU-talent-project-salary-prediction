from concurrent.futures import thread
from pydoc import describe
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import logging
import coloredlogs
import threading
import requests
import sys

# Logger Config
logging.basicConfig(filename='py_spyder.log', filemode='a')
logger = logging.getLogger("py_spyder")
coloredlogs.install(level='DEBUG', logger=logger, milliseconds=True,
                    fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')

# Webdriver Chrome Config
chrome_binary_path = r"C:\Users\Hoarfroster\AppData\Local\Google\Chrome SxS\Application\chrome.exe" if sys.platform == "win32" else r"/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
chrome_driver_extension = ".exe" if sys.platform == "win32" else ""


class Job:
    # Job Model
    def __init__(self, title, published_at, salary, address, basic_requirement, need, company, company_information,
                 company_category, tags, description):
        self.title = title
        self.published_at = published_at
        self.salary = salary
        self.address = address
        self.basic_requirement = basic_requirement
        self.need = need
        self.company = company
        self.company_information = company_information
        self.company_category = company_category
        self.tags = tags
        self.description = description

class Spider:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
                          "Chrome/94.0.4579.0 Safari/537.36 "
        self.base_url = "https://search.51job.com/list/000000,000000,0000,00,9,99," \
                        "%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588,2," \
                        "1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&company_size" \
                        "=99&ord_field=0&dibiaoid=0&line=&welfare= "
        self.headers = {
            "User-Agent": self.user_agent,
            'Host': 'search.51job.com',
            'Referer': self.base_url,
        }
        self.pool = []
        self.jobs = []

        # define chrome webdriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.binary_location = chrome_binary_path
        self.driver = webdriver.Chrome(r"./chromedriver" + chrome_driver_extension, options=chrome_options)

    def check_pool(self):
        print(self.jobs)
        if self.pool == [] and len(self.jobs) > 0:
            self.save()

    def parse_html_source(self, source, name):
        self.pool.append(name)
        print(source)
        soup = BeautifulSoup(source, "lxml")
        result=[]
        for el in soup.select('.j_joblist .e'):
            print("---")
            title = el.select('[title]')[0].text
            salary = el.select('.sal')[0].text
            published_at = el.select('.time')[0].text[:-2]
            # here we will get a string containing multiple information,
            # thus iterating on the array created with the string is the only way
            # to process with the string
            meta = el.select('.d.at')[0].text.split(' | ')
            address = meta[0]
            need = meta[-1]
            basic_requirement = meta[1:-1]
            company_information = el.select('.dc.at')[0].text
            company = el.select('.cname.at')[0].text
            company_category = el.select('.int.at')[0].text
            # tags is not available in all jobs
            # try-except is needed
            try:
                tags = el.select('.tags')[0].text
            except Exception:
                tags = ''

            result.append(Job(title, published_at, salary, address, basic_requirement,
                            need, company, company_information, company_category, tags, "description"))

        self.jobs.extend(result)
        self.pool.remove(name)
        self.check_pool()

    def reset_url(self):
        self.driver.get(self.base_url)
        self.driver.find_element_by_css_selector('.allcity').click()
        # sleep to wait for webdriver to load the page
        time.sleep(0.5)

    def scrape(self, pages, current_url, name):
        self.pool.append(name)
        for i in range(1, pages + 1):
            # notice that the url changes only in the last part before .html:
            # https://....,2,[page].html?lang=c... is the actual url
            res = requests.get(current_url.replace(
                "2," + str(i) + ".html", "2," + str(i + 1) + ".html"), headers=self.headers).content.decode("gbk")
            # iterate on jobs
            t = threading.Thread(target=self.parse_html_source,
                                 args=(res, name + "parser" + str(i),))
            t.start()
            logger.debug("Started crawling with name " + name + " and page(s) " + str(i))

        self.pool.remove(name)
        self.check_pool()

    def main(self):
        self.reset_url()
        # all rows of popular cities
        current_row = 0
        rows = len(self.driver.find_elements_by_css_selector(
            '.con>div:not(:first-child) tr'))

        # iterate on rows
        while current_row < rows:
            # select all city(-ies) in the current row
            for el in self.driver.find_elements_by_css_selector('.con>div:not(:first-child) tr')[
                current_row].find_elements_by_css_selector('em'):
                el.click()
            # confirm filter
            self.driver.find_element_by_css_selector('span.p_but').click()
            time.sleep(0.5)

            # get page count
            pages = int(self.driver.find_element_by_css_selector(
                '.p_in>.td:first-child').text[2:-2])
            # iterate on pages
            threading.Thread(target=self.scrape, args=(
                pages, self.driver.current_url, 'scrape' + str(current_row),)).start()
            logger.debug("Started crawling with row-id " + str(current_row))
            self.reset_url()
            current_row += 1

        self.driver.quit()

    def save(self):
        # save the content with csv format
        with open('jobs.csv', 'w') as fp:
            # csv headers
            fp.write(
                'title,published_at,salary,address,basic_requirement,need,company,company_information,company_category,tags\n')
            for job in jobs:
                fp.write(
                    ','.join([job.title, job.published_at, job.salary, job.address, job.basic_requirement, job.need,
                              job.company, job.company_information, job.company_category, job.tags]) + "\n")
            logger.debug(str(len(jobs)) + " jobs saved to jobs.csv")


if __name__ == '__main__':
    spider = Spider()
    spider.main()
