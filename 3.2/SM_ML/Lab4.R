# Загрузка данных
pulse_data <- read.table("pulse.txt", header = TRUE, fill = TRUE)

# Проверка на нормальность (графически и критерий Шапиро-Уилка)
par(mfrow = c(2, 2))
for (col in names(pulse_data)) {
  hist(pulse_data[[col]], main = paste("Гистограмма для", col), xlab = "Пульс", probability = TRUE)
  lines(density(pulse_data[[col]], na.rm = TRUE), col = "red")
  qqnorm(pulse_data[[col]], main = paste("Q-Q plot для", col))
  qqline(pulse_data[[col]])
  shapiro_p <- shapiro.test(pulse_data[[col]])$p.value
  cat("Группа", col, ": p-value =", shapiro_p, "\n")
}

# Сравнение групп «до» и «после»
# Для здоровых (EB vs EA)
t_test_healthy <- t.test(pulse_data$EB, pulse_data$EA, paired = FALSE)
cat("p-value для здоровых (до vs после):", t_test_healthy$p.value, "\n")

# Для пациентов (CB vs CA)
t_test_patient <- t.test(pulse_data$CB, pulse_data$CA, paired = FALSE)
cat("p-value для пациентов (до vs после):", t_test_patient$p.value, "\n")

# Boxplot для сравнения
boxplot(pulse_data$EB, pulse_data$EA, pulse_data$CB, pulse_data$CA,
        names = c("EB (до)", "EA (после)", "CB (до)", "CA (после)"),
        col = c("lightblue", "lightgreen", "pink", "orange"),
        main = "Сравнение пульса до и после")

# Сравнение здоровых и пациентов внутри временных точек
# До (EB vs CB)
t_test_before <- wilcox.test(pulse_data$EB, pulse_data$CB, var.equal = TRUE)
cat("p-value (до: здоровые vs пациенты):", t_test_before$p.value, "\n")

# После (EA vs CA)
t_test_after <- wilcox.test(pulse_data$EA, pulse_data$CA, var.equal = TRUE)
cat("p-value (после: здоровые vs пациенты):", t_test_after$p.value, "\n")

# Загрузка данных (пример данных)
grades <- data.frame(
  Группа = rep(c("Группа1", "Группа2", "Группа3", "Группа4"), each = 10),
  Оценка = c(3,4,5,3,4,5,4,3,4,5,3,4,5,4,5,4,3,4,5,4,3, 5,4,3,4,5,4,3,4,5,4, 3,4,5,3,4,5,4,3,4,5)
)

# Создание таблицы сопряженности
contingency_table <- table(grades$Группа, grades$Оценка)
print("Таблица сопряженности:")
print(contingency_table)

# Критерий Хи-квадрат
chi_test <- chisq.test(contingency_table)
cat("p-value критерия Хи-квадрат:", chi_test$p.value, "\n")

# Если ожидаемые частоты <5, используем критерий Фишера
if (any(chi_test$expected < 5)) {
  fisher_test <- fisher.test(contingency_table)
  cat("p-value критерия Фишера:", fisher_test$p.value, "\n")
}