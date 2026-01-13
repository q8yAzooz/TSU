#ifndef TASK_H
#define TASK_H

#include <QDateTime>
#include <QString>

class Task {
public:
    Task(int id = -1, const QString& title = "", const QString& description = "",
         bool completed = false, const QDateTime& createdAt = QDateTime::currentDateTime())
        : m_id(id), m_title(title), m_description(description),
        m_completed(completed), m_createdAt(createdAt) {}

    int id() const { return m_id; }
    QString title() const { return m_title; }
    QString description() const { return m_description; }
    bool isCompleted() const { return m_completed; }
    QDateTime createdAt() const { return m_createdAt; }

    void setTitle(const QString& title) { m_title = title; }
    void setDescription(const QString& description) { m_description = description; }
    void setCompleted(bool completed) { m_completed = completed; }

private:
    int m_id;
    QString m_title;
    QString m_description;
    bool m_completed;
    QDateTime m_createdAt;
};

Q_DECLARE_METATYPE(Task)
#endif // TASK_H
