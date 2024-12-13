#include <stdio.h>
#include <pthread.h>
#include <unistd.h>

// Условная переменная и мьютекс для синхронизации
pthread_cond_t cond1 = PTHREAD_COND_INITIALIZER;
pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;

// Флаг состояния
int ready = 0;

// Функция производителя
void* supplier(void* arg) {
    while (1) {
        pthread_mutex_lock(&lock);
        if (ready == 1) {
            pthread_mutex_unlock(&lock);
            continue;
        }
        ready = 1;
        printf("Provided\n");
        pthread_cond_signal(&cond1); // Сигнал потребителю
        pthread_mutex_unlock(&lock);
        sleep(1); // Имитируем работу производителя
    }
    return NULL;
}

// Функция потребителя
void* consumer(void* arg) {
    while (1) {
        pthread_mutex_lock(&lock);
        while (ready == 0) { // Ожидаем, пока ресурс не станет доступным
            pthread_cond_wait(&cond1, &lock);
        }
        ready = 0;
        printf("Consumed\n");
        pthread_mutex_unlock(&lock);
        sleep(2); // Имитируем работу потребителя
    }
    return NULL;
}

// Основная функция
int main() {
    pthread_t supplier_thread, consumer_thread;

    // Создаем потоки производителя и потребителя
    pthread_create(&supplier_thread, NULL, supplier, NULL);
    pthread_create(&consumer_thread, NULL, consumer, NULL);

    // Ожидаем завершения потоков
    pthread_join(supplier_thread, NULL);
    pthread_join(consumer_thread, NULL);

    return 0;
}
