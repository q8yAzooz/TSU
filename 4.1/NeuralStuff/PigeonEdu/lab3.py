import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split, Subset
from torchvision import transforms, datasets
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import os
from PIL import Image
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Установка seed для воспроизводимости
torch.manual_seed(42)
np.random.seed(42)

# Определяем классы согласно варианту (пример для нечетного дня рождения)
# Класс 0: Caries+Infection+Fractured, Класс 1: Healthy
# Для четного: CLASS_0 = ['BDC - BDR', 'Impacted Teeth'], CLASS_1 = ['Healthy Teeth']

# ТЕКУЩИЙ ВАРИАНТ (для нечетного дня рождения)
CLASS_0 = ['Caries', 'Infection', 'Fractured Teeth']
CLASS_1 = ['Healthy Teeth']

# Раскомментируйте для четного варианта:
# CLASS_0 = ['BDC - BDR', 'Impacted Teeth']
# CLASS_1 = ['Healthy Teeth']

IMAGE_SIZE = 224  # Размер входного изображения
BATCH_SIZE = 16  # Уменьшим batch size из-за возможных ограничений памяти
EPOCHS = 30
LEARNING_RATE = 0.001
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Путь к данным
DATA_PATH = r"C:\Users\VICTUS\Documents\GitHub\TSU\4.1\NeuralStuff\PigeonEdu\Dental OPG XRAY Dataset\Dental OPG (Classification)"

print(f"Используется устройство: {DEVICE}")
print(f"Путь к данным: {DATA_PATH}")

class DentalDataset(torch.utils.data.Dataset):
    """Пользовательский Dataset для загрузки изображений зубов"""
    def __init__(self, root_dir, class_0_dirs, class_1_dirs, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        
        print(f"Загрузка данных из {root_dir}")
        
        # Загрузка изображений класса 0
        for class_dir in class_0_dirs:
            class_path = os.path.join(root_dir, class_dir)
            if os.path.exists(class_path):
                print(f"Поиск в папке класса 0: {class_dir}")
                for img_name in os.listdir(class_path):
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        self.images.append(os.path.join(class_path, img_name))
                        self.labels.append(0)
                print(f"  Найдено {len([img for img in os.listdir(class_path) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))])} изображений")
            else:
                print(f"  Папка не найдена: {class_path}")
        
        # Загрузка изображений класса 1
        for class_dir in class_1_dirs:
            class_path = os.path.join(root_dir, class_dir)
            if os.path.exists(class_path):
                print(f"Поиск в папке класса 1: {class_dir}")
                for img_name in os.listdir(class_path):
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        self.images.append(os.path.join(class_path, img_name))
                        self.labels.append(1)
                print(f"  Найдено {len([img for img in os.listdir(class_path) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))])} изображений")
            else:
                print(f"  Папка не найдена: {class_path}")
        
        print(f"Всего загружено изображений: {len(self.images)}")
        print(f"Распределение по классам: Класс 0 - {self.labels.count(0)}, Класс 1 - {self.labels.count(1)}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        try:
            image = Image.open(img_path).convert('RGB')
            label = self.labels[idx]
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
        except Exception as e:
            print(f"Ошибка при загрузке изображения {img_path}: {e}")
            # Возвращаем другое изображение в случае ошибки
            return self.__getitem__((idx + 1) % len(self.images))

# Определение архитектур свёрточных сетей
class CNNArchitecture1(nn.Module):
    """Архитектура 1: Простая сеть с 3 сверточными слоями"""
    def __init__(self, num_classes=2):
        super(CNNArchitecture1, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
        )
        
        # Динамическое вычисление размера после сверток
        self._to_linear = None
        self._get_conv_output()
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self._to_linear, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def _get_conv_output(self):
        # Пропускаем через сверточную часть тензор нужного размера
        with torch.no_grad():
            dummy_input = torch.zeros(1, 3, IMAGE_SIZE, IMAGE_SIZE)
            dummy_output = self.features(dummy_input)
            self._to_linear = int(np.prod(dummy_output.size()))
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class CNNArchitecture2(nn.Module):
    """Архитектура 2: Увеличенное количество карт признаков"""
    def __init__(self, num_classes=2):
        super(CNNArchitecture2, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class CNNArchitecture3(nn.Module):
    """Архитектура 3: Сеть с residual блоками"""
    def __init__(self, num_classes=2):
        super(CNNArchitecture3, self).__init__()
        
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        
        self.res_block1 = self._make_res_block(32, 64)
        self.res_block2 = self._make_res_block(64, 128)
        self.res_block3 = self._make_res_block(128, 256)
        
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def _make_res_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25)
        )
    
    def forward(self, x):
        x = self.conv1(x)
        x = self.res_block1(x)
        x = self.res_block2(x)
        x = self.res_block3(x)
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x

class CNNArchitecture4(nn.Module):
    """Архитектура 4: Сеть с dilated convolutions"""
    def __init__(self, num_classes=2):
        super(CNNArchitecture4, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1, dilation=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=2, dilation=2),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1, dilation=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, padding=4, dilation=4),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1, dilation=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, padding=8, dilation=8),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

class CNNArchitecture5(nn.Module):
    """Архитектура 5: Сеть с разными размерами ядер"""
    def __init__(self, num_classes=2):
        super(CNNArchitecture5, self).__init__()
        
        self.conv1_3x3 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv1_5x5 = nn.Conv2d(3, 16, kernel_size=5, padding=2)
        self.conv1_7x7 = nn.Conv2d(3, 16, kernel_size=7, padding=3)
        self.bn1 = nn.BatchNorm2d(48)
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(48, 96, kernel_size=3, padding=1),
            nn.BatchNorm2d(96),
            nn.ReLU(),
            nn.Conv2d(96, 96, kernel_size=3, padding=1),
            nn.BatchNorm2d(96),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(96, 192, kernel_size=3, padding=1),
            nn.BatchNorm2d(192),
            nn.ReLU(),
            nn.Conv2d(192, 192, kernel_size=3, padding=1),
            nn.BatchNorm2d(192),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(192, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x1 = self.conv1_3x3(x)
        x2 = self.conv1_5x5(x)
        x3 = self.conv1_7x7(x)
        x = torch.cat([x1, x2, x3], dim=1)
        x = self.bn1(x)
        x = torch.relu(x)
        x = self.conv2(x)
        x = self.classifier(x)
        return x

def train_model(model, train_loader, val_loader, criterion, optimizer, epochs, device, model_name):
    """Функция для обучения модели"""
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    
    best_val_acc = 0.0
    patience = 10
    patience_counter = 0
    
    for epoch in range(epochs):
        # Обучение
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            if batch_idx % 10 == 0:
                print(f'  Batch [{batch_idx}/{len(train_loader)}], Loss: {loss.item():.4f}')
        
        train_loss = running_loss / len(train_loader)
        train_acc = 100 * correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # Валидация
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100 * correct / total
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        
        print(f'\nEpoch [{epoch+1}/{epochs}], {model_name}:')
        print(f'Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%')
        print(f'Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%')
        print('-' * 50)
        
        # Сохранение лучшей модели
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), f'best_model_{model_name}.pth')
            print(f'  -> Сохранена лучшая модель с точностью {val_acc:.2f}%')
            patience_counter = 0
        else:
            patience_counter += 1
            
        # Ранняя остановка
        if patience_counter >= patience:
            print(f'Ранняя остановка на эпохе {epoch+1}')
            break
    
    return train_losses, val_losses, train_accs, val_accs

def evaluate_model(model, test_loader, device):
    """Оценка модели на тестовых данных"""
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    return all_labels, all_preds

def plot_training_history(histories, model_names):
    """Построение графиков обучения"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (history, name) in enumerate(zip(histories, model_names)):
        train_losses, val_losses, train_accs, val_accs = history
        
        axes[0, 0].plot(train_losses, color=colors[i % len(colors)], label=f'{name}', linewidth=2)
        axes[0, 1].plot(val_losses, color=colors[i % len(colors)], label=f'{name}', linewidth=2)
        axes[1, 0].plot(train_accs, color=colors[i % len(colors)], label=f'{name}', linewidth=2)
        axes[1, 1].plot(val_accs, color=colors[i % len(colors)], label=f'{name}', linewidth=2)
    
    axes[0, 0].set_title('Training Loss', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    axes[0, 1].set_title('Validation Loss', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    axes[1, 0].set_title('Training Accuracy', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Accuracy (%)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].set_title('Validation Accuracy', fontsize=14, fontweight='bold')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Accuracy (%)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('training_history.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_confusion_matrix(y_true, y_pred, model_name):
    """Построение матрицы ошибок"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Class 0', 'Class 1'], 
                yticklabels=['Class 0', 'Class 1'])
    plt.title(f'Confusion Matrix - {model_name}', fontsize=14, fontweight='bold')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'confusion_matrix_{model_name}.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    print("="*60)
    print("НАЧАЛО ОБУЧЕНИЯ СВЕРТОЧНЫХ НЕЙРОННЫХ СЕТЕЙ")
    print("="*60)
    print(f"Устройство: {DEVICE}")
    print(f"Класс 0: {CLASS_0}")
    print(f"Класс 1: {CLASS_1}")
    print("="*60)
    
    # Определение трансформаций для аугментации данных
    train_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Создание датасета
    print("\nЗагрузка данных...")
    full_dataset = DentalDataset(
        root_dir=DATA_PATH,
        class_0_dirs=CLASS_0,
        class_1_dirs=CLASS_1,
        transform=train_transform
    )
    
    if len(full_dataset) == 0:
        print("ОШИБКА: Не найдено изображений! Проверьте пути к папкам.")
        return
    
    # Разделение на train/val/test
    train_size = int(0.7 * len(full_dataset))
    val_size = int(0.15 * len(full_dataset))
    test_size = len(full_dataset) - train_size - val_size
    
    print(f"\nРазмер выборок:")
    print(f"  Обучающая: {train_size}")
    print(f"  Валидационная: {val_size}")
    print(f"  Тестовая: {test_size}")
    
    # Создание индексов для разделения
    indices = list(range(len(full_dataset)))
    np.random.shuffle(indices)
    
    train_indices = indices[:train_size]
    val_indices = indices[train_size:train_size + val_size]
    test_indices = indices[train_size + val_size:]
    
    # Создание подмножеств с разными трансформациями
    train_dataset = Subset(full_dataset, train_indices)
    val_dataset = Subset(full_dataset, val_indices)
    test_dataset = Subset(full_dataset, test_indices)
    
    # Применение разных трансформаций
    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_transform
    test_dataset.dataset.transform = val_transform
    
    # Создание DataLoader
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    # Инициализация моделей
    models = [
        (CNNArchitecture1().to(DEVICE), "Architecture_1_Simple"),
        (CNNArchitecture2().to(DEVICE), "Architecture_2_Feature_Rich"),
        (CNNArchitecture3().to(DEVICE), "Architecture_3_Residual"),
        (CNNArchitecture4().to(DEVICE), "Architecture_4_Dilated"),
        (CNNArchitecture5().to(DEVICE), "Architecture_5_Multi_Kernel")
    ]
    
    criterion = nn.CrossEntropyLoss()
    histories = []
    results = []
    
    # Обучение каждой модели
    for model, model_name in models:
        print(f"\n{'='*60}")
        print(f"ОБУЧЕНИЕ МОДЕЛИ: {model_name}")
        print(f"{'='*60}")
        print(f"Количество параметров: {sum(p.numel() for p in model.parameters())}")
        
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)
        
        # Обучение
        history = train_model(
            model, train_loader, val_loader, 
            criterion, optimizer, EPOCHS, DEVICE, model_name
        )
        histories.append(history)
        
        # Загрузка лучшей модели
        model.load_state_dict(torch.load(f'best_model_{model_name}.pth'))
        
        # Оценка на тестовых данных
        y_true, y_pred = evaluate_model(model, test_loader, DEVICE)
        
        # Сохранение результатов
        results.append({
            'model_name': model_name,
            'y_true': y_true,
            'y_pred': y_pred
        })
        
        # Построение матрицы ошибок
        plot_confusion_matrix(y_true, y_pred, model_name)
        
        # Вывод метрик
        print(f"\nClassification Report for {model_name}:")
        print(classification_report(y_true, y_pred, target_names=['Class 0 (Caries+Infection+Fractured)', 'Class 1 (Healthy)']))
    
    # Построение общих графиков обучения
    plot_training_history(histories, [name for _, name in models])
    
    # Создание сводной таблицы результатов
    summary_data = []
    for result in results:
        cm = confusion_matrix(result['y_true'], result['y_pred'])
        accuracy = np.trace(cm) / np.sum(cm)
        
        # Precision, Recall, F1 для класса 1 (Healthy)
        tn, fp, fn, tp = cm.ravel()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        summary_data.append({
            'Model': result['model_name'],
            'Accuracy': f'{accuracy:.4f}',
            'Precision (Class 1)': f'{precision:.4f}',
            'Recall (Class 1)': f'{recall:.4f}',
            'F1-Score (Class 1)': f'{f1:.4f}'
        })
    
    summary_df = pd.DataFrame(summary_data)
    print("\n" + "="*70)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*70)
    print(summary_df.to_string(index=False))
    
    # Сохранение результатов в файл
    summary_df.to_csv('model_results.csv', index=False)
    print("\nРезультаты сохранены в файл 'model_results.csv'")
    
    # Находим лучшую модель
    best_model_idx = np.argmax([float(acc) for acc in summary_df['Accuracy']])
    print(f"\nЛУЧШАЯ МОДЕЛЬ: {summary_df.iloc[best_model_idx]['Model']}")
    print(f"Точность: {summary_df.iloc[best_model_idx]['Accuracy']}")

if __name__ == "__main__":
    main()