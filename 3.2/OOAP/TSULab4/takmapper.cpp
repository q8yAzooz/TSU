// taskmapper.cpp
#include "taskmapper.h"
#include <QFile>
#include <QJsonDocument>
#include <QJsonArray>
#include <QJsonObject>
#include <QDebug>

TaskMapper::TaskMapper(const QString& filePath) : m_filePath(filePath) {}

QList<Task> TaskMapper::findAll() {
    QList<Task> tasks;
    QFile file(m_filePath);

    if (!file.open(QIODevice::ReadOnly)) {
        qWarning() << "Failed to open file for reading:" << file.errorString();
        return tasks;
    }

    QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
    QJsonArray jsonArray = doc.array();

    for (const QJsonValue& value : jsonArray) {
        QJsonObject obj = value.toObject();
        tasks.append(Task(
            obj["id"].toInt(),
            obj["title"].toString(),
            obj["description"].toString(),
            obj["completed"].toBool(),
            QDateTime::fromString(obj["createdAt"].toString(), Qt::ISODate)
            ));
    }

    file.close();
    return tasks;
}

void TaskMapper::save(const Task& task) {
    QList<Task> tasks = findAll();
    bool exists = false;

    for (Task& t : tasks) {
        if (t.id() == task.id()) {
            t = task;
            exists = true;
            break;
        }
    }

    if (!exists) {
        Task newTask(generateNewId(), task.title(), task.description(), task.isCompleted(), task.createdAt());
        tasks.append(newTask);
    }

    QJsonArray jsonArray;
    for (const Task& t : tasks) {
        QJsonObject obj;
        obj["id"] = t.id();
        obj["title"] = t.title();
        obj["description"] = t.description();
        obj["completed"] = t.isCompleted();
        obj["createdAt"] = t.createdAt().toString(Qt::ISODate);
        jsonArray.append(obj);
    }

    QFile file(m_filePath);
    if (!file.open(QIODevice::WriteOnly)) {
        qWarning() << "Failed to open file for writing:" << file.errorString();
        return;
    }

    file.write(QJsonDocument(jsonArray).toJson());
    file.close();
}

void TaskMapper::remove(int taskId) {
    QList<Task> tasks = findAll();
    auto it = std::remove_if(tasks.begin(), tasks.end(),
                             [taskId](const Task& t) { return t.id() == taskId; });

    if (it != tasks.end()) {
        tasks.erase(it, tasks.end());

        QJsonArray jsonArray;
        for (const Task& t : tasks) {
            QJsonObject obj;
            obj["id"] = t.id();
            obj["title"] = t.title();
            obj["description"] = t.description();
            obj["completed"] = t.isCompleted();
            obj["createdAt"] = t.createdAt().toString(Qt::ISODate);
            jsonArray.append(obj);
        }

        QFile file(m_filePath);
        if (file.open(QIODevice::WriteOnly)) {
            file.write(QJsonDocument(jsonArray).toJson());
            file.close();
        }
    }
}

int TaskMapper::generateNewId() {
    QList<Task> tasks = findAll();
    int maxId = 0;
    for (const Task& t : tasks) {
        if (t.id() > maxId) maxId = t.id();
    }
    return maxId + 1;
}
