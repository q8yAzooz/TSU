# Установка зерна для воспроизводимости результатов
set.seed(42)

# Задание 1: Дискретные распределения
cat("Задание 1: Дискретные распределения\n\n")
# Параметры
N <- 150     # Размер выборки
n <- 10      # Количество испытаний (для биномиального)
p <- 0.3     # Вероятность успеха

# 1. Генерация выборок
binomial_sample <- rbinom(N, n, p)
geometric_sample <- rgeom(N, p)

# 2. Построение полигона частот и эмпирической функции распределения
par(mfrow = c(2, 2))

# Полигон частот для биномиального распределения
bin_freq <- table(factor(binomial_sample, levels = 0:n))
plot(bin_freq, type = "l", col = "blue", xlab = "Значения", ylab = "Частота", 
     main = "Полигон частот (Биномиальное)")

# Эмпирическая функция распределения для биномиального
plot(ecdf(binomial_sample), col = "blue", main = "Эмпирическая функция распределения (Биномиальное)")

# Полигон частот для геометрического распределения
geom_freq <- table(geometric_sample)
plot(geom_freq, type = "l", col = "red", xlab = "Значения", ylab = "Частота", 
     main = "Полигон частот (Геометрическое)")

# Эмпирическая функция распределения для геометрического
plot(ecdf(geometric_sample), col = "red", main = "Эмпирическая функция распределения (Геометрическое)")

# 3. Оценки числовых характеристик (для обоих распределений)
# Для биномиального
bin_mean <- mean(binomial_sample)
bin_var <- var(binomial_sample)
bin_std <- sd(binomial_sample)
bin_mode <- as.numeric(names(sort(table(binomial_sample), decreasing = TRUE)[1]))
bin_median <- median(binomial_sample)
bin_skewness <- sum((binomial_sample - bin_mean)^3) / (N * bin_std^3)
bin_kurtosis <- (sum((binomial_sample - bin_mean)^4) / (N * bin_std^4)) - 3

# Для геометрического
geom_mean <- mean(geometric_sample)
geom_var <- var(geometric_sample)
geom_std <- sd(geometric_sample)
geom_mode <- as.numeric(names(sort(table(geometric_sample), decreasing = TRUE)[1]))
geom_median <- median(geometric_sample)
geom_skewness <- sum((geometric_sample - geom_mean)^3) / (N * geom_std^3)
geom_kurtosis <- (sum((geometric_sample - geom_mean)^4) / (N * geom_std^4)) - 3

# Вывод характеристик для биномиального распределения
cat("Биномиальное распределение:\n")
cat("  Выборочное среднее =", bin_mean, "\n")
cat("  Выборочная дисперсия =", bin_var, "\n")
cat("  Выборочное СКО =", bin_std, "\n")
cat("  Мода =", bin_mode, "\n")
cat("  Медиана =", bin_median, "\n")
cat("  Коэффициент асимметрии =", bin_skewness, "\n")
cat("  Коэффициент эксцесса =", bin_kurtosis, "\n\n")

# Вывод характеристик для геометрического распределения
cat("Геометрическое распределение:\n")
cat("  Выборочное среднее =", geom_mean, "\n")
cat("  Выборочная дисперсия =", geom_var, "\n")
cat("  Выборочное СКО =", geom_std, "\n")
cat("  Мода =", geom_mode, "\n")
cat("  Медиана =", geom_median, "\n")
cat("  Коэффициент асимметрии =", geom_skewness, "\n")
cat("  Коэффициент эксцесса =", geom_kurtosis, "\n\n")

# 4. Теоретические математическое ожидание и дисперсия
bin_theo_mean <- n * p
bin_theo_var <- n * p * (1 - p)

geom_theo_mean <- (1 - p) / p
geom_theo_var <- (1 - p) / p^2

# Сравнение
cat("Сравнение с теоретическими значениями:\n")
cat("Биномиальное:\n")
cat("  Выборочное среднее =", bin_mean, ", Теоретическое =", bin_theo_mean, "\n")
cat("  Выборочная дисперсия =", bin_var, ", Теоретическая =", bin_theo_var, "\n")
cat("Геометрическое:\n")
cat("  Выборочное среднее =", geom_mean, ", Теоретическое =", geom_theo_mean, "\n")
cat("  Выборочная дисперсия =", geom_var, ", Теоретическая =", geom_theo_var, "\n\n")

# 5. Оценка параметров
p_est_bin <- bin_mean / n
p_est_geom <- 1 / (geom_mean + 1)

cat("Оценка параметра p:\n")
cat("  Для биномиального:", p_est_bin, "\n")
cat("  Для геометрического:", p_est_geom, "\n\n")

# 6. Критерий хи-квадрат
# Для биномиального (полный диапазон 0:n)
bin_range <- 0:n
bin_probs <- dbinom(bin_range, n, p)
chisq_bin <- chisq.test(table(factor(binomial_sample, levels = bin_range)), p = bin_probs)
cat("Хи-квадрат тест для биномиального распределения:\n")
print(chisq_bin)

# Для геометрического (диапазон до максимума в выборке)
geom_range <- 0:max(geometric_sample)
geom_probs <- dgeom(geom_range, p)
geom_probs <- geom_probs / sum(geom_probs)  # Нормализация
chisq_geom <- chisq.test(table(factor(geometric_sample, levels = geom_range)), p = geom_probs)
cat("\nХи-квадрат тест для геометрического распределения:\n")
print(chisq_geom)

# Задание 2: Непрерывные распределения
cat("\n\nЗадание 2: Непрерывные распределения\n\n")
# Параметры
lambda <- 0.5  # Параметр экспоненциального распределения
alpha <- 2     # Параметр формы гамма-распределения
beta <- 1      # Параметр скорости гамма-распределения

# 1. Генерация выборок
exponential_sample <- rexp(N, rate = lambda)
gamma_sample <- rgamma(N, shape = alpha, rate = beta)

# 2. Построение гистограммы и плотности
par(mfrow = c(2, 2))

# Экспоненциальное распределение
hist(exponential_sample, breaks = 30, probability = TRUE, 
     col = "lightblue", main = "Гистограмма (Экспоненциальное)")
curve(dexp(x, rate = lambda), add = TRUE, col = "red", lwd = 2)

plot(density(exponential_sample), col = "blue", 
     main = "Оценка плотности (Экспоненциальное)")
curve(dexp(x, rate = lambda), add = TRUE, col = "red", lwd = 2)

# Гамма-распределение
hist(gamma_sample, breaks = 30, probability = TRUE, 
     col = "lightgreen", main = "Гистограмма (Гамма)")
curve(dgamma(x, shape = alpha, rate = beta), add = TRUE, col = "red", lwd = 2)

plot(density(gamma_sample), col = "green", main = "Оценка плотности (Гамма)")
curve(dgamma(x, shape = alpha, rate = beta), add = TRUE, col = "red", lwd = 2)

# 3. Оценки числовых характеристик
# Для экспоненциального
exp_mean <- mean(exponential_sample)
exp_var <- var(exponential_sample)
exp_std <- sd(exponential_sample)
exp_mode <- density(exponential_sample)$x[which.max(density(exponential_sample)$y)]
exp_median <- median(exponential_sample)
exp_skewness <- sum((exponential_sample - exp_mean)^3) / (N * exp_std^3)
exp_kurtosis <- (sum((exponential_sample - exp_mean)^4) / (N * exp_std^4)) - 3

# Для гамма-распределения
gamma_mean <- mean(gamma_sample)
gamma_var <- var(gamma_sample)
gamma_std <- sd(gamma_sample)
gamma_mode <- density(gamma_sample)$x[which.max(density(gamma_sample)$y)]
gamma_median <- median(gamma_sample)
gamma_skewness <- sum((gamma_sample - gamma_mean)^3) / (N * gamma_std^3)
gamma_kurtosis <- (sum((gamma_sample - gamma_mean)^4) / (N * gamma_std^4)) - 3

# Вывод характеристик
cat("Экспоненциальное распределение:\n")
cat("  Выборочное среднее =", exp_mean, "\n")
cat("  Выборочная дисперсия =", exp_var, "\n")
cat("  Мода =", exp_mode, "\n")
cat("  Медиана =", exp_median, "\n")
cat("  Коэффициент асимметрии =", exp_skewness, "\n")
cat("  Коэффициент эксцесса =", exp_kurtosis, "\n\n")

cat("Гамма-распределение:\n")
cat("  Выборочное среднее =", gamma_mean, "\n")
cat("  Выборочная дисперсия =", gamma_var, "\n")
cat("  Мода =", gamma_mode, "\n")
cat("  Медиана =", gamma_median, "\n")
cat("  Коэффициент асимметрии =", gamma_skewness, "\n")
cat("  Коэффициент эксцесса =", gamma_kurtosis, "\n\n")

# 4. Теоретические значения
exp_theo_mean <- 1 / lambda
exp_theo_var <- 1 / lambda^2

gamma_theo_mean <- alpha / beta
gamma_theo_var <- alpha / beta^2

# Сравнение
cat("Сравнение с теоретическими значениями:\n")
cat("Экспоненциальное:\n")
cat("  Выборочное среднее =", exp_mean, ", Теоретическое =", exp_theo_mean, "\n")
cat("  Выборочная дисперсия =", exp_var, ", Теоретическая =", exp_theo_var, "\n")
cat("Гамма-распределение:\n")
cat("  Выборочное среднее =", gamma_mean, ", Теоретическое =", gamma_theo_mean, "\n")
cat("  Выборочная дисперсия =", gamma_var, ", Теоретическая =", gamma_theo_var, "\n\n")

# 5. Оценка параметров
lambda_est <- 1 / exp_mean
alpha_est <- gamma_mean^2 / gamma_var
beta_est <- gamma_mean / gamma_var

cat("Оценка параметров:\n")
cat("  Экспоненциальное (lambda):", lambda_est, "\n")
cat("  Гамма (alpha):", alpha_est, "\n")
cat("  Гамма (beta):", beta_est, "\n\n")

# 6. Проверка распределений
# Тест Колмогорова-Смирнова (более подходит для непрерывных)
cat("Тест Колмогорова-Смирнова:\n")
cat("Экспоненциальное:\n")
print(ks.test(exponential_sample, "pexp", lambda))

cat("\nГамма-распределение:\n")
print(ks.test(gamma_sample, "pgamma", shape = alpha, rate = beta))

# Хи-квадрат тест с группировкой
cat("\nХи-квадрат тест с группировкой:\n")

# Функция для хи-квадрат теста с автоматической группировкой
chi_square_test <- function(sample, dist_func, ...) {
  # Автоматическое определение интервалов
  breaks <- hist(sample, plot = FALSE)$breaks
  observed <- hist(sample, breaks = breaks, plot = FALSE)$counts
  
  # Теоретические вероятности
  probs <- diff(dist_func(breaks, ...))
  probs <- probs / sum(probs)  # Нормализация
  
  # Проверка
  chisq.test(observed, p = probs)
}

cat("Экспоненциальное:\n")
print(chi_square_test(exponential_sample, pexp, rate = lambda))

cat("\nГамма-распределение:\n")
print(chi_square_test(gamma_sample, pgamma, shape = alpha, rate = beta))

# Сброс графических параметров
par(mfrow = c(1, 1))