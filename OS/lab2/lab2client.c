#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

// Параметры сервера
#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 12345

int main() {
    int sock;
    struct sockaddr_in server_addr;
    char message[] = "Hello, server!";
    char buffer[1024];
    ssize_t bytes_received;

    // Создаем TCP сокет
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock == -1) {
        perror("Error creating socket");
        exit(EXIT_FAILURE);
    }

    // Настройка адреса сервера
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);

    // Преобразуем IP-адрес из строкового в числовой формат
    if (inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr) <= 0) {
        perror("Invalid server IP address");
        close(sock);
        exit(EXIT_FAILURE);
    }

    // Подключаемся к серверу
    if (connect(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("Connection failed");
        close(sock);
        exit(EXIT_FAILURE);
    }
    printf("Connected to server at %s:%d\n", SERVER_IP, SERVER_PORT);

    // Отправляем сообщение серверу
    if (send(sock, message, strlen(message), 0) == -1) {
        perror("Failed to send message");
        close(sock);
        exit(EXIT_FAILURE);
    }
    printf("Sent message: %s\n", message);

    // Ожидаем ответ от сервера
    bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
    if (bytes_received > 0) {
        buffer[bytes_received] = '\0'; // Завершаем строку
        printf("Received from server: %s\n", buffer);
    } else if (bytes_received == 0) {
        printf("Server closed connection.\n");
    } else {
        perror("Failed to receive message");
    }

    // Закрываем сокет
    close(sock);
    printf("Connection closed.\n");
    return 0;
}
