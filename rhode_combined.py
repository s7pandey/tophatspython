import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import json
import pandas as pd


def scrape_classes(term, args, frame=None):
    driver = webdriver.Firefox()
    driver.get("https://appsaprod.uri.edu:9516/psc/sa_crse_cat/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL")
    time.sleep(5)
    terms = Select(driver.find_element_by_id('CLASS_SRCH_WRK2_STRM$35$'))
    terms.select_by_visible_text(term)
    time.sleep(2)
    driver.find_element_by_id('SSR_CLSRCH_WRK_SSR_OPEN_ONLY$5').click()
    class_select = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$1')
    classes = class_select.find_elements_by_tag_name('option')
    classes_length = len(classes)
    try:
        index = args['index']
    except KeyError:
        index = 0
    try:
        new_index = args['new_index']
    except KeyError:
        new_index = 0
    try:
        another_index = args['another_index']
    except KeyError:
        another_index = 0
    columns = {"type":[],"title":[], "name":[], "size": []} if not frame else frame
    try:
        while index < classes_length:
            class_select = driver.find_element_by_id('SSR_CLSRCH_WRK_SUBJECT_SRCH$1')
            class_select.find_elements_by_tag_name('option')[index].click()
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH").click()
            time.sleep(4)
            
            try:
                driver.find_element_by_id("win0divDERIVED_CLSMSG_ERROR_TEXT")
                index += 1
                continue
            except Exception:
                pass
            try:
                driver.find_element_by_id("#ICSave").click()
                time.sleep(18)
            except Exception:
                pass
            try:
                title_box_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$" + str(new_index)
                title_box = driver.find_element_by_id(title_box_id)
                while title_box is not None:
                    class_title = title_box.text
                    try:
                        row_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX3$" + str(another_index)
                        table = driver.find_element_by_id("ACE_$ICField48$" + str(new_index))
                        row = table.find_element_by_id(row_id)
                        # print(row)
                        while row is not None:
                            information_boxes = row.find_elements_by_class_name("PSLEVEL3GRIDROW")
                            print(information_boxes[1].text)
                            if "LEC" in information_boxes[1].text:
                                # print("what")
                                columns["type"].append(information_boxes[1].text)
                                columns['title'].append(class_title)
                                columns["name"].append(information_boxes[4].text)
                                information_boxes[1].find_element_by_tag_name("a").click()
                                time.sleep(4)
                                columns["size"].append(driver.find_element_by_id("SSR_CLS_DTL_WRK_ENRL_CAP").text)
                                driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_BACK").click()
                                time.sleep(12)
                            # print(columns)
                            another_index += 1
                            row_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX3$" + str(another_index)
                            table = driver.find_element_by_id("ACE_$ICField48$" + str(new_index))
                            row = table.find_element_by_id(row_id)
                    except NoSuchElementException:
                        pass
                    new_index += 1
                    title_box_id = "win0divSSR_CLSRSLT_WRK_GROUPBOX2GP$" + str(new_index)
                    title_box = driver.find_element_by_id(title_box_id)
                    print(title_box.text)
            except NoSuchElementException:
                pass
            time.sleep(4)
            driver.find_element_by_id("CLASS_SRCH_WRK2_SSR_PB_MODIFY").click()
            time.sleep(15)
            index += 1
            new_index = 0
            another_index = 0
    except Exception:
        pass

    print("INDEXES: %s, %s, %s" % ( index, new_index, another_index))
    driver.quit()
    # frame = pd.DataFrame(columns)
    args = {"school": "Rhode", "term": term, "index": index, 
            "new_index": new_index, "another_index": another_index,
            "finished": index >= classes_length}
    return columns, args

def scrape_profs(scraped):
    driver = webdriver.Firefox()
    driver.get("https://directory.uri.edu")
    time.sleep(5)
    emails = []
    phone = []
    for i, row in old.iterrows():
        names = row["name"].split(" ")
        if len(names) > 3:
            firstname = names[0]
            lastname = names[1].replace(",","")
        else:
            firstname = names[0]
            lastname = names[-1]
            if firstname == " " and lastname == " ":
                emails.append("")
                phone.append("")
                continue
        driver.find_element_by_id("lname").send_keys(lastname)
        driver.find_element_by_id("fname").send_keys(firstname)
        driver.find_element_by_name("Search").click()
        time.sleep(4)
        try:
            email = driver.find_element_by_partial_link_text("@uri.edu").text
            emails.append(email)
        except NoSuchElementException:
            email = ""
            emails.append("")
        try:
            num = driver.find_element_by_xpath("/html/body/div[3]/div[1]/div/div[1]/div[1]/div/div[1]/div[2]/table[2]/tbody/tr[1]/td[2]").text
            phone.append(num)
        except Exception:
            num = ""
            phone.append("")
        print(email)
        print(num)
    old["email"] = emails
    old["phone"] = phone

    # Parsing
    old["title"] = old["title"].str.split(" - ").str.get(1)
    old["title"] = old["title"].str.strip()

    old["phone"] = old["phone"].astype("str")
    old["email"] = old["email"].astype("str")
    old["size"] = old["size"].astype("int")
    old["email"].fillna("",inplace=True)
    old["phone"].fillna("",inplace=True)

    def f(x):
        return pd.Series(dict(size=x["size"].sum(),
                            title= "%s" % ', '.join(x['title']),
                            email= "%s" % ', '.join(x["email"]),
                            phone="%s" % ', '.join(x["phone"])))
                    

    result = old.groupby("name").apply(f)
    result["email"] = result["email"].str.replace("nan", "")
    result["phone"] = result["phone"].str.replace("nan", "")
    result["email"] = result["email"].str.split(",").str.get(0)
    result["phone"] = result["phone"].str.split(",").str.get(0)
    driver.quit()
    return result