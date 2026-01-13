// mainwindow.cpp
#include "mainwindow.h"
#include "taskdialog.h"
#include <QListWidget>
#include <QVBoxLayout>
#include <QPushButton>
#include <QMessageBox>

// Убрать все SQL-заголовки и зависимости

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent) {
    setupUI();
    loadTasks();
}

void MainWindow::setupUI() {
    QWidget* centralWidget = new QWidget;
    QVBoxLayout* layout = new QVBoxLayout;

    m_taskList = new QListWidget;
    m_taskList->setSelectionMode(QAbstractItemView::SingleSelection);

    QHBoxLayout* buttonLayout = new QHBoxLayout;
    QPushButton* addButton = new QPushButton("Add Task");
    QPushButton* editButton = new QPushButton("Edit Task");
    QPushButton* deleteButton = new QPushButton("Delete Task");

    connect(addButton, &QPushButton::clicked, this, &MainWindow::addTask);
    connect(editButton, &QPushButton::clicked, this, &MainWindow::editTask);
    connect(deleteButton, &QPushButton::clicked, this, &MainWindow::deleteTask);

    buttonLayout->addWidget(addButton);
    buttonLayout->addWidget(editButton);
    buttonLayout->addWidget(deleteButton);

    layout->addWidget(m_taskList);
    layout->addLayout(buttonLayout);
    centralWidget->setLayout(layout);
    setCentralWidget(centralWidget);

    setWindowTitle("Task Manager");
    resize(600, 400);
}

void MainWindow::loadTasks() {
    m_taskList->clear();
    foreach (const Task& task, m_taskMapper.findAll()) {
        QListWidgetItem* item = new QListWidgetItem(task.title());
        item->setData(Qt::UserRole, QVariant::fromValue(task));
        item->setCheckState(task.isCompleted() ? Qt::Checked : Qt::Unchecked);
        m_taskList->addItem(item);
    }
}

// Реализации addTask, editTask и deleteTask оставить без SQL-логики
