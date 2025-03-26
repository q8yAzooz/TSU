# Задание 1: Дискретные распределения
cat("Задание 1: Дискретные распределения\n\n")
# Параметры
N <- 150
n <- 10
p <- 0.3

# 1. Генерация выборок
binomial_sample <- rbinom(N, n, p)
geometric_sample <- rgeom(N, p)

# 2. Построение полигона частот и эмпирической функции распределения
par(mfrow=c(2,2))

# Полигон частот для биномиального распределения
bin_freq <- table(binomial_sample)
plot(bin_freq, type="l", col="blue", xlab="Значения", ylab="Частота", main="Полигон частот (Биномиальное)")

# Эмпирическая функция распределения для биномиального распределения
plot(ecdf(binomial_sample), col="blue", main="Эмпирическая функция распределения (Биномиальное)")

# Полигон частот для геометрического распределения
geom_freq <- table(geometric_sample)
plot(geom_freq, type="l", col="red", xlab="Значения", ylab="Частота", main="Полигон частот (Геометрическое)")

# Эмпирическая функция распределения для геометрического распределения
plot(ecdf(geometric_sample), col="red", main="Эмпирическая функция распределения (Геометрическое)")

# 3. Оценки числовых характеристик
bin_mean <- mean(binomial_sample)
bin_var <- var(binomial_sample)
bin_std <- sd(binomial_sample)
bin_mode <- as.numeric(names(sort(table(binomial_sample), decreasing=TRUE)[1]))
bin_median <- median(binomial_sample)
bin_skewness <- sum((binomial_sample - bin_mean)^3) / (length(binomial_sample) * bin_std^3)
bin_kurtosis <- (sum((binomial_sample - bin_mean)^4) / (length(binomial_sample) * bin_std^4)) - 3

cat("Выборочное среднее = ", bin_mean <- mean(binomial_sample), "\n")  # Выборочное среднее
cat("Выборочная дисперсия = ", bin_var <- var(binomial_sample), "\n")  # Выборочная дисперсия
cat("Выборочное стандартное отклонение (СКО) = ", bin_std <- sd(binomial_sample), "\n")  # Выборочное стандартное отклонение (СКО)
cat("Мода = ", bin_mode <- as.numeric(names(sort(table(binomial_sample), decreasing=TRUE)[1])), "\n")  # Мода
cat("Медиана = ", bin_median <- median(binomial_sample), "\n")  # Медиана
cat("Коэффициент асимметрии = ", bin_skewness <- sum((binomial_sample - bin_mean)^3) / (length(binomial_sample) * bin_std^3), "\n")  # Коэффициент асимметрии
cat("Коэффициент эксцесса = ", bin_kurtosis <- (sum((binomial_sample - bin_mean)^4) / (length(binomial_sample) * bin_std^4)) - 3, "\n")  # Коэффициент эксцесса

# 4. Теоретические математическое ожидание и дисперсия
bin_theo_mean <- n * p
bin_theo_var <- n * p * (1 - p)

geom_theo_mean <- (1 - p) / p
geom_theo_var <- (1 - p) / p^2

# Сравнение
cat("Биномиальное: Выборочное среднее =", bin_mean, ", Теоретическое среднее =", bin_theo_mean, "\n")
cat("Биномиальное: Выборочная дисперсия =", bin_var, ", Теоретическая дисперсия =", bin_theo_var, "\n")
cat("Геометрическое: Выборочное среднее =", geom_mean, ", Теоретическое среднее =", geom_theo_mean, "\n")
cat("Геометрическое: Выборочная дисперсия =", geom_var, ", Теоретическая дисперсия =", geom_theo_var, "\n")

# 5. Оценка параметров
p_est_bin <- bin_mean / n
p_est_geom <- 1 / (geom_mean + 1)

cat("Оценка p для биномиального распределения:", p_est_bin, "\n")
cat("Оценка p для геометрического распределения:", p_est_geom, "\n")

# Критерий хи-квадрат для биномиального распределения
bin_range <- min(binomial_sample):max(binomial_sample)
bin_probs <- dbinom(bin_range, n, p)  # Используем dbinom для биномиального распределения
bin_probs <- bin_probs / sum(bin_probs)  # Нормализация вероятностей
chisq.test(table(factor(binomial_sample, levels = bin_range)), p = bin_probs)


# Критерий хи-квадрат для геометрического распределения
geom_range <- min(geometric_sample):max(geometric_sample)
geom_probs <- dgeom(geom_range, p)  # Используем dgeom для геометрического распределения
geom_probs <- geom_probs / sum(geom_probs)  # Нормализация вероятностей
chisq.test(table(factor(geometric_sample, levels = geom_range)), p = geom_probs)

# Задание 2: Непрерывные распределения
cat("\nЗадание 2: Непрерывные распределения\n\n")
# Параметры
N <- 150
lambda <- 0.5
alpha <- 2
beta <- 1

# 1. Генерация выборок
exponential_sample <- rexp(N, rate = lambda)
gamma_sample <- rgamma(N, shape = alpha, rate = beta)

# 2. Построение гистограммы и плотности
par(mfrow=c(2,2))

# Гистограмма и плотность для экспоненциального распределения
hist(exponential_sample, breaks=30, probability=TRUE, col="lightblue", main="Гистограмма (Экспоненциальное)")
curve(dexp(x, rate = lambda), add=TRUE, col="red", lwd=2)

# Оценка плотности для экспоненциального распределения
plot(density(exponential_sample), col="blue", main="Оценка плотности (Экспоненциальное)")
curve(dexp(x, rate = lambda), add=TRUE, col="red", lwd=2)

# Гистограмма и плотность для гамма-распределения
hist(gamma_sample, breaks=30, probability=TRUE, col="lightgreen", main="Гистограмма (Гамма)")
curve(dgamma(x, shape = alpha, rate = beta), add=TRUE, col="red", lwd=2)

# Оценка плотности для гамма-распределения
plot(density(gamma_sample), col="green", main="Оценка плотности (Гамма)")
curve(dgamma(x, shape = alpha, rate = beta), add=TRUE, col="red", lwd=2)

# 3. Оценки числовых характеристик
exp_mean <- mean(exponential_sample)
exp_var <- var(exponential_sample)
exp_std <- sd(exponential_sample)
exp_mode <- density(exponential_sample)$x[which.max(density(exponential_sample)$y)]
exp_median <- median(exponential_sample)
exp_skewness <- sum((exponential_sample - exp_mean)^3) / (N * exp_std^3)
exp_kurtosis <- (sum((exponential_sample - exp_mean)^4) / (N * exp_std^4)) - 3

gamma_mean <- mean(gamma_sample)
gamma_var <- var(gamma_sample)
gamma_std <- sd(gamma_sample)
gamma_mode <- density(gamma_sample)$x[which.max(density(gamma_sample)$y)]
gamma_median <- median(gamma_sample)
gamma_skewness <- sum((gamma_sample - gamma_mean)^3) / (N * gamma_std^3)
gamma_kurtosis <- (sum((gamma_sample - gamma_mean)^4) / (N * gamma_std^4)) - 3

# 4. Теоретические математическое ожидание и дисперсия
exp_theo_mean <- 1 / lambda
exp_theo_var <- 1 / lambda^2

gamma_theo_mean <- alpha / beta
gamma_theo_var <- alpha / beta^2

# Сравнение
cat("Экспоненциальное: Выборочное среднее =", exp_mean, ", Теоретическое среднее =", exp_theo_mean, "\n")
cat("Экспоненциальное: Выборочная дисперсия =", exp_var, ", Теоретическая дисперсия =", exp_theo_var, "\n")
cat("Гамма: Выборочное среднее =", gamma_mean, ", Теоретическое среднее =", gamma_theo_mean, "\n")
cat("Гамма: Выборочная дисперсия =", gamma_var, ", Теоретическая дисперсия =", gamma_theo_var, "\n")

# 5. Оценка параметров
lambda_est <- 1 / exp_mean
alpha_est <- gamma_mean^2 / gamma_var
beta_est <- gamma_mean / gamma_var

cat("Оценка lambda для экспоненциального распределения:", lambda_est, "\n")
cat("Оценка alpha и beta для гамма-распределения:", alpha_est, beta_est, "\n")

# Критерий хи-квадрат
# Экспоненциальное
# Используем квантили для разбиения на интервалы
breaks <- quantile(exponential_sample, probs = seq(0, 1, length.out = 11))

# Разбиваем данные на интервалы
cut_sample <- cut(exponential_sample, breaks = breaks, include.lowest = TRUE)

# Рассчитываем теоретические вероятности для каждого интервала
theoretical_probs <- diff(pexp(breaks, rate = lambda))

# Нормализация вероятностей (если необходимо)
theoretical_probs <- theoretical_probs / sum(theoretical_probs)

# Критерий хи-квадрат
chisq.test(table(cut_sample), p = theoretical_probs)

# Гамма
# Используем квантили для разбиения на интервалы
breaks <- quantile(gamma_sample, probs = seq(0, 1, length.out = 11))

# Разбиваем данные на интервалы
cut_sample <- cut(gamma_sample, breaks = breaks, include.lowest = TRUE)

# Рассчитываем теоретические вероятности для каждого интервала
theoretical_probs <- diff(pgamma(breaks, shape = alpha, rate = beta))

# Нормализация вероятностей
theoretical_probs <- theoretical_probs / sum(theoretical_probs)

# Критерий хи-квадрат
chisq.test(table(cut_sample), p = theoretical_probs)
