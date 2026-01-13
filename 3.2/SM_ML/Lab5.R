# 1. Генерация выборки X1
set.seed(123)
a1 <- 5    # Среднее
S1 <- 2    # Стандартное отклонение
N <- 200
X1 <- rnorm(N, mean = a1, sd = S1)

# 2. Задание коэффициентов корреляции
r1 <- 0.15  # ∈ [0.1; 0.2]
r2 <- 0.75  # ∈ [0.6; 0.9]

# 3. Построение выборок X2 и X3
a2 <- 0     # Среднее для шума
S2 <- 1     # Стандартное отклонение для шума

# X2 = r1*X1 + sqrt(1 - r1^2)*шум
noise_X2 <- rnorm(N, mean = a2, sd = S2)
X2 <- r1 * X1 + sqrt(1 - r1^2) * noise_X2

# X3 = r2*X1 + sqrt(1 - r2^2)*шум
noise_X3 <- rnorm(N, mean = a2, sd = S2)
X3 <- r2 * X1 + sqrt(1 - r2^2) * noise_X3

# 4. Диаграммы рассеяния
par(mfrow = c(1, 2))
plot(X1, X2, main = "X1 vs X2 (r = 0.15)", col = "blue", pch = 19)
plot(X1, X3, main = "X1 vs X3 (r = 0.75)", col = "red", pch = 19)
par(mfrow = c(1, 1))

# 5. Выборочные коэффициенты корреляции
cor_X1X2 <- cor(X1, X2)
cor_X1X3 <- cor(X1, X3)
cat("Выборочный r1:", round(cor_X1X2, 3), "\n")
cat("Выборочный r2:", round(cor_X1X3, 3), "\n")

# 6. Проверка гипотезы о корреляции
t_test_X1X2 <- cor.test(X1, X2)
t_test_X1X3 <- cor.test(X1, X3)

cat("\nТест для X1 и X2:\n")
cat("t-статистика:", round(t_test_X1X2$statistic, 3), "\n")
cat("p-value:", t_test_X1X2$p.value, "\n")

cat("\nТест для X1 и X3:\n")
cat("t-статистика:", round(t_test_X1X3$statistic, 3), "\n")
cat("p-value:", t_test_X1X3$p.value, "\n")

# 7. Доверительный интервал с Z-преобразованием Фишера
fisher_transform <- function(r) 0.5 * log((1 + r)/(1 - r))

# Для X1 и X2
z_r1 <- fisher_transform(cor_X1X2)
se_z1 <- 1 / sqrt(N - 3)
ci_z1_low <- z_r1 - qnorm(0.975) * se_z1
ci_z1_high <- z_r1 + qnorm(0.975) * se_z1

# Обратное преобразование
ci_r1_low <- (exp(2 * ci_z1_low) - 1) / (exp(2 * ci_z1_low) + 1)
ci_r1_high <- (exp(2 * ci_z1_high) - 1) / (exp(2 * ci_z1_high) + 1)

# Для X1 и X3
z_r2 <- fisher_transform(cor_X1X3)
se_z2 <- 1 / sqrt(N - 3)
ci_z2_low <- z_r2 - qnorm(0.975) * se_z2
ci_z2_high <- z_r2 + qnorm(0.975) * se_z2

ci_r2_low <- (exp(2 * ci_z2_low) - 1) / (exp(2 * ci_z2_low) + 1)
ci_r2_high <- (exp(2 * ci_z2_high) - 1) / (exp(2 * ci_z2_high) + 1)

cat("\nДоверительный интервал для r1: [", 
    round(ci_r1_low, 3), ";", round(ci_r1_high, 3), "]\n")
cat("Доверительный интервал для r2: [", 
    round(ci_r2_low, 3), ";", round(ci_r2_high, 3), "]\n")