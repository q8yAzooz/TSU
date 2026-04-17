import re
import sys
from collections import defaultdict
from typing import List, Tuple, Optional

import pymorphy3


def load_text_from_file(filepath: str) -> str:
    """Загружает текст из файла."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Ошибка: файл '{filepath}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)


def tokenize_text(text: str) -> List[str]:
    """
    Разбивает текст на слова (токены).
    Словами считаются последовательности русских букв (включая ё),
    разделённые небуквенными символами.
    """
    # Регулярное выражение для русских слов (включая букву ё)
    russian_word_pattern = re.compile(r'[а-яА-ЯёЁ]+')
    tokens = russian_word_pattern.findall(text)
    return tokens


def get_word_info(word: str, morph: pymorphy3.MorphAnalyzer) -> Optional[Tuple[str, str, str, str]]:
    """
    Возвращает информацию о слове: лемму, часть речи, род, число, падеж.
    Если слово не удалось разобрать или оно не является существительным или прилагательным,
    возвращает None.
    """
    parsed = morph.parse(word)[0]  # Берём наиболее вероятный вариант разбора
    
    # Проверяем, что слово является существительным или прилагательным
    pos = parsed.tag.POS
    if pos not in ('NOUN', 'ADJF'):
        return None
    
    # Получаем грамматические характеристики
    # Для прилагательных род, число, падеж берутся из tag
    # Для существительных тоже из tag
    gender = parsed.tag.gender
    number = parsed.tag.number
    case = parsed.tag.case
    
    # Если какой-то из параметров отсутствует, слово не подходит
    if gender is None or number is None or case is None:
        return None
    
    lemma = parsed.normal_form
    return (lemma, pos, gender, number, case)


def check_compatibility(info1: Tuple[str, str, str, str], 
                        info2: Tuple[str, str, str, str]) -> bool:
    """
    Проверяет, совпадают ли два слова по роду, числу и падежу.
    """
    # info: (lemma, pos, gender, number, case)
    return (info1[2] == info2[2] and   # род
            info1[3] == info2[3] and   # число
            info1[4] == info2[4])      # падеж


def main():
    # Инициализация морфологического анализатора
    try:
        morph = pymorphy3.MorphAnalyzer()
    except Exception as e:
        print(f"Ошибка инициализации pymorphy3: {e}")
        print("Убедитесь, что библиотека установлена: pip install pymorphy3 pymorphy3-dicts")
        sys.exit(1)
    
    # Проверка аргументов командной строки
    if len(sys.argv) < 2:
        print("Использование: python script.py <путь_к_файлу>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # Чтение текста
    text = load_text_from_file(filepath)
    
    # Токенизация
    words = tokenize_text(text)
    
    # Сбор информации о каждом слове
    words_info = []  # список кортежей (слово, информация) или None
    for word in words:
        info = get_word_info(word.lower(), morph)
        words_info.append((word, info))
    
    # Поиск пар соседних слов, удовлетворяющих условиям
    pairs = []
    for i in range(len(words_info) - 1):
        word1, info1 = words_info[i]
        word2, info2 = words_info[i + 1]
        
        # Пропускаем, если хотя бы одно слово не подходит
        if info1 is None or info2 is None:
            continue
        
        # Проверяем, что на первом или втором месте есть сущ. или прил.
        # Условие: оба слова уже являются сущ. или прил. (мы это проверили при получении info)
        # Или условие "имеют существительные или прилагательные на первом или втором месте"
        # Так как мы уже отфильтровали, что оба слова — сущ. или прил., условие выполнено.
        
        # Проверка совпадения по роду, числу, падежу
        if check_compatibility(info1, info2):
            # Выводим пару лемм
            lemma1, lemma2 = info1[0], info2[0]
            pairs.append((lemma1, lemma2))
    
    # Вывод результатов
    for lemma1, lemma2 in pairs:
        print(f"{lemma1} {lemma2}")


if __name__ == "__main__":
    main()