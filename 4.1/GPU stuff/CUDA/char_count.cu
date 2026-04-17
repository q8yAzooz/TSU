
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define ALPHABET_SIZE 256

// CUDA kernel для подсчёта символов с использованием атомарных операций
__global__ void countChars(const unsigned char *text, int *counts, int textLength) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < textLength) {
        unsigned char ch = text[idx];
        atomicAdd(&counts[ch], 1);
    }
}

// CPU реализация для проверки
void countCharsCPU(const unsigned char *text, int *counts, int textLength) {
    for (int i = 0; i < textLength; i++) {
        counts[text[i]]++;
    }
}

// Генерация случайного текста
unsigned char* generateRandomText(int length) {
    unsigned char *text = (unsigned char*)malloc(length);
    for (int i = 0; i < length; i++) {
        text[i] = rand() % ALPHABET_SIZE;
    }
    return text;
}

// Проверка результатов
bool verifyResults(const int *cpu_counts, const int *gpu_counts) {
    for (int i = 0; i < ALPHABET_SIZE; i++) {
        if (cpu_counts[i] != gpu_counts[i]) {
            printf("Mismatch at char %d: CPU = %d, GPU = %d\n", i, cpu_counts[i], gpu_counts[i]);
            return false;
        }
    }
    return true;
}

int main() {
    int textLength;
    printf("Enter text length (e.g., 4000000): ");
    scanf("%d", &textLength);

    // Генерация текста
    srand(time(NULL));
    unsigned char *h_text = generateRandomText(textLength);
    size_t textBytes = textLength * sizeof(unsigned char);
    size_t countsBytes = ALPHABET_SIZE * sizeof(int);

    // CPU подсчёт
    int *h_cpu_counts = (int*)calloc(ALPHABET_SIZE, sizeof(int));
    clock_t cpu_start = clock();
    countCharsCPU(h_text, h_cpu_counts, textLength);
    clock_t cpu_end = clock();
    double cpu_time = (double)(cpu_end - cpu_start) / CLOCKS_PER_SEC * 1000.0;

    // Выделение памяти на GPU
    unsigned char *d_text;
    int *d_counts;
    cudaMalloc(&d_text, textBytes);
    cudaMalloc(&d_counts, countsBytes);
    cudaMemset(d_counts, 0, countsBytes);

    // Копирование текста на GPU
    cudaMemcpy(d_text, h_text, textBytes, cudaMemcpyHostToDevice);

    // Настройка сетки и блоков
    int threadsPerBlock = 256;
    int blocksPerGrid = (textLength + threadsPerBlock - 1) / threadsPerBlock;

    // Замер времени GPU
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start);

    // Запуск ядра
    countChars<<<blocksPerGrid, threadsPerBlock>>>(d_text, d_counts, textLength);
    cudaDeviceSynchronize();

    // Копирование результатов обратно
    int *h_gpu_counts = (int*)malloc(countsBytes);
    cudaMemcpy(h_gpu_counts, d_counts, countsBytes, cudaMemcpyDeviceToHost);

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float gpu_time = 0;
    cudaEventElapsedTime(&gpu_time, start, stop);

    // Проверка корректности
    bool isCorrect = verifyResults(h_cpu_counts, h_gpu_counts);

    // Вывод результатов (только первые 20 символов для наглядности)
    printf("\n=== Results ===\n");
    printf("Text length: %d characters\n", textLength);
    printf("CPU time: %.2f ms\n", cpu_time);
    printf("GPU time (copy + kernel + copy back): %.2f ms\n", gpu_time);
    printf("Results match: %s\n", isCorrect ? "TRUE" : "FALSE");

    printf("\nSample character counts (first 20):\n");
    for (int i = 0; i < 20; i++) {
        printf("Char %3d: CPU = %5d, GPU = %5d\n", i, h_cpu_counts[i], h_gpu_counts[i]);
    }

    // Освобождение памяти
    cudaFree(d_text);
    cudaFree(d_counts);
    free(h_text);
    free(h_cpu_counts);
    free(h_gpu_counts);

    return 0;
}
