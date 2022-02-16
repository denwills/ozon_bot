
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

import time

if __name__ == '__main__':

    root_url = 'http://www.ozon.ru'
    SEARCH_PARAM_CLASS_ROOT_CATEGORY_0 = 'fv0 bp5 pb5 pb6'
    SEARCH_PARAM_CLASS_ROOT_CATEGORY_1 = 'fv0 bp5 p6b'
    SEARCH_PARAM_BUTTON_ALL_PRODUCTS = 'Смотреть все товары'
    SEARCH_PARAM_BUTTON_NEXT_PAGE = 'ui-b4 ui-c0'
    SEARCH_PARAM_CLASS_HREF_PRODUCT = 'tile-hover-target gz7'


# ************************** ЗАПУСК ДРАЙВЕРА *****************************************************

    time1 = time.time()
    Options = webdriver.ChromeOptions()
    #Options.add_argument('--headless')
    #Options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(options=Options)

    driver.get(root_url)
    #driver.implicitly_wait(10)

    # Нужна проверка на исключения по ошибкам (адрес, драйвер)

    # Нужна проверка на блок по признаку бота

    time2 = time.time()
    print(f'--Page {root_url} size: {len(driver.page_source)/1000} Kb, time: {time2-time1} s.')

# ************************** ЗАГРУЗКА КОРНЕВЫХ КАТЕГОРИЙ *****************************************************
    try:
        categories = driver.find_elements(By.XPATH, f".//a[@class='{SEARCH_PARAM_CLASS_ROOT_CATEGORY_0}']")
    except NoSuchElementException:
        pass

    __cat_name = ''
    __cat_href = ''

    if len(categories) == 0:
        print('--Categories was not found.')
    else:
        if len(categories) == 1:
            categories.extend(driver.find_elements(By.XPATH, f".//a[@class='{SEARCH_PARAM_CLASS_ROOT_CATEGORY_1}']"))

        for __cat in categories:
            __cat_href = __cat.get_attribute('href')
            __cat_name = __cat.get_attribute('text')
            print(f'{__cat_name} {__cat_href}')

        print(f'--Root categories ({len(categories)}) loaded.')



# ************************** ИНДЕКСИРОВАНИЕ ТОВАРОВ *****************************************************

    driver_cat = webdriver.Chrome(options=Options)
    for __cat in categories:
        __cat_href = __cat.get_attribute('href')
        __cat_name = __cat.get_attribute('text')

        time1 = time.time()
        driver_cat.get(__cat_href)

        time2 = time.time()
        print(f'|-->Page({__cat_name}) {__cat_href} '
              f'size: {len(driver_cat.page_source)/1000} Kb, time: {time2-time1} s.')

# ************************** ПЕРЕХОД К СПИСКУ ТОВАРОВ (ПОИСК КНОПКИ) ***************************************************
        time1 = 0
        time2 = 0

        try:    # поиск кнопки "Смотреть все товары"
            button = driver_cat.find_element(By.XPATH, f".//*[text() = '{SEARCH_PARAM_BUTTON_ALL_PRODUCTS}']")
        except NoSuchElementException: # кнопка не обнаружена
            pass
        else: # кнопка обнаружена

            try: # нажатие на кнопку (ожидание загрузки до появления кнопки "Далее")
                time1 = time.time()
                button.click()
                wait = WebDriverWait(driver_cat, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f".//div[@class='{SEARCH_PARAM_BUTTON_NEXT_PAGE}']")))
                time2 = time.time()
            except TimeoutException: # страница не загружена
                pass
            else:
                print(f'   |-->Page list products({__cat_name}) '
                      f'size: {len(driver_cat.page_source) / 1000} Kb, time: {time2 - time1} s.')

# ************************** АНАЛИЗ СПИСКА ТОВАРОВ *****************************************************

        products = driver_cat.find_elements(By.XPATH, f".//a[@class='{SEARCH_PARAM_CLASS_HREF_PRODUCT}']")
        for __prod in products:
            __prod_name = __prod.get_attribute('text')
            print(f'      |-->Product: {__prod_name}')

        driver_cat.back()

    driver_cat.close()
    driver.close()



