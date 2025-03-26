from collections import defaultdict, Counter
import numpy as np
import pandas as pd

class LanguageNgramModel:
    """
    order - порядок (сколько предыдущих букв помнит модель), или n-1
    smoothing - величина, добавляемая к каждому счётчику букв для устойчивости
    recursive - вес, с которым используется модель на один порядок меньше
    Обучаемые параметры:
    counter_ - хранилище частот n-грам, в виде словаря счётчиков. 
    vocabulary_ - множество всех символов, учитываемых моделью
    
    """
    def __init__(self, order=1, smoothing=1.0, recursive=0.001):
        self.order = order
        self.smoothing = smoothing
        self.recursive = recursive
    
    def fit(self, corpus):
        """
        corpus - текстовая строка. 
        """
        self.counter_ = defaultdict(lambda: Counter())
        self.vocabulary_ = set()
        for i, token in enumerate(corpus[self.order:]):
            context = corpus[i:(i+self.order)]
            self.counter_[context][token] += 1
            self.vocabulary_.add(token)
        self.vocabulary_ = sorted(list(self.vocabulary_))
        if self.recursive > 0 and self.order > 0:
            self.child_ = LanguageNgramModel(self.order-1, self.smoothing, self.recursive)
            self.child_.fit(corpus)
            
    def get_counts(self, context):
        """
        context - текстовая строка (учиываются только последние self.order символов)
        Возвращает: 
        freq - вектор условных частот букв, в форме pandas.Series
        """
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        freq_dict = self.counter_[local]
        freq = pd.Series(index=self.vocabulary_)
        for i, token in enumerate(self.vocabulary_):
            freq[token] = freq_dict[token] + self.smoothing
        if self.recursive > 0 and self.order > 0:
            child_freq = self.child_.get_counts(context) * self.recursive
            freq += child_freq
        return freq
    
    def predict_proba(self, context):
        """
        context - текстовая строка (учиываются только последние self.order символов)
        Возвращает: 
        freq - вектор условных вероятностей букв, в форме pandas.Series  
        """
        counts = self.get_counts(context)
        return counts / counts.sum()
    
    def single_log_proba(self, context, continuation):
        """
        context - текстовая строка, известное начало фразы
        continuation - текстовая строка, гипотетическое продолжение фразы
        """
        result = 0.0
        for token in continuation:
            result += np.log(self.predict_proba(context)[token])
            context += token
        return result
    
    def single_proba(self, context, continuation):
        """
        context - текстовая строка, известное начало фразы
        continuation - текстовая строка, гипотетическое продолжение фразы
        """
        return np.exp(self.single_log_proba(context, continuation))
    

"""
=======================================================================================================================================================================================
"""


class MissingLetterModel:
    """
    order - порядок, или n+1
    smoothing_missed - число, прибавляемое к счётчику пропущенных символов
    smoothing_total - число, прибавляемое к счётчику всех символов
    """
    def __init__(self, order=0, smoothing_missed=0.3, smoothing_total=1.0):
        self.order = order
        self.smoothing_missed = smoothing_missed
        self.smoothing_total = smoothing_total
    
    def fit(self, sentence_pairs):
        """
        sentence_pairs - список пар (исходная фраза, сокращение)
        В сокращении все пропущенные символы заменены на дефисы. 
        """
        self.missed_counter_ = defaultdict(lambda: Counter())
        self.total_counter_ = defaultdict(lambda: Counter())
        for (original, observed) in sentence_pairs:
            for i, (original_letter, observed_letter) in enumerate(zip(original[self.order:], observed[self.order:])):
                context = original[i:(i+self.order)]
                if observed_letter == '-':
                    self.missed_counter_[context][original_letter] += 1
                self.total_counter_[context][original_letter] += 1 
    
    def predict_proba(self, context, last_letter):
        if self.order:
            local = context[-self.order:]
        else:
            local = ''
        missed_freq = self.missed_counter_[local][last_letter] + self.smoothing_missed
        total_freq = self.total_counter_[local][last_letter] + self.smoothing_total
        return missed_freq / total_freq
    
    def single_log_proba(self, context, continuation, actual=None):
        """ 
        Оценка логарифма вероятности того, после фразы context фраза continuation трансформируется в actual
        Если actual не указана, предполагается, что continuation не изменяется. 
        """
        if not actual:
            actual = continuation
        result = 0.0
        for orig_token, act_token in zip(continuation, actual):
            pp = self.predict_proba(context, orig_token)
            if act_token != '-':
                pp = 1 - pp
            result += np.log(pp)
            context += orig_token
        return result
    
    def single_proba(self, context, continuation, actual=None):
        """ 
        Оценка вероятности того, после фразы context фраза continuation трансформируется в actual
        Если actual не указана, предполагается, что continuation не изменяется. 
        """
        return np.exp(self.single_log_proba(context, continuation, actual))
    
    
from heapq import heappush, heappop

def generate_options(prefix_proba, prefix, suffix, lang_model, missed_model, optimism=0.5, cache=None):
    """ Генерация вариантов расшифровки аббревиатуры (вспомогательная функция)
    Параметры:
    prefix_proba - правдоподобие расшифрованной части аббревиатуры
    prefix - расшифрованная часть аббревиатуры
    suffix - не расшифрованная часть аббревиатуры
    lang_model - модель языка
    missed_model - модель вероятности сокращений
    optimism - коэффициент, с которым учитывается не объясненный конец слова
    cache - хранилище оценок качества концов слова
    Возвращает: список опций в форме (оценка качества, расшифрованная часть, не расшифрованная часть, новая буква, оценка качества не расшифрованной части)
    """
    options = []
    for letter in lang_model.vocabulary_ + ['']:
        if letter:  # тут мы считаем, что буква была пропущена
            next_letter = letter
            new_suffix = suffix
            new_prefix = prefix + next_letter
            proba_missing_state = - np.log(missed_model.predict_proba(prefix, letter))
        else:  # тут мы считаем, что пропущенной буквы не было
            next_letter = suffix[0]
            new_suffix = suffix[1:]
            new_prefix = prefix + next_letter
            proba_missing_state = - np.log((1 - missed_model.predict_proba(prefix, next_letter)))
        proba_next_letter = - np.log(lang_model.single_proba(prefix, next_letter))
        if cache:
            proba_suffix = cache[len(new_suffix)] * optimism
        else:
            proba_suffix = - np.log(lang_model.single_proba(new_prefix, new_suffix)) * optimism
        proba = prefix_proba + proba_next_letter + proba_missing_state + proba_suffix
        options.append((proba, new_prefix, new_suffix, letter, proba_suffix))
    return options




def noisy_channel(word, lang_model, missed_model, freedom=3.0, max_attempts=10000, optimism=0.9, verbose=False):
    """
    word - аббревиатура
    lang_model - модель языка
    missed_model - модель вероятности сокращений
    freedom - возможный зазор по оценке логарифма правдоподобия кандидатов
    max_attempts - число итераций
    optimism - коэффициент, с которым учитывается не объясненный конец слова
    verbose - печатать ли наилучших текущих кандидатов в ходе исполнения функции
    Возвращает: словарик с ключами - расшифровками и значениями - минус логарифмом правдоподобия расшифровок. 
    Чем меньше значение, тем правдоподобнее расшифровка. 
    """
    query = word + ' '
    prefix = ' '
    prefix_proba = 0.0
    suffix = query
    full_origin_logprob = -lang_model.single_log_proba(prefix, query)
    no_missing_logprob = -missed_model.single_log_proba(prefix, query)
    best_logprob = full_origin_logprob + no_missing_logprob
    # добавляем в кучу пустое начало
    heap = [(best_logprob * optimism, prefix, suffix, '', best_logprob * optimism)]
    # добавляем в кандидаты расшифровку по умолчанию - без пропущенных букв
    candidates = [(best_logprob, prefix + query, '', None, 0.0)]
    if verbose:
        print('baseline score is', best_logprob)
    # готовим хранилище вероятностей конфов слов
    cache = {}
    for i in range(len(query)+1):
        future_suffix = query[:i]
        cache[len(future_suffix)] = -lang_model.single_log_proba('', future_suffix) # rough approximation
        cache[len(future_suffix)] += -missed_model.single_log_proba('', future_suffix) # at least add missingness
    
    for i in range(max_attempts):
        if not heap:
            break
        next_best = heappop(heap)
        if verbose:
            print(next_best)
        if next_best[2] == '':  # слово расшифровано до конца
            # если оно достаточно хорошее, добавим его в кандидаты
            if next_best[0] <= best_logprob + freedom:
                candidates.append(next_best)
                # обновим наилучшую оценку правдоподобия
                if next_best[0] < best_logprob:
                    best_logprob = next_best[0]
        else: # it is not a leaf - generate more options
            prefix_proba = next_best[0] - next_best[4] # all proba estimate minus suffix
            prefix = next_best[1]
            suffix = next_best[2]
            new_options = generate_options(prefix_proba, prefix, suffix, lang_model, missed_model, optimism, cache)
            # add only the solution potentioally no worse than the best + freedom
            for new_option in new_options: 
                if new_option[0] < best_logprob + freedom:
                    heappush(heap, new_option)
    if verbose:
        print('heap size is', len(heap), 'after', i, 'iterations')
    result = {}
    for candidate in candidates:
        if candidate[0] <= best_logprob + freedom:
            result[candidate[1][1:-1]] = candidate[0]
    return result

from heapq import heappush, heappop

import re
# считываем текст
with open('book.txt', encoding = 'Windows-1251') as f:
    text = f.read()
# оставляем только буквы и пробелы в тексте
text2 = re.sub(r'[^а-я ]+', '', text.lower().replace('\n', ' '))
all_letters = ''.join(list(sorted(list(set(text2)))))
print(repr(all_letters)) # ' abcdefghijklmnopqrstuvwxyz'
# готовим обучающую выборку для модели опечаток:
missing_set =  (
    [(all_letters, '-' * len(all_letters))] * 3 # тут считаем все буквы пропущенными
    + [(all_letters, all_letters)] * 10 # тут считаем все буквы НЕ пропущенными
    + [('уеыаоэяию', '------')] * 30 # тут считаем пропущенными только гласные
)
# обучаем обе модели
big_lang_m = LanguageNgramModel(order=4, smoothing=0.001, recursive=0.01)
big_lang_m.fit(text2)
big_err_m = MissingLetterModel(order=0, smoothing_missed=0.1)
big_err_m.fit(missing_set)

print(noisy_channel('мсн', big_lang_m, big_err_m))

print(noisy_channel('дб', big_lang_m, big_err_m))

print(noisy_channel('апт', big_lang_m, big_err_m))

print(noisy_channel('судр', big_lang_m, big_err_m))

