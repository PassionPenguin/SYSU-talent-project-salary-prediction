from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
import logging
import coloredlogs


logging.basicConfig(filename='py_spyder.log',
                    filemode='a')
logger = logging.getLogger("py_spyder")
coloredlogs.install(level='DEBUG',
                    logger=logger,
                    milliseconds=True,
                    fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')


class Job:
    # Job Model
    def __init__(self, title, published_at, salary, address, exp, deg, need, company, companyType, companySize, companyCategory, tags):
        self.title = title
        self.published_at = published_at
        self.salary = salary
        self.address = address
        self.exp = exp
        self.deg = deg
        self.need = need
        self.company = company
        self.companyType = companyType
        self.companySize = companySize
        self.companyCategory = companyCategory
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
        exp = ""
        deg = ""
        exp_standard = ['在校生/应届生', '1-3年',
                        '3-5年', '5-10年', '10年以上', '无需经验']
        degree_standard = ['初中及以下', '高中/中技/中专',
                           '大专', '本科', '硕士', '博士', '无学历要求']
        for i in l:
            if any(i in s for s in exp_standard):
                exp = i
            if any(i in s for s in degree_standard):
                deg = i
        # same as L80
        l = el.select('.dc.at')[0].text.split(' | ')
        companyType_standard = ['国企', '外资（欧美）', '外资（非欧美）', '上市公司',
                                '合资', '民营公司', '外企代表处', '政府机关', '事业单位', '非营利组织', '创业公司']
        companySize_standard = ['少于50人', '50-150人', '150-500人',
                                '500-1000人', '1000-5000人', '5000-10000人', '10000人以上']
        companyType = ""
        companySize = ""
        for i in l:
            if any(i in s for s in companyType_standard):
                companyType = i
            if any(i in s for s in companySize_standard):
                companySize = i
        company = el.select('.cname.at')[0].text
        companyCategory = el.select('.int.at')[0].text
        # tags is not available in all jobs
        # try-except is needed
        tags = ''
        try:
            tags = el.select('.tags')[0].split(' ')
        except Exception:
            tags = ''
        jobs.append(Job(title, published_at, salary, address, exp, deg,
                    need, company, companyType, companySize, companyCategory, tags))
        logger.debug("Writing new job to jobs with title " +
                     title + " + company name " + company)
    return


# define chrome webdriver
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(
    r"./chromedriver", options=chrome_options)
# reset webdriver to default page


def resetUrl():
    driver.get("https://search.51job.com/list/000000,000000,0000,00,9,99,%25E6%2595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590%25E5%25B8%2588,2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare=")
    driver.find_element_by_css_selector('.allcity').click()
    # sleep to wait for webdriver to load the page
    time.sleep(1)


resetUrl()
# all rows of popular cities
currentRow = 0
rows = len(driver.find_elements_by_css_selector(
    '.con>div:not(:first-child) tr'))
# iterate on rows
while(currentRow < rows):
    # select all city(-ies) in the current row
    for el in driver.find_elements_by_css_selector('.con>div:not(:first-child) tr')[currentRow].find_elements_by_css_selector('em'):
        el.click()
    # confirm filter
    driver.find_element_by_css_selector('span.p_but').click()
    time.sleep(1)
    # get page count
    pages = int(driver.find_element_by_css_selector(
        '.p_in>.td:first-child').text[2:-2])
    # iterate on pages
    for i in range(1, pages+1):
        # notice that the url changes only in the last part before .html:
        # https://....,2,[page].html?lang=c... is the actual url
        new_url = driver.current_url.replace(
            "2,"+str(i)+".html", "2,"+str(i+1)+".html")
        driver.get(new_url)
        time.sleep(1)
        # iterate on jobs
        t = threading.Thread(target=parseHTMLSource, args=(driver.page_source,))
        t.start()
        logger.debug("Started Thread with filter row " +
                     str(currentRow)+" + page(s) " + str(i))
    # every time all the jobs provided in the cities of current row is collected
    # reset the url to the default one to load for the next row
    resetUrl()
    currentRow += 1
# save the content with csv format
with open('jobs.csv', 'w') as fp:
    # csv headers
    fp.write(
        'title,published_at,salary,address,exp,deg,need,company,companyType,companySize,companyCategory,tags\n')
    for job in jobs:
        fp.write(','.join([job.title, job.published_at, job.salary, job.address, job.exp, job.deg, job.need,
                           job.company, job.companyType, job.companySize, job.companyCategory, job.tags])+"\n")
    logger.debug(str(len(jobs)) + " jobs saved to jobs.csv")
driver.quit()
