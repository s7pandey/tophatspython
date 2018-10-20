import time
import string
import math
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException


def scrape_classes():
    driver = webdriver.Firefox()
    driver.get("https://peportal.maine.edu/psp/PAPRD_1/EMPLOYEE/CSPRDST/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL?PORTALPARAM_PTCNAV=UM_CLASS_SRCH1&EOPP.SCNode=EMPL&EOPP.SCPortal=EMPLOYEE&EOPP.SCName=ADMN_UM_CLASS_SRCH_QCKLINLS&EOPP.SCLabel=&EOPP.SCPTcname=PT_PTPP_SCFNAV_BASEPAGE_SCR&FolderPath=PORTAL_ROOT_OBJECT.PORTAL_BASE_DATA.CO_NAVIGATION_COLLECTIONS.ADMN_UM_CLASS_SRCH_QCKLINLS.ADMN_S201006251221396117606016&IsFolder=false")
    time.sleep(5)
    driver.switch_to.frame("TargetContent")
    select = Select(driver.find_element_by_id('CLASS_SRCH_WRK2_INSTITUTION$31$'))
    select.select_by_value("UMS05")
    time.sleep(2)
    i = 0
    alpha = list(string.ascii_uppercase)
    columns = {"title":[],"size":[],"name":[], "type": []}
    try:
        while i < 26:
            print("*******"+alpha[i]+"********")
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_SUBJ_SRCH$0").click()
            time.sleep(2)
            driver.find_element_by_id("SSR_CLSRCH_WRK2_SSR_ALPHANUM_"+alpha[i]).click()
            time.sleep(2)
            another_index = 0
            try:
                while another_index > -1:
                    driver.find_element_by_id("SSR_CLSRCH_WRK2_SSR_ALPHANUM_"+alpha[i]).click()
                    time.sleep(2)
                    driver.find_element_by_id("SSR_CLSRCH_WRK2_SSR_PB_SELECT_SUBJ$"+str(another_index)).click()
                    time.sleep(2)
                    driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()
                    new_index = 0
                    try:
                        driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_SUBJ_SRCH$0").click()
                        time.sleep(2)
                        another_index += 1
                        continue
                    except Exception:
                        pass
                    try:
                        driver.find_element_by_id("#ICSave").click()
                        time.sleep(2)
                    except Exception:
                        pass
                    time.sleep(3)
                    try:
                        row_id = "ACE_SSR_CLSRSLT_WRK_GROUPBOX3$" + str(new_index)
                        row = driver.find_element_by_id(row_id)
                        while row is not None:
                            combined_section = False
                            information_boxes = row.find_elements_by_class_name("PSLEVEL3GRIDROW")
                            if "LAB" not in information_boxes[1].text.replace("-"," "):
                                class_type = information_boxes[1].text.replace("\n"," ")
                                information_boxes[1].find_element_by_tag_name("a").click()
                                time.sleep(2)
                                class_title = driver.find_element_by_id("DERIVED_CLSRCH_DESCR200").text
                                time.sleep(2)
                                p_table = driver.find_element_by_id("SSR_CLSRCH_MTG$scroll$0")
                                profs = p_table.find_elements_by_class_name("PSLEVEL1GRIDODDROW")
                                thing = math.ceil(len(profs) / 4)
                                value = 2
                                for x in range(thing):
                                    if value < len(profs):
                                        if len(columns["title"]) > 0:
                                            if columns["title"][-1] == class_title and columns["name"][-1] == profs[value].text:
                                                value += 4
                                                continue
                                        columns["type"].append(class_type)
                                        columns["title"].append(class_title)
                                        columns["name"].append(profs[value].text)
                                        columns["size"].append(driver.find_element_by_id("SSR_CLS_DTL_WRK_ENRL_CAP").text)
                                    value += 4
                                print(columns)
                                driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_BACK").click()
                            new_index += 1
                            row_id = "ACE_SSR_CLSRSLT_WRK_GROUPBOX3$" + str(new_index)
                            row = driver.find_element_by_id(row_id)
                            print(columns)
                    except NoSuchElementException:
                        pass
                    time.sleep(2)
                    driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_MODIFY").click()
                    time.sleep(4)
                    driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_SUBJ_SRCH$0").click()
                    time.sleep(2)
                    another_index += 1
            except NoSuchElementException:
                pass
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CANCEL").click()
            time.sleep(2)
            i += 1
    except Exception:
        pass

    driver.quit()
    frame = pd.DataFrame(columns)
    args = {"i": i, "another_index": another_index, "new_index": new_index, "finished": i < 26}
    return frame, args

def scrape_profs(scraped):
    driver = webdriver.Firefox()
    extract = scraped
    driver.get("https://peoplesearch.maine.edu/index.php")
    profs = extract["name"].values.tolist()
    data = {"email":[],"phone":[]}
    for prof in profs:
        driver.find_element_by_id("q").send_keys(prof)
        driver.find_element_by_id("site").click()
        time.sleep(2)
        check = False
        values = driver.find_elements_by_tag_name("dd")
        for index,value in enumerate(values):
            if "@maine" in value.text:
                check = True
                data["email"].append(value.text)
                data["phone"].append(values[index-1].text)
        if not check:
            data["email"].append("")
            data["phone"].append("")
        driver.find_element_by_id("q").clear()

    extract["email"] = data["email"]
    extract["phone"] = data["phone"]

    extract["title"] = extract["title"].str.replace(r"[A-Z]+\s+\d{3}\s+-\s+\d{4}", "")
    extract["title"] = extract["title"].str.strip()
    driver.quit()
    return extract