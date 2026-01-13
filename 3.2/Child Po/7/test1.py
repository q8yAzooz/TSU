#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("https://modrinth.com/")

try:
    # Проверка заголовка
    header = driver.find_element(By.XPATH, "//h1")
    assert "The place for Minecraft\nmods\nplugins" in header.text
    print("Тест 'Проверка наличия заголовка' - пройден")

    # Проверка поля поиска
    search = driver.find_element(By.XPATH, "//input[@type='search']")
    assert search.is_displayed()
    print("Тест 'Проверка наличия поля поиска' - пройден")

except Exception as e:
    print(f"Тест 'Проверка наличия элементов' - не пройден (ошибка: {str(e)})")

driver.quit()