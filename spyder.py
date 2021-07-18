from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import logging
import coloredlogs
import threading
import requests


logging.basicConfig(filename='py_spyder.log',
                    filemode='a')
logger = logging.getLogger("py_spyder")
coloredlogs.install(level='DEBUG',
                    logger=logger,
                    milliseconds=True,
                    fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')


class Job:
    # Job Model
    def __init__(self, title, published_at, salary, address, basic_requirement, need, company, company_information, company_category, tags):
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


# define list
jobs = []


def parseHTMLSource(source):
    soup = BeautifulSoup(source, "lxml")
    for el in soup.select('.j_joblist .e'):
        title = el.select('[title]')[0].text
        salary = el.select('.sal')[0].text
        published_at = el.select('.time')[0].text[:-2]
        # here we will get a string containing multiple information,
        # thus iterating on the array created with the string is the only way
        # to process with the string
        l = el.select('.d.at')[0].text.split(' | ')
        address = l[0]
        need = l[-1]
        basic_requirement = l[1:-1]
        company_information = el.select('.dc.at')[0].text
        company = el.select('.cname.at')[0].text
        company_category = el.select('.int.at')[0].text
        # tags is not available in all jobs
        # try-except is needed
        tags = ''
        try:
            tags = el.select('.tags')[0].text
        except Exception:
            tags = ''
        jobs.append(Job(title, published_at, salary, address, basic_requirement,
                    need, company, company_information, company_category, tags))
    return


# define chrome webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.binary_location = r"C:\Users\Hoarfroster\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
driver = webdriver.Chrome(
    r"./chromedriver.exe", options=chrome_options)


def resetUrl():
    driver.get("https://search.51job.com/list/000000,000000,0000,00,9,99,%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588,2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&company_size=99&ord_field=0&dibiaoid=0&line=&welfare=")
    driver.find_element_by_css_selector('.allcity').click()
    # sleep to wait for webdriver to load the page
    time.sleep(0.5)


resetUrl()
# all rows of popular cities
current_row = 0
rows = len(driver.find_elements_by_css_selector(
    '.con>div:not(:first-child) tr'))
# iterate on rows
while(current_row < rows):
    # select all city(-ies) in the current row
    for el in driver.find_elements_by_css_selector('.con>div:not(:first-child) tr')[current_row].find_elements_by_css_selector('em'):
        el.click()
    # confirm filter
    driver.find_element_by_css_selector('span.p_but').click()
    time.sleep(0.5)
    # get page count
    pages = int(driver.find_element_by_css_selector(
        '.p_in>.td:first-child').text[2:-2])
    current_url = driver.current_url
    # iterate on pages
    for i in range(1, pages+1):
        print("---")
        # notice that the url changes only in the last part before .html:
        # https://....,2,[page].html?lang=c... is the actual url
        res=requests.get(current_url.replace(
            "2,"+str(i)+".html", "2,"+str(i+1)+".html")).content.decode("utf-8")
        time.sleep(0.5)
        # iterate on jobs
        t = threading.Thread(target=parseHTMLSource,
                             args=(res,))
        t.start()
    # every time all the jobs provided in the cities of current row is collected
    # reset the url to the default one to load for the next row
    resetUrl()
    current_row += 1
# save the content with csv format
with open('jobs.csv', 'w') as fp:
    # csv headers
    fp.write(
        'title,published_at,salary,address,basic_requirement,need,company,company_information,company_category,tags\n')
    for job in jobs:
        fp.write(','.join([job.title, job.published_at, job.salary, job.address, job.basic_requirement, job.need,
                           job.company, job.company_information, job.company_category, job.tags])+"\n")
    logger.debug(str(len(jobs)) + " jobs saved to jobs.csv")
driver.quit()
