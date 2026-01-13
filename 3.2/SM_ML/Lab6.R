# Лабораторная работа №6: Регрессионный анализ «Квартиры»

# 1. Импорт данных
flats <- read.csv2("flats R.csv", sep = ";", dec = ",", fileEncoding = "Windows-1251")

# 2. Переименование столбцов
colnames(flats) <- c("Type", "Rent", "Floor", "TotalFloors", "Area", "Furniture")

# 3. Графики для визуализации данных
library(ggplot2)

# Гистограммы
ggplot(flats, aes(x = Rent)) + geom_histogram(fill = "skyblue") + ggtitle("Распределение арендной платы")
ggplot(flats, aes(x = Area)) + geom_histogram(fill = "salmon") + ggtitle("Распределение площади")

# Диаграммы рассеяния
ggplot(flats, aes(x = Area, y = Rent)) + 
  geom_point(color = "blue") + 
  ggtitle("Зависимость арендной платы от площади")

# Boxplot по категориям
ggplot(flats, aes(x = Furniture, y = Rent, fill = Furniture)) + 
  geom_boxplot() + 
  ggtitle("Арендная плата по наличию мебели")

# 4. Корреляционный анализ
cor_matrix <- cor(flats[, c("Rent", "Area", "Floor", "TotalFloors")])
print(cor_matrix)

# 5. Парная регрессия: Rent ~ Area
model1 <- lm(Rent ~ Area, data = flats)
summary(model1)

# 6. Проверка остатков на нормальность
shapiro.test(resid(model1)) # Тест Шапиро-Уилка
qqnorm(resid(model1))
qqline(resid(model1))

# 7. Проверка на гетероскедастичность (тест Бреуша-Пагана)
library(lmtest)
bptest(model1)

# 8. Устранение гетероскедастичности
# Способ 1: Деление на Area
flats$Rent_scaled <- flats$Rent / flats$Area
model2 <- lm(Rent_scaled ~ Area, data = flats)

# Способ 2: Логарифмирование
flats$log_Rent <- log(flats$Rent)
model3 <- lm(log_Rent ~ Area, data = flats)

# 9. Проверка новой модели
summary(model3)
bptest(model3) # Тест на гетероскедастичность

# 12. График регрессии с доверительными интервалами
ggplot(flats, aes(x = Area, y = log_Rent)) + 
  geom_point() + 
  geom_smooth(method = "lm", se = TRUE, color = "red") + 
  ggtitle("Логарифмированная модель")

# 13. Множественная регрессия
full_model <- lm(Rent ~ Area + Floor + TotalFloors + Furniture, data = flats)
summary(full_model)

# 14. Удаление незначимых факторов (p > 0.05)
reduced_model <- lm(Rent ~ Area + Furniture, data = flats)
summary(reduced_model)

# 15. Прогноз для своей квартиры
new_data <- data.frame(Area = 40, Furniture = "есть")
predict(reduced_model, newdata = new_data, interval = "confidence")

# 16. Анализ остатков
plot(reduced_model, which = 1:4)

# 17. Логарифмирование для устранения гетероскедастичности
final_model <- lm(log_Rent ~ Area + Furniture, data = flats)
summary(final_model)