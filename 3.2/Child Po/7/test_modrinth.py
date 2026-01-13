import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service

@pytest.fixture
def driver():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# Проверка наличия и оформления элементов 
def test_elements_header_presence(driver):
    driver.get("https://modrinth.com/")
    header = driver.find_element(By.XPATH, "//div[@id='__nuxt']/div[4]/header/div[2]/div/div/button")
    assert "Discover" in header.text, "Тест 'Наличие кнопки Discover в заголовке' - не пройден (кнопка не найдена)"
    assert header.is_displayed(), "Тест 'Наличие кнопки Discover в заголовке' - не пройден (кнопка не отображается)"
    print("Тест 'Наличие кнопки Discover в заголовке' - пройден")

def test_elements_search_field(driver):
    driver.get("https://modrinth.com/")
    search = driver.find_element(By.XPATH, "//input[@type='search']")
    assert search.is_displayed(), "Тест 'Наличие и оформление поля поиска' - не пройден (поле поиска не отображается)"
    assert search.get_attribute("placeholder"), "Тест 'Наличие и оформление поля поиска' - не пройден (поле поиска не имеет плейсхолдера)"
    print("Тест 'Наличие и оформление поля поиска' - пройден")

def test_elements_discover_mods_link(driver):
    driver.get("https://modrinth.com/")
    link = driver.find_element(By.LINK_TEXT, "Discover mods")
    assert link.is_displayed(), "Тест 'Наличие и оформление ссылки Discover mods' - не пройден (ссылка не отображается)"
    assert "mods" in link.get_attribute("href"), "Тест 'Наличие и оформление ссылки Discover mods' - не пройден (ссылка не ведет на моды)"
    print("Тест 'Наличие и оформление ссылки Discover mods' - пройден")

# Категория 2: Проверка переходов по ссылкам (2 теста)
def test_navigation_mods_link(driver):
    driver.get("https://modrinth.com/")
    link = driver.find_element(By.LINK_TEXT, "Discover mods")
    link.click()
    unique_element = driver.find_element(By.XPATH, "//h3[contains(text(), 'Game version')]")
    assert unique_element.is_displayed(), "Тест 'Переход по ссылке Discover mods' - не пройден (уникальный элемент не найден)"
    print("Тест 'Переход по ссылке Discover mods' - пройден")

def test_navigation_logo_to_home(driver):
    driver.get("https://modrinth.com/mods")
    logo = driver.find_element(By.CSS_SELECTOR, ".h-7")
    logo.click()
    unique_element = driver.find_element(By.CSS_SELECTOR, ".landing-hero > .modrinth-icon")
    assert unique_element.is_displayed(), "Тест 'Переход на главную через логотип' - не пройден (уникальный элемент не найден)"
    print("Тест 'Переход на главную через логотип' - пройден")

#  Полный пользовательский сценарий 
def test_full_scenario_search_and_navigate(driver):
    driver.get("https://modrinth.com/")
    mods = driver.find_element(By.LINK_TEXT, "Discover mods")
    mods.click()
    search = driver.find_element(By.XPATH, "//input[@type='text' and @placeholder='Search mods...']")
    search.send_keys("Sodium" + Keys.ENTER)
    mod_link = driver.find_element(By.XPATH, "//a[@href='/mod/sodium']")
    mod_link.click()
    mod_title = driver.find_element(By.CSS_SELECTOR, ".font-extrabold:nth-child(1)")
    assert "Sodium" in mod_title.text, "Тест 'Полный сценарий: поиск и переход к Sodium' - не пройден (переход не выполнен)"
    print("Тест 'Полный сценарий: поиск и переход к Sodium' - пройден")

def test_full_scenario_search_and_download(driver):
    driver.get("https://modrinth.com/")
    mods = driver.find_element(By.LINK_TEXT, "Discover mods")
    mods.click()
    search = driver.find_element(By.XPATH, "//input[@type='text' and @placeholder='Search mods...']")
    search.send_keys("Sodium" + Keys.ENTER)
    driver.find_element(By.CSS_SELECTOR, ".project-card:nth-child(1) .name").click()
    driver.find_element(By.CSS_SELECTOR, ".hidden > .btn-wrapper > button").click()
    driver.find_element(By.CSS_SELECTOR, "div:nth-child(1) > .btn-wrapper > .\\!w-full").click()
    driver.find_element(By.CSS_SELECTOR, ".bottom-fade .btn-wrapper:nth-child(1) > button").click()
    driver.find_element(By.CSS_SELECTOR, ".scrollable-pane-wrapper:nth-child(1) .btn-wrapper:nth-child(2) > button").click()
    download_link = driver.find_element(By.LINK_TEXT, "Download")
    assert download_link.is_displayed(), "Тест 'Полный сценарий: поиск и скачивание мода' - не пройден (ссылка на скачивание не найдена)"
    print("Тест 'Полный сценарий: поиск и скачивание мода' - пройден")