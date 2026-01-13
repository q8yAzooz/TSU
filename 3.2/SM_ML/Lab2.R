# Лабораторная работа №2
# Интервальные оценки параметров нормального распределения

# Параметры распределения
a <- 5    # Среднее
sigma <- 2 # Стандартное отклонение

# 1. Генерация выборок
n_values <- c(100, 500, 1000)
samples <- list(
  N100 = rnorm(100, mean = a, sd = sigma),
  N500 = rnorm(500, mean = a, sd = sigma),
  N1000 = rnorm(1000, mean = a, sd = sigma)
)

# 2. Построение графиков
par(mfrow = c(3, 2)) # Разделение окна на 3 строки и 2 столбца

for (name in names(samples)) {
  # Гистограмма с плотностью
  hist(samples[[name]], main = paste("Гистограмма для", name), 
       xlab = "Значения", col = "lightblue", probability = TRUE)
  curve(dnorm(x, mean = a, sd = sigma), add = TRUE, col = "red", lwd = 2)
  
  # Q-Q plot
  qqnorm(samples[[name]], main = paste("Q-Q plot для", name))
  qqline(samples[[name]], col = "red")
}

# 3. Вычисление характеристик
results <- data.frame(
  N = n_values,
  Sample_Mean = sapply(samples, mean),
  Sample_Var = sapply(samples, var),
  Sample_SD = sapply(samples, sd)
)
print(results)

# 4. Доверительные интервалы (известная дисперсия)
alpha <- 0.05
z <- qnorm(1 - alpha/2)

ci_known_var <- t(sapply(samples, function(x) {
  mean_x <- mean(x)
  margin <- z * sigma / sqrt(length(x))
  c(mean_x - margin, mean_x + margin)
}))
colnames(ci_known_var) <- c("Lower_Known", "Upper_Known")

# 5. Доверительные интервалы (неизвестная дисперсия)
ci_unknown_var <- t(sapply(samples, function(x) {
  t_test <- t.test(x, conf.level = 1 - alpha)
  c(t_test$conf.int[1], t_test$conf.int[2])
}))
colnames(ci_unknown_var) <- c("Lower_Unknown", "Upper_Unknown")

# Объединение результатов
results <- cbind(results, ci_known_var, ci_unknown_var)
print(results)

# 6. График зависимости оценок от объема выборки
library(ggplot2)
library(tidyr)

plot_data <- results %>% 
  pivot_longer(cols = -N, names_to = "Metric", values_to = "Value")

ggplot(plot_data, aes(x = N, y = Value, color = Metric)) +
  geom_line() +
  geom_point() +
  labs(title = "Зависимость оценок от объема выборки",
       x = "Объем выборки", y = "Значение") +
  theme_minimal()
