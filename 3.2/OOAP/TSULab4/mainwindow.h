#ifndef MAINWINDOW_H
#define MAINWINDOW_H

// mainwindow.h
#include <QMainWindow>
#include "taskmapper.h"

class QListWidget;

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    MainWindow(QWidget *parent = nullptr);

private slots:
    void addTask();
    void editTask();
    void deleteTask();
    void toggleTaskCompletion();

private:
    void setupUI();
    void loadTasks();
    void updateTaskList();

    TaskMapper m_taskMapper;
    QListWidget* m_taskList;
};

#endif // MAINWINDOW_H
