#ifndef LOGPARSER_H
#define LOGPARSER_H

#include <QString>
#include <QTimer>
#include <QDir>
#include <iostream>
#include <fstream>
#include <QDateTime>
#include <string>
#include <QTextStream>
#include <unistd.h>
#include <QFile>
#include "utilities/globalvariables.h"

enum LOGLEVEL{
    INFO,
    DEBUG,
    WARNING,
    ERROR,
    CRITICAL,
    LOGERROR,
    ST
};

class LogParser : public QObject{
    Q_OBJECT
public:
    explicit LogParser();
    static LogParser* getInstance();
    void init();
    static void writeLog(QString logType, const char* logSource, QString logMessage, int logLevel = LOGLEVEL::INFO);
    void startSynchronizationTimer();
    ~LogParser();

public slots:
    void synchronizeLogFile();

private:
    QTimer *_synchronizationTimer;
    static QString _logsDirPath;
    static QString _mainLogFilePath;
    static int _logTimeoutS;
    static LogParser *_instance;
};



#endif // LOGPARSER_H
