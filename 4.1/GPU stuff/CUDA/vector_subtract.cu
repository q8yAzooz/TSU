
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// CUDA kernel для поэлементного вычитания: C[i] = A[i] - B[i]
__global__ void vectorSubtract(const float *A, const float *B, float *C, int N) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < N) {
        C[idx] = A[idx] - B[idx];
    }
}

// Функция для проверки результатов
bool verifyResult(const float *cpu_C, const float *gpu_C, int N) {
    for (int i = 0; i < N; i++) {
        if (cpu_C[i] != gpu_C[i]) {
            printf("Mismatch at index %d: CPU = %f, GPU = %f\n", i, cpu_C[i], gpu_C[i]);
            return false;
        }
    }
    return true;
}

int main() {
    int N;
    printf("Enter vector size (e.g., 1000000): ");
    scanf("%d", &N);

    // Выделение памяти на хосте
    size_t bytes = N * sizeof(float);
    float *h_A = (float*)malloc(bytes);
    float *h_B = (float*)malloc(bytes);
    float *h_C_cpu = (float*)malloc(bytes);
    float *h_C_gpu = (float*)malloc(bytes);

    // Инициализация случайными числами
    srand(time(NULL));
    for (int i = 0; i < N; i++) {
        h_A[i] = (float)(rand() % 100) / 10.0f;
        h_B[i] = (float)(rand() % 100) / 10.0f;
    }

    // CPU вычисления
    clock_t cpu_start = clock();
    for (int i = 0; i < N; i++) {
        h_C_cpu[i] = h_A[i] - h_B[i];
    }
    clock_t cpu_end = clock();
    double cpu_time = (double)(cpu_end - cpu_start) / CLOCKS_PER_SEC * 1000.0;

    // Выделение памяти на устройстве
    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);

    // Копирование данных на устройство
    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);

    // Настройка сетки и блоков
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;

    // Замер времени GPU (копирование + ядро + копирование обратно)
    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);
    cudaEventRecord(start);

    // Запуск ядра
    vectorSubtract<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);
    cudaDeviceSynchronize();

    // Копирование результата обратно
    cudaMemcpy(h_C_gpu, d_C, bytes, cudaMemcpyDeviceToHost);

    cudaEventRecord(stop);
    cudaEventSynchronize(stop);
    float gpu_time = 0;
    cudaEventElapsedTime(&gpu_time, start, stop);

    // Проверка корректности
    bool isCorrect = verifyResult(h_C_cpu, h_C_gpu, N);
    printf("\n=== Results ===\n");
    printf("Vector size: %d\n", N);
    printf("CPU time: %.2f ms\n", cpu_time);
    printf("GPU time (copy + kernel + copy back): %.2f ms\n", gpu_time);
    printf("Results match: %s\n", isCorrect ? "TRUE" : "FALSE");

    // Освобождение памяти
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    free(h_A);
    free(h_B);
    free(h_C_cpu);
    free(h_C_gpu);

    return 0;
}
