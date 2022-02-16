import time
import timeit

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import logging
import platform
import pandas as pd

logger = logging.getLogger(__name__)

start = timeit.default_timer()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
driver.maximize_window()
baseUrl = "https://www.tarladalal.com/"
driver.get(baseUrl)
#driver.implicitly_wait(2)
driver.find_element(By.XPATH, '//a[@href="RecipeAtoZ.aspx"]').click()
driver.find_element(By.LINK_TEXT, 'A').click()

scrapedDataDict = {}

titleDataList = []
ingredientsDataList = []
methodDataList = []
nutrientValuesDataList = []
categoryDataList = []
imageLinkDataList = []

mainHandle = driver.current_window_handle
pagesAtoZ = driver.find_elements(By.XPATH, '//table[@id="ctl00_cntleftpanel_mnuAlphabets"]//table//a')
pageNameUrlsArr = []
# for page in pagesAtoZ:
#     pageName = page.get_attribute('text')
#     pageNameUrl = 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=' + pageName + '&pageindex=1'
#     pageNameUrlsArr.append(pageNameUrl)

pageNameUrlsArr.append('https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=Y&pageindex=1')
print("pageNameUrlsArr:" + str(pageNameUrlsArr))
# logger.info("pageNameUrlsArr:", str(pageNameUrlsArr))

def is_undefined_or_empty(s):
    return bool((s is None) or (str(s).strip() == ""))


for page in pageNameUrlsArr:
    driver.get(page)
    print("After click Current Url: " + driver.current_url)
    # logger.info("After click Current Url: " + driver.current_url)

    parentGoToPageUrl = driver.current_url

    try:
        if driver.current_url == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=0-9&pageindex=1' or \
                driver.current_url == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=Misc&pageindex=1':
            print("Skipping current url: " + driver.current_url)
            continue

        lastPageIndexArr = driver.find_elements(By.XPATH, '//div[contains(text(), "Goto Page:")][1]/a')
        lastPaginationValue = len(lastPageIndexArr)
        lastPaginationXpath = '//div[contains(text(), "Goto Page:")][1]/a[' + str(lastPaginationValue) + ']'
        lastPageIndex = driver.find_element(By.XPATH, lastPaginationXpath)
        lastPageIndexVal = lastPageIndex.text
        print("Max Pagination size for this: " + lastPageIndexVal)
        # logger.info("Max Pagination size for this: " + lastPageIndexVal)

        # Create the list urls for recipe for A to Z
        urlsListAtoZ = []
        lastPageIndexToVisit = int(lastPageIndexVal)+1

        for i in range(1, lastPageIndexToVisit):
            # recipeUrl = baseUrl + "RecipeAtoZ.aspx?pageindex=" + str(i)
            recipeUrl = page[0:page.rfind('=')] + "=" + str(i)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"+recipeUrl)
            urlsListAtoZ.append(recipeUrl)

        print("urls for receipe A to Z: " + str(urlsListAtoZ))
        print("urls for receipe A to Z length: " + str(len(urlsListAtoZ)))

        for urlInAtoZ in urlsListAtoZ:
            print("Navigating to url: " + urlInAtoZ)
            driver.get(urlInAtoZ)
            print("Current Url now: " + driver.current_url)
            parentGoToPageUrl = driver.current_url
            allRecipeElementsHyperLink = driver.find_elements(By.XPATH,
                                                              '//div[contains(text(), "Goto Page:")][1]/following-sibling::div[1]//div[@class="rcc_recipecard"]//span[@class="rcc_recipename"]/a')
            allRecipeElementsHyperLinkHrefArr = []
            for hyperLink in allRecipeElementsHyperLink:
                allRecipeElementsHyperLinkHrefArr.append(hyperLink.get_attribute('href'))

            print("All Hyper Links for Recipe on page: " + driver.current_url + " no of links : " + str(
                len(allRecipeElementsHyperLinkHrefArr)) + " : " + str(allRecipeElementsHyperLinkHrefArr))
            countHyperLinksOnThePage = 0

            print("")
            print("Going to read the hyperlinked page recipe.....")

            for eachRecipePage in allRecipeElementsHyperLinkHrefArr:
                parentHandle = driver.current_window_handle
                try:
                    print(">>>>>>>>>> Navigating to page: " + eachRecipePage)
                    driver.get(eachRecipePage)

                    child_handle = driver.current_window_handle
                    driver.find_element(By.XPATH, '//div[@id="recipehead"]')
                    recipeCurrentLink = driver.current_url

                    countHyperLinksOnThePage = countHyperLinksOnThePage + 1
                    print("countHyperLinksOnThePage: " + str(countHyperLinksOnThePage))
                    print("recipeCurrentLink: " + recipeCurrentLink)

                    # Skip reading for receipt in the first 3 links (which are decorative item posts) on the first page
                    if parentGoToPageUrl == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=A&pageindex=1' and countHyperLinksOnThePage < 4:
                        print("--------> Going to skip this page : " + driver.current_url)
                        continue

                    print("")
                    print("--------> Going to read Title for page : " + driver.current_url)
                    title = driver.find_element(By.XPATH,
                                                '//div[@id="recipehead"]//span[@id="ctl00_cntrightpanel_lblRecipeName"]')
                    titleText = "" if is_undefined_or_empty(title.text) else title.text
                    titleDataList.append(titleText)
                    print("**********************************************")
                    print("Title: " + titleText)
                    ingredientsArr = driver.find_elements(By.XPATH,
                                                          '//div[@id="rcpinglist"]//span[@itemprop="recipeIngredient"]')
                    ingredientsArrStrData = []
                    spanText = ""
                    for v in ingredientsArr:
                        spanText = v.text
                        ingredientsArrStrData.append(spanText)

                    ingredientsDataList.append(ingredientsArrStrData)
                    print("ingredients: " + str(ingredientsArrStrData))
                    spanText = ""
                    ingredientsArrStrData = []

                    method = driver.find_element(By.XPATH, "//div[@id='ctl00_cntrightpanel_pnlRcpMethod']/div").text
                    method = "" if is_undefined_or_empty(method) else method
                    methodDataList.append(method)
                    print("method: " + method)

                    dynamicElements = driver.find_elements(By.XPATH, "//div[@id='recipe_nutrients']/div//table")
                    nutrientValues = ""
                    if len(dynamicElements) != 0:
                        nutrientValues = driver.find_element(By.XPATH, "//div[@id='recipe_nutrients']/div//table").text
                        # If list size is non-zero, element is present
                        print("nutrientValues Element present : " + nutrientValues)
                    else:
                        print("nutrientValues element is not present")
                    nutrientValues = "" if is_undefined_or_empty(nutrientValues) else nutrientValues
                    nutrientValuesDataList.append(nutrientValues)

                    category = driver.find_element(By.XPATH, "//div[@id='recipe_tags']").text
                    print("category: " + category)
                    category = "" if is_undefined_or_empty(category) else category
                    categoryDataList.append(category)

                    imageLink = driver.find_element(By.XPATH, "//img[@id='ctl00_cntrightpanel_imgRecipe']").get_attribute(
                        "src")
                    print("imageLink: " + imageLink)
                    print("**********************************************")
                    imageLink = "" if is_undefined_or_empty(imageLink) else imageLink
                    imageLinkDataList.append(imageLink)
                except TimeoutException as e:
                    print(e.msg)
                    # logger.exception("TimeoutException error msg: ", e.msg)
                    continue
                except UnexpectedAlertPresentException as e1:
                    print(e1.msg)
                    # logger.exception("UnexpectedAlertPresentException error msg: ", e1.msg)
                    continue
                except Exception as e2:
                    print(e2.msg)
                    # logger.exception("Exception error msg: ", e2.msg)
                    continue

    except NoSuchElementException as e:
        print(e.msg)
        continue
    except Exception as e1:
        print(e1.msg)
        # logger.exception("Exception error msg: ", e1.msg)
        continue

print("")

scrapedDataDict["title"] = titleDataList
scrapedDataDict["ingredients"] = ingredientsDataList
scrapedDataDict["methods"] = methodDataList
scrapedDataDict["nutrientValues"] = nutrientValuesDataList
scrapedDataDict["category"] = categoryDataList
scrapedDataDict["imageLink"] = imageLinkDataList

df = pd.DataFrame(scrapedDataDict)
stop = timeit.default_timer()
print("")
print('Time taken to calculate and store into dataframe: ', stop - start)

# print(df)
if platform.system() == 'Darwin':
    df.to_excel('/Users/shibaramsahoo/Dropbox/Mamata NumpyNinja/PyCharm_Windows_WS/TasteOfIndia/output/scrappedfiles/tarladalalRecipes_Y.xlsx')
elif platform.system() == 'Windows':
    df.to_excel('C:\\Users\\shiba\\Dropbox\\Mamata NumpyNinja\\PyCharm_Windows_WS\\TasteOfIndia\\output\\scrappedfiles\\tarladalalRecipes_Y.xlsx')

stop2 = timeit.default_timer()
print("")
print('Time taken to write dataframe into Excel: ', stop2 - start)

