import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import json
import pandas as pd

def scrape_classes(term,index=None,new_index=None,another_index=None):
    driver = webdriver.Firefox()
    driver.get("https://my.wcupa.edu/psp/pprd/EMPLOYEE/SA/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?PAPP=YES")
    time.sleep(5)
    driver.switch_to.frame("TargetContent")
    select = Select(driver.find_element_by_id('CLASS_SRCH_WRK2_STRM$35$'))
    select.select_by_visible_text(term)
    time.sleep(2)
    career = Select(driver.find_element_by_id('SSR_CLSRCH_WRK_ACAD_CAREER$2'))
    career.select_by_value("UGRD")
    driver.find_element_by_id('SSR_CLSRCH_WRK_SSR_OPEN_ONLY$5').click()
    class_select = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$0')
    classes = class_select.find_elements_by_tag_name('option')
    classes_length = len(classes)
    index = 0 if not index else index
    columns = {'title':[],'size':[],'name':[]}
    try:
        while index < classes_length:
            class_select = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$0')
            class_select.find_elements_by_tag_name('option')[index].click()
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()
            time.sleep(4)
            new_index = 0 if not new_index else new_index
            another_index = 0 if not another_index else another_index
            try:
                driver.find_element_by_id("win0divDERIVED_CLSMSG_ERROR_TEXT")
                index += 1
                continue
            except Exception:
                pass
            try:
                title_box_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$" + str(new_index)
                title_box = driver.find_element_by_id(title_box_id)
                while title_box is not None:
                    class_title = title_box.text
                    class_table = driver.find_element_by_id("ACE_$ICField48$" + str(new_index))
                    try:
                        row_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX3$" + str(another_index)
                        row = class_table.find_element_by_id(row_id)
                        while row is not None:
                            information_boxes = row.find_elements_by_class_name("PSLEVEL3GRIDROW")
                            if "LEC" in information_boxes[1].text:
                                columns['title'].append(class_title)
                                columns["name"].append(information_boxes[6].text)
                                columns["size"].append(information_boxes[10].text)
                            print(columns)
                            another_index += 1
                            row_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX3$" + str(another_index)
                            row = class_table.find_element_by_id(row_id)
                    except NoSuchElementException:
                        pass
                    new_index += 1
                    title_box_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$" + str(new_index)
                    title_box = driver.find_element_by_id(title_box_id)
                    print(title_box.text)
            except NoSuchElementException:
                pass
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_MODIFY").click()
            time.sleep(4)
            index += 1
    except Exception:
        pass

    print("INDEXES: %s, %s, %s" % ( index, new_index, another_index))

    frame = pd.DataFrame(columns)
    driver.quit()
    return frame, index, new_index, another_index, index < classes_length

def check(x):
    check_list = re.findall('[A-Z][^A-Z]*',x[0])
    check_list = [thing.strip() for thing in check_list]
    if all(set([item.strip() for item in re.findall('[A-Z][^A-Z]*\s*',y)])==set(check_list) for y in x):
        return " ".join(check_list)
    else:
        return ",".join(x)

def scrape_profs(scraped):
    driver = webdriver.Firefox()
    def f(x):
        return pd.Series(dict(size=x["size"].sum(), title= "%s" % ', '.join(x['title'])))

    driver.get("https://www.wcupa.edu/forms/search/default.aspx")
    profs = scraped["name"].values.tolist()
    data = {"name": [], "email":[],"phone":[]}
    for prof in profs:
        data["name"].append(prof)
        driver.find_element_by_id("txtSearch").send_keys(prof)
        driver.find_element_by_id("ctl00_body_btnSearch").click()
        time.sleep(2)
        try:
            data["email"].append(driver.find_element_by_class_name("peopleEmail").text.split(":")[1].strip())
        except Exception:
            data["email"].append("")
            pass
        try:
            data["phone"].append(driver.find_element_by_class_name("dialPhone").text)
        except Exception:
            data["phone"].append("")
            pass
        driver.find_element_by_id("txtSearch").clear()

    scraped["email"] = data["email"]
    scraped["name"] = scraped["name"].str.strip()
    scraped["name"] = scraped["name"].str.replace(r"\s+", " ")
    scraped["name"] = scraped["name"].str.replace(r"\s+-\s+","-")

    scraped["name"] = scraped["name"].str.split(r"\s*,\s*").apply(lambda x: check(x))
    scraped["title"] = scraped["title"].str.strip()
    
    scraped.groupby("name").apply(f)
    driver.quit()
    return scraped
