#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

options = Options()
driver = webdriver.Firefox(options=options)
driver.get("https://modrinth.com/mods")

try:
    # Ожидание и поиск поля ввода
    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@type='search']"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
    search_input.click()
    search_input.clear()
    search_input.send_keys("Sodium")
    print("Текст 'Sodium' введен в поле поиска")

    # Найти и кликнуть по кнопке поиска
    search_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Search')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
    search_button.click()
    print("Клик по кнопке поиска выполнен")

    # Ожидание и проверка результатов
    mod_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Sodium')]"))
    )
    assert "Sodium" in mod_link.text, "Mod 'Sodium' not found in results"
    print("Тест 'Поиск мода Sodium на странице mods' - пройден")

except Exception as e:
    print(f"Тест 'Поиск мода Sodium на странице mods' - не пройден (ошибка: {str(e)})")

finally:
    driver.quit()
