# Лабораторная работа №3
# Критерии сравнения групп

# 1. Генерация выборок для всех ситуаций

# Ситуация a: равные средние и дисперсии
X1_a <- rnorm(100, mean = 0, sd = 1)
X2_a <- rnorm(100, mean = 0, sd = 1)

# Ситуация b: разные средние, равные дисперсии
X1_b <- rnorm(100, mean = 0, sd = 1)
X2_b <- rnorm(100, mean = 2, sd = 1)

# Ситуация c: равные средние, разные дисперсии
X1_c <- rnorm(100, mean = 0, sd = 1)
X2_c <- rnorm(100, mean = 0, sd = 2)

# Ситуация d: разные средние и дисперсии
X1_d <- rnorm(100, mean = 0, sd = 1)
X2_d <- rnorm(100, mean = 2, sd = 2)

# 2. Функция для анализа ситуации
analyze_situation <- function(X1, X2, situation_name) {
  # a. Проверка гипотез
  cat("\n--- Ситуация:", situation_name, "---\n")
  
  # Проверка нормальности (Шапиро-Уилк)
  shapiro_X1 <- shapiro.test(X1)
  shapiro_X2 <- shapiro.test(X2)
  cat("Нормальность X1: p-value =", shapiro_X1$p.value, "\n")
  cat("Нормальность X2: p-value =", shapiro_X2$p.value, "\n")
  
  # Проверка равенства средних (t-тест)
  t_test <- t.test(X1, X2, var.equal = TRUE)
  cat("Гипотеза о равенстве средних: p-value =", t_test$p.value, "\n")
  
  # Проверка равенства дисперсий (F-тест)
  var_test <- var.test(X1, X2)
  cat("Гипотеза о равенстве дисперсий: p-value =", var_test$p.value, "\n")
  
  # b. График гистограмм и плотностей
  par(mfrow = c(1, 2))
  hist(X1, col = rgb(1, 0, 0, 0.5), main = paste("Гистограммы:", situation_name), 
       xlab = "Значения", ylim = c(0, 0.5), probability = TRUE)
  hist(X2, col = rgb(0, 0, 1, 0.5), add = TRUE, probability = TRUE)
  lines(density(X1), col = "red", lwd = 2)
  lines(density(X2), col = "blue", lwd = 2)
  abline(v = mean(X1), col = "red", lty = 2, lwd = 2)
  abline(v = mean(X2), col = "blue", lty = 2, lwd = 2)
  legend("topright", legend = c("X1", "X2"), fill = c(rgb(1,0,0,0.5), rgb(0,0,1,0.5)))
  
  # c. График коробок с усами
  boxplot(list(X1, X2), names = c("X1", "X2"), col = c("red", "blue"),
          main = paste("Boxplot:", situation_name))
  par(mfrow = c(1, 1))
}

# Анализ всех ситуаций
analyze_situation(X1_a, X2_a, "a) Равные средние и дисперсии")
analyze_situation(X1_b, X2_b, "b) Разные средние, равные дисперсии")
analyze_situation(X1_c, X2_c, "c) Равные средние, разные дисперсии")
analyze_situation(X1_d, X2_d, "d) Разные средние и дисперсии")