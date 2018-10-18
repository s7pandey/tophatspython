import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import json


def scrape_classes(first=None, index=None):
    driver = webdriver.Firefox()
    columns = {
        "title": [],
        "email": [],
        "name": [],
        "size": [],
        "type": []
    }
    # print(columns)
    first = 0 if not first else first
    index = 0 if not index else index
    final = 0
    try:
        def reset():
            driver.get("https://ssb.montclair.edu/PROD/bwckschd.p_disp_dyn_sched")
            time.sleep(2)
            term = Select(driver.find_element_by_id('term_input_id'))
            term.select_by_value("201820")
            driver.find_element_by_id("id____UID0").click()
            time.sleep(2)
        reset()
        # form = driver.find_element_by_tag_name("form")
        element = driver.find_element_by_id("subj_id")
        instruc = Select(driver.find_element_by_id("insm_id"))
        all_options = len(element.find_elements_by_tag_name("option"))
        final = all_options
        while first < all_options:
            subj = Select(driver.find_element_by_id("subj_id"))
            subj.select_by_index(first)
            time.sleep(2)
            driver.find_element_by_id("id____UID0").click()
            time.sleep(15)
            numberOfElements = len(driver.find_elements_by_xpath("//th/a"))
            while index < numberOfElements:
                driver.find_elements_by_xpath("//th/a")[index].click()
                time.sleep(4)
                title = driver.find_element_by_xpath("//th[@class='ddlabel']").text.split("-")[0]
                columns["title"].append(title.strip())
                columns["size"].append(driver.find_element_by_xpath("//tbody/tr[position()=2]/td[position() = 1]/table/tbody/tr[position()=2]/td[position()=1]").text)
                driver.find_element_by_xpath("//td[@class='ntdefault']/a").click()
                time.sleep(2)
                detail = driver.find_elements_by_xpath("//div[3]/div[3]/div[2]/div[1]/div[2]/table[1]/tbody/tr/td")[index]
                rows = detail.find_elements_by_tag_name("td")
                try:
                    columns['type'].append(rows[5].text)
                except Exception:
                    columns['type'].append("")
                try:
                    name = rows[6].text
                    bracket = name.find("(")
                    if bracket > -1:
                        name = name[:name.find("(")]
                    columns['name'].append(name)
                except Exception:
                    columns['name'].append("")
                try:
                    columns['email'].append(rows[6].find_element_by_tag_name("a").get_attribute("href").split(":")[1])
                except Exception:
                    columns['email'].append("")
                time.sleep(2)
                # driver.back()
                index += 1
                time.sleep(2)
                # print(columns)
            driver.find_element_by_xpath("//td[@class='ntdefault']/a").click()
            time.sleep(2)
            subj = Select(driver.find_element_by_id("subj_id"))
            subj.deselect_by_index(first)
            first += 1
            index = 0
                    # reset()
    except Exception:
        pass
    print(columns)
    print("First: "+str(first))
    print("Index: "+str(index))
    driver.quit()
    df = pd.DataFrame(columns)
    return df, first, index, first < final

def scrape_profs(scraped):
    driver = webdriver.Firefox()
    phones = []
    emails = list(scraped['email'])
    print_index = 0
    try:
        def reset():
            driver.get("https://www.montclair.edu/search.php?tab=EmpDirectory")
            time.sleep(2)
            term = Select(driver.find_element_by_id('filter'))
            term.select_by_value("people")
            time.sleep(2)
        reset()
        for index,prof in enumerate(scraped['name']): 
            print_index = index
            element = driver.find_element_by_id("q")
            element.clear()
            element.send_keys(prof)
            driver.find_element_by_name("Submit").click()
            time.sleep(4)
            results = driver.find_elements_by_css_selector("div.result.person")
            if len(results) > 0:
                result = results[0]
                name = result.find_element_by_class_name("title").text.split(" ")
                try:
                    emails[index] = str(result.find_element_by_class_name("email").find_element_by_tag_name("a").get_attribute("href").split(":")[1])
                except NoSuchElementException:
                    pass
                try:
                    phones.append(result.find_element_by_class_name("phone").text.split(" ")[1])
                except NoSuchElementException:
                    phones.append("")
            else:
                phones.insert(index,"")
    except Exception:
        pass
    print(emails)
    print(phones)
    print(print_index)
    df = scraped
    df['email'] = emails
    df['phone'] = phones
    driver.quit()
    return df