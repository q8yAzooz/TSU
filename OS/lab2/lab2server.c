#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/select.h>
#include <errno.h>

#define PORT 12345
#define BACKLOG 5
#define BUFFER_SIZE 1024

volatile sig_atomic_t got_sighup = 0;

// Signal handler for SIGHUP
void handle_signal(int sig) {
    if (sig == SIGHUP) {
        got_sighup = 1;
    }
}

// Initialize and configure the server socket
int setup_server_socket() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) == -1) {
        perror("bind");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, BACKLOG) == -1) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server is listening on port %d\n", PORT);
    return server_fd;
}

// Configure signal handling
void setup_signal_handling() {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sa.sa_flags = 0;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGHUP, &sa, NULL) == -1) {
        perror("sigaction");
        exit(EXIT_FAILURE);
    }
}

// Main server loop
void run_server(int server_fd) {
    int client_fd = -1;
    fd_set read_fds;
    sigset_t sigmask, origmask;
    char buffer[BUFFER_SIZE];

    sigemptyset(&sigmask);
    sigaddset(&sigmask, SIGHUP);

    if (sigprocmask(SIG_BLOCK, &sigmask, &origmask) == -1) {
        perror("sigprocmask");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    while (1) {
        // Prepare the file descriptor set
        FD_ZERO(&read_fds);
        FD_SET(server_fd, &read_fds);
        if (client_fd != -1) {
            FD_SET(client_fd, &read_fds);
        }

        int nfds = (client_fd > server_fd ? client_fd : server_fd) + 1;

        // Wait for activity on the file descriptors
        int ready = pselect(nfds, &read_fds, NULL, NULL, NULL, &origmask);
        if (ready == -1) {
            if (errno == EINTR) continue;
            perror("pselect");
            break;
        }

        // Handle SIGHUP
        if (got_sighup) {
            printf("Received SIGHUP\n");
            got_sighup = 0;
        }

        // Handle new connections
        if (FD_ISSET(server_fd, &read_fds)) {
            int new_fd = accept(server_fd, NULL, NULL);
            if (new_fd == -1) {
                perror("accept");
                continue;
            }
            printf("New connection received\n");

            if (client_fd == -1) {
                client_fd = new_fd;
            } else {
                printf("Connection closed (only one connection allowed)\n");
                close(new_fd);
            }
        }

        // Handle data from the client
        if (client_fd != -1 && FD_ISSET(client_fd, &read_fds)) {
            ssize_t bytes_read = recv(client_fd, buffer, sizeof(buffer), 0);
            if (bytes_read > 0) {
                printf("Received %zd bytes of data\n", bytes_read);
            } else if (bytes_read == 0) {
                printf("Client disconnected\n");
                close(client_fd);
                client_fd = -1;
            } else {
                perror("recv");
            }
        }
    }

    // Clean up
    close(server_fd);
    if (client_fd != -1) {
        close(client_fd);
    }
}

int main() {
    // Step 1: Set up the server socket
    int server_fd = setup_server_socket();

    // Step 2: Configure signal handling
    setup_signal_handling();

    // Step 3: Run the server loop
    run_server(server_fd);

    return 0;
}
