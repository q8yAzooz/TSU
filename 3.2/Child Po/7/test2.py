#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("https://modrinth.com/")

try:
    # Клик по ссылке "Mods"
    link = driver.find_element(By.XPATH, "//a[contains(text(), 'Discover mods')]")
    link.click()

    # Проверка уникального элемента
    unique = driver.find_element(By.XPATH, "//span[contains(text(), 'Mods')]")
    assert "Mods" in unique.text
    print("Тест 'Проверка перехода по ссылке Mods' - пройден")

except Exception as e:
    print(f"Тест 'Проверка перехода по ссылке' - не пройден (ошибка: {str(e)})")

driver.quit()