#ifndef TASKMAPPER_H
#define TASKMAPPER_H

// taskmapper.h
#include <QList>
#include <QString>
#include "task.h"

class TaskMapper {
public:
    TaskMapper(const QString& filePath = "tasks.json");

    QList<Task> findAll();
    void save(const Task& task);
    void remove(int taskId);

private:
    QString m_filePath;
    int generateNewId();
};

#endif // TASKMAPPER_H
