#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <errno.h>

#define PORT 12345        // Порт, на котором сервер будет принимать подключения
#define BACKLOG 5         // Максимальная очередь подключений
#define BUFFER_SIZE 1024  // Размер буфера для приема данных

// Глобальная переменная для обработки сигнала SIGHUP
volatile sig_atomic_t got_sighup = 0;

// Обработчик сигнала SIGHUP
void handle_signal(int sig) {
    if (sig == SIGHUP) {
        got_sighup = 1;  // Устанавливаем флаг, что был получен сигнал SIGHUP
    }
}

// Функция для создания и настройки серверного сокета
int setup_server_socket() {
    // Создаем сокет TCP (IPv4)
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("Ошибка при создании сокета");
        exit(EXIT_FAILURE);
    }

    // Настраиваем параметры адреса сервера
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;             // IPv4
    server_addr.sin_addr.s_addr = INADDR_ANY;     // Любой локальный адрес
    server_addr.sin_port = htons(PORT);           // Порт сервера (с переводом в сетевой порядок байтов)

    // Привязываем сокет к указанному адресу и порту
    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Ошибка при привязке сокета");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Переводим сокет в режим ожидания входящих подключений
    if (listen(server_fd, BACKLOG) == -1) {
        perror("Ошибка при установке режима прослушивания");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Сервер слушает порт %d\n", PORT);
    return server_fd;  // Возвращаем дескриптор серверного сокета
}

// Функция для настройки обработки сигналов
void setup_signal_handling() {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;  // Указываем обработчик для SIGHUP
    sa.sa_flags = 0;
    sigemptyset(&sa.sa_mask);

    // Устанавливаем обработчик сигнала SIGHUP
    if (sigaction(SIGHUP, &sa, NULL) == -1) {
        perror("Ошибка при настройке обработки сигналов");
        exit(EXIT_FAILURE);
    }
}

// Главный цикл сервера
void run_server(int server_fd) {
    int client_fd = -1;              // Дескриптор клиентского сокета
    fd_set read_fds;                 // Множество дескрипторов для select
    sigset_t sigmask, origmask;      // Маски для управления сигналами
    char buffer[BUFFER_SIZE];        // Буфер для приема данных

    // Блокируем сигнал SIGHUP для корректной обработки в pselect
    sigemptyset(&sigmask);
    sigaddset(&sigmask, SIGHUP);
    if (sigprocmask(SIG_BLOCK, &sigmask, &origmask) == -1) {
        perror("Ошибка при блокировке сигналов");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    while (1) {
        // Подготавливаем множество дескрипторов для проверки
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);  // Добавляем серверный сокет
        if (client_fd != -1) {
            FD_SET(client_fd, &read_fds);  // Добавляем клиентский сокет, если клиент подключен
        }

        // Определяем максимальный дескриптор для pselect
        int nfds = (client_fd > server_fd ? client_fd : server_fd) + 1;

        // Ожидаем активности с учетом сигналов
        int ready = pselect(nfds, &read_fds, NULL, NULL, NULL, &origmask);
        if (ready == -1) {
            if (errno == EINTR) continue;  // Игнорируем прерывания вызовом сигналов
            perror("Ошибка при вызове pselect");
            break;
        }

        // Обрабатываем сигнал SIGHUP
        if (got_sighup) {
            printf("Получен сигнал SIGHUP\n");
            got_sighup = 0;  // Сбрасываем флаг
        }

        // Обрабатываем новые подключения
        if (FD_ISSET(server_fd, &read_fds)) {
            int new_fd = accept(server_fd, NULL, NULL);
            if (new_fd == -1) {
                perror("Ошибка при принятии подключения");
                continue;
            }
            printf("Получено новое подключение\n");

            if (client_fd == -1) {
                client_fd = new_fd;  // Устанавливаем текущего клиента
            } else {
                printf("Отключение нового клиента (разрешено только одно подключение)\n");
                close(new_fd);  // Закрываем новое подключение
            }
        }

        // Обрабатываем данные от клиента
        if (client_fd != -1 && FD_ISSET(client_fd, &read_fds)) {
            ssize_t bytes_read = recv(client_fd, buffer, sizeof(buffer), 0);
            if (bytes_read > 0) {
                printf("Получено %zd байт данных\n", bytes_read);
                // Здесь можно добавить обработку полученных данных
            } else if (bytes_read == 0) {
                printf("Клиент отключился\n");
                close(client_fd);
                client_fd = -1;  // Освобождаем дескриптор клиентского сокета
            } else {
                perror("Ошибка при получении данных");
            }
        }
    }

    // Очистка ресурсов
    close(server_fd);
    if (client_fd != -1) {
        close(client_fd);
    }
}

// Главная функция программы
int main() {
    // Шаг 1: Настраиваем серверный сокет
    int server_fd = setup_server_socket();

    // Шаг 2: Настраиваем обработку сигналов
    setup_signal_handling();

    // Шаг 3: Запускаем главный цикл сервера
    run_server(server_fd);

    return 0;
}
