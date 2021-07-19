import requests
import meta
from bs4 import BeautifulSoup
import threading

import models
import logging
import coloredlogs

# Logger Config
logging.basicConfig(filename='py_spyder.log', filemode='a')
logger = logging.getLogger("py_spyder")
coloredlogs.install(level='DEBUG', logger=logger, milliseconds=True,
                    fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')

jobs = []
pool = []


def get_url(zone_code, page=1):
    return "https://msearch.51job.com/job_list.php?keyword=%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E5%B8%88&keywordtype" \
           "=2&jobarea=" + zone_code + "&landmark=&issuedate=&saltype=&degree=&funtype=&indtype=&jobterm=&cotype" \
                                       "=&workyear=&cosize=&lonlat=&line=&radius=&areaname=&from=&searchtype=&fromapp" \
                                       "=&filttertype=&pageno=" + str(page)


def iterate_zones():
    for zone_code in meta.get_zone_codes():
        threading.Thread(target=iterate_zone, args=(zone_code,)).start()


def iterate_zone(zone_code):
    pool.append(zone_code)
    logger.debug("Iterating on zone with zone_code "+zone_code)

    first_page = requests.get(get_url(zone_code),
                              headers={"User-Agent": meta.get_user_agent(),
                                       "Cookie": meta.get_cookies()}).content.decode('utf-8')
    doc = BeautifulSoup(first_page, "lxml")
    print(first_page)
    option = doc.select_one("select option:last-child")
    pages = int(1 if option is None else option.text)

    threading.Thread(target=iterate_jobs, args=(zone_code, 1, doc,)).start()

    for page in range(2, pages + 1):
        page_content = requests.get(get_url(zone_code, page),
                                    headers={"User-Agent": meta.get_user_agent(),
                                             "Cookie": meta.get_cookies()}).content.decode('utf-8')
        threading.Thread(target=iterate_jobs, args=(
            zone_code, page, BeautifulSoup(page_content, "lxml"),)).start()

    pool.remove(zone_code)
    check_pool()


def iterate_jobs(zone_code, page_id, doc):
    pool.append(zone_code + str(page_id))
    logger.debug("Iterating on jobs with zone_code " +
                 zone_code+" and page_id " + str(page_id))

    for job in doc.select(".e.e3"):
        url = job['href']
        title = job.select_one('strong span').text
        area = job.select_one('em').text
        salary = job.select_one('i').text
        tmp = job.select_one('p').text.split(' | ')
        company_type = tmp[0]
        requirements = "" if len(tmp) == 0 else " | ".join(tmp[1:])
        company_name = job.select_one('aside').text

        jobs.append(models.Job(url, title, area, salary,
                    company_type, requirements, company_name))
        threading.Thread(target=get_job_description, args=(
            url, len(jobs), )).start()

    pool.remove(zone_code + str(page_id))
    check_pool()


def get_job_description(url, id):
    pool.append("description_getter_"+str(id))
    logger.debug("Getting Job Description with id " + str(id))
    page_content = requests.get(url, headers={"User-Agent": meta.get_user_agent(),
                                              "Cookie": meta.get_cookies()}).content.decode('utf-8')
    el = BeautifulSoup(page_content, "lxml").select_one("article p")
    jobs[id].description = "" if el is None else el.text.strip()
    pool.remove("description_getter_"+str(id))
    check_pool()


def check_pool():
    if len(pool) == 0 and len(jobs) > 0:
        save()


def save():
    # save the content with csv format
    with open('jobs.csv', 'w') as fp:
        # csv headers
        fp.write(
            'url,title,area,salary,company_type,requirements,company_name,description\n')
        for job in jobs:
            fp.write(','.join([job.url, job.title, job.area, job.salary,
                               job.company_type, job.requirements, job.company_name, job.description]) + "\n")


if __name__ == '__main__':
    iterate_zones()
