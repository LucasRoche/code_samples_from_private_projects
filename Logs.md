# Purpose

The application stores most of the actions executed in log files. These logs are used as a traceability tool both for debugging and troubleshooting. The log entries are timestamped and categorized for easier processing. Log file storage is done both locally and remotely on the AWS S3 server, so troubleshooting can be done remotely.

# Implementation

## Format
Log files are stored in CSV format, with semi-colon separators.

Each log entry is a row in the log file, with at least 5 columns organized as:

[LOG_LEVEL];DATE;[LOG_TYPE];SOURCE;MESSAGE;

With:
* LOG_LEVEL is the severity of the log message, which can be one of the following:
    * DEBUG : Information about non-critical processes, which are not needed to follow the state of the app. They are used to log more precise details about the internal state of the app for troubleshooting.
    * INFO : Information about key steps of each processes. This is the main log level used in the app, which should be sufficient to retrace the different processes execution.
    * WARNING : Information about an action or app state that could be abnormal but not critical to the execution.
    * ERROR : Information about an incorrect state that required error correction to continue normal execution.
    * LOGERROR : Error in the logging process itself, logged in a separate file.
    * ST : Information concerning the micro-controller state. The ST logs are sent to app by the micro-controller through UART, and logged by the app.

* DATE is the timestamp of the log message, formatted as yyyy-MM-dd.hh:mm:ss:zzz. Microsecond precision is required as most actions are only a few micro-seconds in duration.

* LOG_TYPE is the log category, depending on scope of the action logged, and process logging it. It can take the following values (non-exhaustive):
    * STARTUP : Logs relative to the startup of the app and launch of the different processes
    * USER: User identity, user switches
    * WIFI
    * UART: Communication with the micro-controller
    * I2C: Low-level read/write actions on the cartridges
    * GPIO: Interaction with the tactile button, LED, and door sensor
    * RTC: Low-level time-keeping
    * STLOG: logs ofthe micro-controller
    * PAGES: User interaction and page display
    * NOTIFICATIONS: Creation, storage and display of notifications
    * DELIVERY: Processes related to the delivery
    * DELIVERY_END: Human readable summary of the delivery
    * DELIVERY_CHECK: Various check before delivery
    * STOCK: State of the cartridges
    * INITIALIZATION: Cartridge initialization process
    * DATABASE: Interaction with the API
    * HTML_REQUEST: Low-level handling of API calls
    * PROGRAM: User program update process
    * USERALERT: Visual reminders for the user
    * REMOTEACCESS: Remote access process
    * USER_SURVEYS

* SOURCE : Function from which the entry is logged, formatted as CALLER_OBJECT_NAME::FUNCTION(ARGS).

* Message: Content of the log entry. This field can potentially contains semi-colons to further divide the message in multiple fields for readability or automated processing.


## Content
### What is logged ?

Every major step of every key process in the app is logged as an info entry. These include deliveries, timer triggers, UART and I2C communication, wifi management, etc....

Debug entries include further details in process that are prone to require troubleshooting (delivery, wifi, I2C, UART).

Every user action is also logged (screen and button interactions).

Importantly, every error or uncommon behavior is logged, with varying degrees of severity (ERROR/WARNING).

### What is not logged ?

Minute details of processes (function entry and exit, data structures content ...) are not logged unless part of critical processes, in order to limit the total size of the log files.


## The LogParser module

This module (instantiated by the MainController) is used to write the log entries on the log files. To avoid having to manage signals from every part of the app to the LogParser, a static method is used (LogParser::writeLog), and the logparser.h header is linked in the globalvariables.h header, itself linked in every other module.

The writeLog static method take four arguments (log level and type, caller function, and message), creates the log message string, and writes it to the log file. A while loop with 10s timeout is used to request write permissions, to avoid multiple calls to the function trying to write simultaneously to the file.

# Storage

## Local

### File location

The logs are stored in /usr/share/coati/logs/ with a .log extension. The main log file is called all.log. 

### File synchronisation

On recent UNIX systems, a low level call to write() is first applied to the running kernel filesystem, stored and executed in volatile memory. The filesystem is periodically synchronized and actually stored to non-volatile memory. In case of power-failure, data "written" since the last synchronization is lost. On the linux used in the machine, automatic synchronization seems to be performed approximately once every 30s. A 30s loss of information in case of power-failure is not acceptable for the logging system, so a forced synchronization (call to sync()) is done every two seconds, triggered by a periodic timer in the LogParser module (a sync call after every write would be unoptimal and severy slow the app).

### File size limit and archive handling

The log files quickly reach extreme sizes, due to the high amount of data logged (DEBUG logs are still used in production due to the frequency of bugs). In order to reduce the impact of file size on the file system and on the log upload process, a limit of 50 Mo is enforced on the log file. A shell script is launched periodically by an internal timer in the app, which check the current (all.log) log file size. If the log file is too big, its content is copied in an archive, named log_DATE.archive.log, and the all.log file is erased to start anew.

## Cloud synchronization

To allow remote trouble shooting and automatized log storage and centralization, a systemd timer service is set to launch a log upload script /________/uploadLogs.sh every day at 03:00. The timer is installed during the first machine programmation process.
The log upload script upload every .log file in the folder to an AWS S3 bucket called mvplogs, in a subfolder named as the serial number of the machine. 

WARNING: the uploadLogs.sh script can't be updated easily remotely, but would need to be changed to check if an archive has already been uploaded to the S3 repo before attempting upload, to reduce the amount of data that needs to be uploaded every day.
