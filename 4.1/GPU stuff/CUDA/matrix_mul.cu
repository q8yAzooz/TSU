
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <cmath>
#include <cuda_runtime.h>

#define CUDA_CHECK(call) \
    do { \
        cudaError_t status = (call); \
        if (status != cudaSuccess) { \
            std::cerr << "CUDA Error: " << cudaGetErrorString(status) << "\n"; \
            std::exit(EXIT_FAILURE); \
        } \
    } while (0)

constexpr int BLOCK_SZ = 16;

void multiplyOnCPU(const float* mtxA, const float* mtxB, float* result, int rows, int innerDim)
{
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < rows; ++j) {
            float accumulator = 0.0f;
            for (int k = 0; k < innerDim; ++k) {
                accumulator += mtxA[i * innerDim + k] * mtxB[k * rows + j];
            }
            result[i * rows + j] = accumulator;
        }
    }
}


bool verifyResults(const std::vector<float>& cpuRes, const std::vector<float>& gpuRes)
{
    constexpr float tolerance = 1e-2f;
    for (size_t idx = 0; idx < cpuRes.size(); ++idx) {
        if (std::fabs(cpuRes[idx] - gpuRes[idx]) > tolerance) {
            return false;
        }
    }
    return true;
}

__global__ void multiplyOnGPU(const float* __restrict__ A,
    const float* __restrict__ B,
    float* C,
    int n, int m)
{
    __shared__ float tileA[BLOCK_SZ][BLOCK_SZ];
    __shared__ float tileB[BLOCK_SZ][BLOCK_SZ];

    int rowIdx = blockIdx.y * BLOCK_SZ + threadIdx.y;
    int colIdx = blockIdx.x * BLOCK_SZ + threadIdx.x;

    float partialSum = 0.0f;
    int tileCount = (m + BLOCK_SZ - 1) / BLOCK_SZ;

    for (int tile = 0; tile < tileCount; ++tile)
    {
        int aRow = rowIdx;
        int aCol = tile * BLOCK_SZ + threadIdx.x;
        tileA[threadIdx.y][threadIdx.x] = (aRow < n && aCol < m) ? A[aRow * m + aCol] : 0.0f;

        int bRow = tile * BLOCK_SZ + threadIdx.y;
        int bCol = colIdx;
        tileB[threadIdx.y][threadIdx.x] = (bRow < m && bCol < n) ? B[bRow * n + bCol] : 0.0f;

        __syncthreads();

#pragma unroll
        for (int k = 0; k < BLOCK_SZ; ++k) {
            partialSum += tileA[threadIdx.y][k] * tileB[k][threadIdx.x];
        }

        __syncthreads();
    }

    if (rowIdx < n && colIdx < n) {
        C[rowIdx * n + colIdx] = partialSum;
    }
}

int main()
{
    int dimN, dimM;
    std::cout << "Enter matrix dimensions (n m): ";
    std::cin >> dimN >> dimM;

    const size_t countA = static_cast<size_t>(dimN) * dimM;
    const size_t countB = static_cast<size_t>(dimM) * dimN;
    const size_t countC = static_cast<size_t>(dimN) * dimN;

    std::cout << "Matrix A size: " << countA << " elements\n";
    std::cout << "Matrix B size: " << countB << " elements\n";

    std::vector<float> h_A(countA), h_B(countB);
    std::vector<float> h_C_cpu(countC), h_C_gpu(countC);

    std::mt19937 rng(777);
    std::uniform_real_distribution<float> uniform(-5.0f, 5.0f);
    for (auto& val : h_A) val = uniform(rng);
    for (auto& val : h_B) val = uniform(rng);

    auto cpuStart = std::chrono::high_resolution_clock::now();
    multiplyOnCPU(h_A.data(), h_B.data(), h_C_cpu.data(), dimN, dimM);
    auto cpuEnd = std::chrono::high_resolution_clock::now();
    double cpuElapsed = std::chrono::duration<double, std::milli>(cpuEnd - cpuStart).count();

    float* d_A = nullptr, * d_B = nullptr, * d_C = nullptr;
    CUDA_CHECK(cudaMalloc(&d_A, countA * sizeof(float)));
    CUDA_CHECK(cudaMalloc(&d_B, countB * sizeof(float)));
    CUDA_CHECK(cudaMalloc(&d_C, countC * sizeof(float)));

    cudaEvent_t evtStart, evtStop;
    cudaEventCreate(&evtStart);
    cudaEventCreate(&evtStop);

    cudaEventRecord(evtStart);

    CUDA_CHECK(cudaMemcpy(d_A, h_A.data(), countA * sizeof(float), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemcpy(d_B, h_B.data(), countB * sizeof(float), cudaMemcpyHostToDevice));

    dim3 threadsPerBlock(BLOCK_SZ, BLOCK_SZ);
    dim3 blocksPerGrid((dimN + BLOCK_SZ - 1) / BLOCK_SZ,
        (dimN + BLOCK_SZ - 1) / BLOCK_SZ);

    multiplyOnGPU << <blocksPerGrid, threadsPerBlock >> > (d_A, d_B, d_C, dimN, dimM);
    CUDA_CHECK(cudaDeviceSynchronize());

    CUDA_CHECK(cudaMemcpy(h_C_gpu.data(), d_C, countC * sizeof(float), cudaMemcpyDeviceToHost));

    cudaEventRecord(evtStop);
    cudaEventSynchronize(evtStop);

    float gpuElapsed = 0.0f;
    cudaEventElapsedTime(&gpuElapsed, evtStart, evtStop);

    bool isCorrect = verifyResults(h_C_cpu, h_C_gpu);

    std::cout << "\n=== Report ===\n";
    std::cout << "CPU execution time: " << cpuElapsed << " ms\n";
    std::cout << "GPU time: " << gpuElapsed << " ms\n";
    std::cout << "VALID: " << (isCorrect ? "TRUE" : "FALSE") << "\n";

    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    cudaEventDestroy(evtStart);
    cudaEventDestroy(evtStop);

    return 0;
}
