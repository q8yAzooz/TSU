import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

class TestFullUserScenario():
    def setup_method(self, method):
        self.driver = webdriver.Chrome()
        self.vars = {}
    
    def teardown_method(self, method):
        self.driver.quit()
    
    def test_full_user_scenario(self, step_tracker):
        # Step 1: Открытие главной страницы
        step_tracker.step(lambda: self.driver.get("https://learn.microsoft.com/ru-ru/"), step_name="Открытие главной страницы")
        time.sleep(2)
        
        # Step 2: Проверка наличия глобального поля поиска
        def check_search_block():
            elements = self.driver.find_elements(By.CSS_SELECTOR, ".hero-content")
            assert len(elements) > 0, "Блок поиска (.hero-content) не найден"
            return elements
        step_tracker.step(check_search_block, step_name="Проверка наличия блока поиска")
        
        # Step 3: Активация поля поиска и ввод запроса
        def activate_and_input():
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".margin-left-xxs > .button .docon")))
            search_button.click()
            input_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "site-header-search-autocomplete-input")))
            input_field.clear()
            input_field.send_keys("python")
            input_field.send_keys(Keys.ENTER)
        step_tracker.step(activate_and_input, step_name="Ввод запроса 'python' в глобальное поле поиска и отправка поиска")
        time.sleep(2)
        
        # Step 4: Переход по первой ссылке в результатах поиска
        def click_first_result():
            try:
                first_result = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "ul > li > h2 > a")))
                link_text = first_result.text
                first_result.click()
                return link_text
            except Exception as e:
                # Диагностика: логируем HTML блока результатов
                try:
                    results_block = self.driver.find_element(By.CSS_SELECTOR, "ul")
                    print("HTML блока результатов поиска:\n", results_block.get_attribute("outerHTML"))
                except Exception as inner_e:
                    print("Не удалось получить HTML блока результатов поиска:", inner_e)
                raise e
        resource_title = step_tracker.step(click_first_result, step_name="Переход по первой ссылке в результатах поиска")
        time.sleep(2)
        
        # Step 5: Проверка, что перешли на нужный источник (заголовок совпадает)
        def check_resource():
            header = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
            page_title = header.text.strip().lower()
            search_title = resource_title.strip().lower()
            assert page_title in search_title or search_title in page_title, (
                f"Заголовок на странице ('{page_title}') не совпадает с заголовком из поиска ('{search_title}')"
            )
            return header
        step_tracker.step(check_resource, step_name="Проверка, что открыт нужный источник по заголовку")
