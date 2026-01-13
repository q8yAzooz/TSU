#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <ctime>
#include <windows.h>
#include <chrono>
#include <iomanip>
#include <queue>
#include <functional>

using namespace std;
using namespace std::chrono;

struct Item {
    int weight;
    int cost;
};

// Компаратор для жадного алгоритма
bool cmpGreedy(const Item& a, const Item& b) {
    return (double)a.cost / a.weight > (double)b.cost / b.weight;
}

// ==================== ЖАДНЫЙ АЛГОРИТМ ====================
pair<int, int> greedyKnapsack(const vector<Item>& items, int W, long long& duration) {
    auto start = high_resolution_clock::now();
    
    vector<Item> sorted = items;
    sort(sorted.begin(), sorted.end(), cmpGreedy);

    int totalCost = 0;
    int totalWeight = 0;
    for (const auto& it : sorted) {
        if (totalWeight + it.weight <= W) {
            totalWeight += it.weight;
            totalCost += it.cost;
        }
    }
    
    auto end = high_resolution_clock::now();
    duration = duration_cast<microseconds>(end - start).count();
    
    return make_pair(totalCost, totalWeight);
}

// ==================== ДИНАМИЧЕСКОЕ ПРОГРАММИРОВАНИЕ ====================
pair<int, int> dpKnapsack(const vector<Item>& items, int W, long long& duration) {
    auto start = high_resolution_clock::now();
    
    int n = items.size();
    vector<vector<int>> dp(n + 1, vector<int>(W + 1, 0));

    for (int i = 1; i <= n; ++i) {
        for (int w = 0; w <= W; ++w) {
            dp[i][w] = dp[i - 1][w];
            if (items[i - 1].weight <= w) {
                int take = dp[i - 1][w - items[i - 1].weight] + items[i - 1].cost;
                if (take > dp[i][w])
                    dp[i][w] = take;
            }
        }
    }

    int totalWeight = 0;
    int curW = W;
    for (int i = n; i > 0; --i) {
        if (dp[i][curW] != dp[i - 1][curW]) {
            totalWeight += items[i - 1].weight;
            curW -= items[i - 1].weight;
        }
    }
    
    auto end = high_resolution_clock::now();
    duration = duration_cast<microseconds>(end - start).count();
    
    return make_pair(dp[n][W], totalWeight);
}

// ==================== БЭКТРЕКИНГ ====================
int bestCostBT = 0;
int bestWeightBT = 0;

void backtrack(int idx, int curWeight, int curCost,
    const vector<Item>& items, int W) {
    if (idx == (int)items.size()) {
        if (curCost > bestCostBT) {
            bestCostBT = curCost;
            bestWeightBT = curWeight;
        }
        return;
    }

    // Берём, если влезает
    if (curWeight + items[idx].weight <= W) {
        backtrack(idx + 1,
            curWeight + items[idx].weight,
            curCost + items[idx].cost,
            items, W);
    }

    // Не берём текущий груз
    backtrack(idx + 1, curWeight, curCost, items, W);
}

pair<int, int> backtrackKnapsack(const vector<Item>& items, int W, long long& duration) {
    auto start = high_resolution_clock::now();
    
    bestCostBT = 0;
    bestWeightBT = 0;
    backtrack(0, 0, 0, items, W);
    
    auto end = high_resolution_clock::now();
    duration = duration_cast<microseconds>(end - start).count();
    
    return make_pair(bestCostBT, bestWeightBT);
}

// ==================== BRANCH AND BOUND ====================
// Структура узла для Branch and Bound
struct Node {
    int level;          
    int weight;         
    int cost;          
    float bound;        
    
    // Компаратор для priority_queue (максимальная граница наверху)
    bool operator<(const Node& other) const {
        return bound < other.bound;
    }
};

// Функция для вычисления верхней границы (оптимистичной оценки)
float calculateBound(Node u, int n, int W, const vector<Item>& items) {
    // Если вес превысил вместимость - потенциал 0
    if (u.weight >= W) return 0;
    
    float bound = u.cost;  // начинаем с текущей стоимости
    int j = u.level + 1;   // следующий предмет
    int totalWeight = u.weight;
    
    // Жадное добавление предметов, пока они целиком помещаются
    while (j < n && totalWeight + items[j].weight <= W) {
        totalWeight += items[j].weight;
        bound += items[j].cost;
        j++;
    }
    
    // Если остались предметы, добавляем часть следующего (дробный рюкзак)
    if (j < n) {
        bound += (W - totalWeight) * ((float)items[j].cost / items[j].weight);
    }
    
    return bound;
}

// Основная функция Branch and Bound
pair<int, int> branchAndBoundKnapsack(const vector<Item>& items, int W, long long& duration) {
    auto start = high_resolution_clock::now();
    
    int n = items.size();
    
    // Шаг 1: Сортируем предметы по удельному весу (стоимость/вес)
    vector<Item> sortedItems = items;
    sort(sortedItems.begin(), sortedItems.end(), cmpGreedy);
    
    // Шаг 2: Инициализация
    priority_queue<Node> pq;
    
    Node u, v;
    u.level = -1;        // начинаем с корня (ничего не взяли)
    u.weight = 0;
    u.cost = 0;
    u.bound = calculateBound(u, n, W, sortedItems);
    
    pq.push(u);  // добавляем корневой узел в очередь
    
    int maxCost = 0;
    int bestWeight = 0;
    
    // Шаг 3: Основной цикл
    while (!pq.empty()) {
        // Берём узел с наибольшей верхней границей
        u = pq.top();
        pq.pop();
        
        // Если эта ветка не может улучшить результат - пропускаем
        if (u.bound <= maxCost) {
            continue;
        }
        
        // Если это лист дерева (рассмотрели все предметы)
        if (u.level == n - 1) {
            continue;
        }
        
        // Шаг 4: Рассматриваем следующий предмет
        v.level = u.level + 1;
        
        // Вариант 1: Берём предмет v.level
        v.weight = u.weight + sortedItems[v.level].weight;
        v.cost = u.cost + sortedItems[v.level].cost;
        
        if (v.weight <= W && v.cost > maxCost) {
            maxCost = v.cost;
            bestWeight = v.weight;
        }
        
        v.bound = calculateBound(v, n, W, sortedItems);
        if (v.bound > maxCost) {
            pq.push(v);  // эта ветка перспективна
        }
        
        // Вариант 2: Не берём предмет v.level
        v.weight = u.weight;
        v.cost = u.cost;
        v.bound = calculateBound(v, n, W, sortedItems);
        
        if (v.bound > maxCost) {
            pq.push(v);  // эта ветка тоже перспективна
        }
    }
    
    auto end = high_resolution_clock::now();
    duration = duration_cast<microseconds>(end - start).count();
    
    return make_pair(maxCost, bestWeight);
}

// ==================== MAIN ====================
int main() {
    SetConsoleOutputCP(CP_UTF8);
    srand((unsigned int)time(NULL));

    const int n = 10000;
    vector<Item> items(n);
    int sumWeight = 0;

    // cout << "Грузы (вес, стоимость):\n";
    for (int i = 0; i < n; ++i) {
        items[i].weight = rand() % 2 + 1;   // вес от 1 до 2
        items[i].cost = rand() % 200 + 1;     // стоимость от 1 до 200
        sumWeight += items[i].weight;

    //     cout << "(" << items[i].weight << "," << items[i].cost << ") ";
    //     if ((i + 1) % 10 == 0) cout << "\n";
    }
    // cout << "\n\n";

    int W = sumWeight / 2;
    cout << "Вместимость рюкзака W = " << W << "\n";
    cout << "Общий вес всех предметов = " << sumWeight << "\n\n";

    long long timeGreedy, timeDP, timeBacktrack, timeBB;
    
    // Запускаем все алгоритмы
    pair<int, int> greedyRes = greedyKnapsack(items, W, timeGreedy);
    pair<int, int> dpRes = dpKnapsack(items, W, timeDP);
    // pair<int, int> btRes = backtrackKnapsack(items, W, timeBacktrack);
    pair<int, int> bbRes = branchAndBoundKnapsack(items, W, timeBB);

    // Вывод результатов
    cout << "═══════════════════════════════════════════════════════════════════════════════════════\n";
    cout << "                                  РЕЗУЛЬТАТЫ                                          \n";
    cout << "═══════════════════════════════════════════════════════════════════════════════════════\n";
    printf("Жадный алгоритм:               стоимость = %4d, вес = %4d, время = %7lld мкс\n", 
           greedyRes.first, greedyRes.second, timeGreedy);
    printf("Динамическое программирование: стоимость = %4d, вес = %4d, время = %7lld мкс\n", 
           dpRes.first, dpRes.second, timeDP);
    // printf("Бэктрекинг (полный перебор):   стоимость = %4d, вес = %4d, время = %7lld мкс\n", 
    //        btRes.first, btRes.second, timeBacktrack);
    printf("Branch and Bound:              стоимость = %4d, вес = %4d, время = %7lld мкс\n", 
           bbRes.first, bbRes.second, timeBB);
    cout << "═══════════════════════════════════════════════════════════════════════════════════════\n\n";

    return 0;
}