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

start = timeit.default_timer()
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
driver.maximize_window()
baseUrl = "https://www.tarladalal.com/"
driver.get(baseUrl)

driver.implicitly_wait(5)
driver.find_element(By.XPATH, '//a[@href="RecipeAtoZ.aspx"]').click()
driver.find_element(By.LINK_TEXT, 'A').click()

scrapedDataDict = {}

titleDataList = []
ingredientsDataList = []
methodDataList = []
nutrientValuesDataList = []
categoryDataList = []
imageLinkDataList = []

pagesAtoZElements = driver.find_elements(By.XPATH, '//table[@id="ctl00_cntleftpanel_mnuAlphabets"]//table//a')
atoZ28pageNameUrlsLis = []
# for page in pagesAtoZElements:
#     pageName = page.get_attribute('text')
#     pageNameUrl = 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=' + pageName + '&pageindex=1'
#     atoZ28pageNameUrlsLis.append(pageNameUrl)

atoZ28pageNameUrlsLis.append('https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=Y&pageindex=1')
print("pageNameUrlsLis:" + str(atoZ28pageNameUrlsLis))


def is_undefined_or_empty(s):
    return bool((s is None) or (str(s).strip() == ""))


# Actual logic to start scraping for the 28 links A to Z, 0-9, Misc pages
for page in atoZ28pageNameUrlsLis:
    driver.get(page)
    print("After click Current Url: " + driver.current_url)

    mainParentPageUrl = driver.current_url

    try:
        # Skip the Scraping for pages containing no Recipes cards on those pages
        if driver.current_url == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=0-9&pageindex=1' or \
                driver.current_url == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=X&pageindex=1' or \
                driver.current_url == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=Misc&pageindex=1':
            print("Skipping current url: " + driver.current_url)
            continue

        # Find the Goto pages Last pagination value dynamically, as gotopage hyper links will showup on UI as 1-5 then ... then 9-13 then ... and 18-22
        allGotoPagesElementsList = driver.find_elements(By.XPATH, '//div[contains(text(), "Goto Page:")][1]/a')
        allGotoPagesElementsListLength = len(allGotoPagesElementsList)
        lastPageIndex = driver.find_element(By.XPATH, '//div[contains(text(), "Goto Page:")][1]/a[' + str(
            allGotoPagesElementsListLength) + ']')
        goToPagelastPaginationIndexVal = lastPageIndex.text
        print("Max Pagination size for this: " + goToPagelastPaginationIndexVal)

        # Create the list urls for recipe for A to Z
        allPaginationUrlsList = []
        lastPageIndexToVisit = int(goToPagelastPaginationIndexVal) + 1

        # Forloop to generate the 1 to 22 (or 82), pagination urls and store into a list
        for i in range(1, lastPageIndexToVisit):
            # recipeUrl = baseUrl + "RecipeAtoZ.aspx?pageindex=" + str(i)
            recipeUrl = page[0:page.rfind('=')] + "=" + str(i)
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + recipeUrl)
            allPaginationUrlsList.append(recipeUrl)

        print("Total no of " + str(len(allPaginationUrlsList)) + " Urls for Pagiantion dynamically build are: " + str(
            allPaginationUrlsList))

        # Iterating all the pagination urls captured above and visit that page by using driver.get and start reading individual recipe cards on each page
        for eachPaginationPage in allPaginationUrlsList:
            print("Navigating to pagination url: " + eachPaginationPage)
            driver.get(eachPaginationPage)
            print("Current Url now after clicking pagination link: " + driver.current_url)
            mainParentPageUrl = driver.current_url
            allRecipeElementsHyperLink = driver.find_elements(By.XPATH,
                                                              '//div[contains(text(), "Goto Page:")][1]/following-sibling::div[1]//div[@class="rcc_recipecard"]//span[@class="rcc_recipename"]/a')
            allRecipeElementsHyperLinkHrefList = []
            for hyperLink in allRecipeElementsHyperLink:
                allRecipeElementsHyperLinkHrefList.append(hyperLink.get_attribute('href'))

            print("All Hyper Links for Recipe on page: " + driver.current_url + " no of links : " + str(
                len(allRecipeElementsHyperLinkHrefList)) + " : " + str(allRecipeElementsHyperLinkHrefList))
            recipeCardsOnAPageCounter = 0

            print("")
            print("Going to read the hyperlinked page recipe.....")

            # Going to read the recipe Cards on this page and start actual scrapping for title, ingredients etc"
            for eachRecipePage in allRecipeElementsHyperLinkHrefList:

                try:
                    print(">>>>>>>>>> Navigating to recipe page: " + eachRecipePage)

                    # Go to the Actual Recipe page
                    driver.get(eachRecipePage)

                    recipeCardsOnAPageCounter = recipeCardsOnAPageCounter + 1
                    print("countHyperLinksOnThePage: " + str(recipeCardsOnAPageCounter))
                    print("Recipe page Link visting now: " + driver.current_url)

                    # Skip reading for receipt in the first 3 links (which are decorative item posts) on the first page
                    if mainParentPageUrl == 'https://www.tarladalal.com/RecipeAtoZ.aspx?beginswith=A&pageindex=1' and recipeCardsOnAPageCounter < 4:
                        print("--------> Going to skip this recipe card page : " + driver.current_url)
                        continue

                    print("")
                    print("--------> Going to read Title for page : " + driver.current_url)
                    title = driver.find_element(By.XPATH,
                                                '//div[@id="recipehead"]//span[@id="ctl00_cntrightpanel_lblRecipeName"]')
                    titleText = "" if is_undefined_or_empty(title.text) else title.text
                    titleDataList.append(titleText)
                    print("**********************************************")
                    print("Title: " + titleText)
                    ingredientsList = driver.find_elements(By.XPATH,
                                                           '//div[@id="rcpinglist"]//span[@itemprop="recipeIngredient"]')
                    ingredientsListStrData = []
                    spanText = ""
                    for ingredEle in ingredientsList:
                        spanText = ingredEle.text
                        ingredientsListStrData.append(spanText)

                    ingredientsDataList.append(ingredientsListStrData)
                    print("ingredients: " + str(ingredientsListStrData))
                    spanText = ""
                    ingredientsListStrData = []

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

                    imageLink = driver.find_element(By.XPATH,
                                                    "//img[@id='ctl00_cntrightpanel_imgRecipe']").get_attribute(
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
print('Time taken to calculate and store into dataframe: ', str(round((stop - start) / 60, 2)) + " minutes")

# print(df)
if platform.system() == 'Darwin':
    df.to_excel(
        '/Users/shibaramsahoo/Dropbox/Mamata NumpyNinja/PyCharm_Windows_WS/TasteOfIndia/output/scrappedfiles/tarladalalRecipes_Y.xlsx')
elif platform.system() == 'Windows':
    df.to_excel(
        'C:\\Users\\shiba\\Dropbox\\Mamata NumpyNinja\\PyCharm_Windows_WS\\TasteOfIndia\\output\\scrappedfiles\\tarladalalRecipes_Y.xlsx')

stop2 = timeit.default_timer()
print("")
print('Time taken to write dataframe into Excel: ', str(round((stop2 - start) / 60, 2)) + " minutes")

