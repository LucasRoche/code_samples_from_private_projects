#include "logparser.h"

// This file is included in every other in order to allow logging
// The function can be called asynchronously without simultaneous write conflict by checking that the log file is available for I/O before opening it
// The logType arguments describe the category of the activity to be logged (STARTUP, DELIVERY, PAGES ...)
// The logSource argument is the function in which the LogParser::writeLog function is called, which is retrieved by the Q_FUNC_INFO macro
// The logMessage argument is the body of the log (info about the action/error)
// The logLevel argument is one of the following :
//      -DEBUG : used for non-important actions and tracing, usefull for debugging
//      -INFO : important actions done by the machine (delivery actions, program changes, wifi connection ...)
//      -ST : logs from the ST embedded microcontroller
//      -WARNING : non critical problem
//      -ERROR/CRITICAL : critical problem, threatening the app functionning
//      -LOGERROR : called by this function when encountering a problem (by calling itself)
// The different levels are stored both separately in different files, and dumped together in the all.log file
QString LogParser::_logsDirPath = "";
QString LogParser::_mainLogFilePath;
LogParser* LogParser::_instance = nullptr;
int LogParser::_logTimeoutS = 10;
LogParser::LogParser(){

}

LogParser* LogParser::getInstance(){
    if(_instance == nullptr){
        _instance = new LogParser();
    }
    return _instance;
}


void LogParser::init(){
    if(g_isEMBEDDEDENVIRONMENT){
        _logsDirPath = "___";
    }
    else{
        _logsDirPath = QDir::currentPath() + "___";
    }
    _mainLogFilePath = _logsDirPath + "___";
}

// Timer needs to be started by a Q_OBJECT, but the first log is in the main, so this function is called by the MainController
void LogParser::startSynchronizationTimer(){
    _synchronizationTimer = new QTimer();
    connect(_synchronizationTimer, SIGNAL(timeout()), this, SLOT(synchronizeLogFile()));
    _synchronizationTimer->start(2000);
}


void LogParser::writeLog(QString logType, const char* logSource, QString logMessage, int logLevel){
    //Checks that the logs folder exists, creates it if necessary
    if(_logsDirPath == ""){
        LogParser::getInstance()->init();
    }
    if(!QDir(_logsDirPath).exists()){
        QDir().mkdir(_logsDirPath);
    }
    QDateTime dateTime = QDateTime();
    dateTime = dateTime.currentDateTime();
    QString date = dateTime.toString("yyyy-MM-dd.hh:mm:ss:zzz");
    QString level;
    QString fillerSpaces = "";

    QString fileName;
    switch(logLevel){
    case LOGLEVEL::DEBUG:
        if(g_configDict["debugActive"]==0 && g_isEMBEDDEDENVIRONMENT == 1){
            return;     // Do not store debug log in normal run mode to avoid accumulating large log file
        }
        fileName = _mainLogFilePath;
        level = "DEBUG";
        break;
    case LOGLEVEL::INFO:
        fileName = _mainLogFilePath;
        level = "INFO";
        fillerSpaces = "   ";
        break;
    case LOGLEVEL::WARNING:
        fileName = _mainLogFilePath;
        level = "WARNING";
        break;
    case LOGLEVEL::ERROR:
        fileName = _mainLogFilePath;
        level = "ERROR";
        break;
    case LOGLEVEL::CRITICAL:
        fileName = _mainLogFilePath;
        level = "CRITICAL";
        break;
    case LOGLEVEL::LOGERROR:
        fileName = _logsDirPath + "___" + date + "___";
        level = "LOGERROR";
        break;
    case LOGLEVEL::ST:
        fileName = _mainLogFilePath;
        level = "ST";
        fillerSpaces = "   ";
        break;
    }

    QString logText = "["+level+"];\t" + fillerSpaces + date + ";\t[" + logType + "];\t" + QString(logSource) + ";\t" + logMessage;

    //Avec boucle while
    QFile outFile(fileName);
    time_t startTime = time(nullptr);
    while(1){
        if(time(nullptr) > startTime + _logTimeoutS){
            LogParser::writeLog(logType, "logParser" ,logMessage, LOGLEVEL::LOGERROR);
            return;
        }
        if(outFile.open(QIODevice::WriteOnly | QIODevice::Append) == 1){
            break;
        }
        usleep(10000);
    }
    QTextStream ts(&outFile);
    ts << logText << "\n";
    outFile.close();

    if(g_configDict["___"]==1 || g_isEMBEDDEDENVIRONMENT == 0){
        std::cout << (logText).toStdString() << std::endl;
    }
}

// Called periodically from _synchronizationTimer timeout
// call fsync to make sure the log file is correctly written in memory
void LogParser::synchronizeLogFile(){
    QFile outFile(_mainLogFilePath);
    time_t startTime = time(nullptr);
    while(1){
        if(time(nullptr) > startTime + _logTimeoutS){
            LogParser::writeLog("SYNC", "logParser" ,"Synchronization error: couldn't open file", LOGLEVEL::LOGERROR);
            return;
        }
        if(outFile.open(QIODevice::WriteOnly | QIODevice::Append) == 1){
            break;
        }
        usleep(10000);
    }
    outFile.flush();
    fsync(outFile.handle());
    outFile.close();
}

LogParser::~LogParser(){
    _synchronizationTimer->stop();
}


