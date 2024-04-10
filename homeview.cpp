#include "homeview.h"

// This is the main view of the widget
// It is accessed from the UnlockWidgetView on start and sleep exit, or from any other page from their Home Button
// The view display the following elements :
//      - Information about the current mode :
//          - mode name
//          - cartridges used in the mode and their status (activated, deactivated, unavailable)
//      - Settings button to access the SettingsMenu view
//      - Sleep button to enter sleep mode
//      - Wifi icon : display the connection status, can be clicked to access WifiSettings view directly
//      - Clock
//      - MeteoIcon : displays current weather and temeprature, can be clicked to access 3 days forecast
//      - Alternative mode icons (can be clicked to switch to another mode available)
//      - If a cartridge in stock is empty, displays an alert message (EmptyCartridgeAlertWidget) which can be clicked to access the CartridgChangeView

// On instantiation, the current mode is chosen as the first main mode available for the time slot (the page is refreshed periodically)
// If the user program contains standalone cartridges (cartridges that can be consumed separately from the program), secondary mode icons are displayed for these cartridges
//      Clicking on secondary mode icons switches the current mode icon to the chosen secondary mode (can be switched back)
// The user can use the cartridges labels to toggle available cartridges status from activated (used in the mode) to deactivated
//      Cartridge status is available when the cartridge is detected and not empty, it can then be toggled between activated and deactivated
//      Cartridge status is unavailable when the cartridge is either missing from the slots or empty

QString HomeView::pageID = PageID::Home;
HomeView::HomeView(QWidget *parent) : ModeSelectionViewTemplate(parent, 0)
{
//    this->setStyleSheet("QWidget{background-color:black;color:white}");
    configDict = g_configDict;
    _width = static_cast<int>(configDict["___"]["___"]);
    _height = configDict["___"]["___"];

    createTopLayout();
    createMainLayouts();
    _timeline = new CureTimelineWidget(this, 400, 95);
    _mainLayout->addWidget(_timeline, 6, 0, Qt::AlignCenter);
    _mainLayout->setRowMinimumHeight(7, 20);
}

// Create the settings and sleep buttons
// Create the clock, wifi and meteo icons
// Creates the EmptyCartridgeAlertWidget, hidden by default
void HomeView::createTopLayout(){
    CustomPushButton *settingsButton = new CustomPushButton(this, "settingsmenu", BUTTON_SIZE_NAVIGATION);
    connect(settingsButton, &CustomPushButton::clicked, this, [=]() {emit next(pageID, PageID::SettingsMenu); updateModeButtons();});
    //Position of settings, user switch and sleep buttons are hardcoded for simplicity (can't use the same margins as the other pages here, it ruins the layout)
    settingsButton->setGeometry(39,29,BUTTON_SIZE_NAVIGATION,BUTTON_SIZE_NAVIGATION);

    _sleepButton = new CustomPushButton(this, "sleep", BUTTON_SIZE_NAVIGATION);
    connect(_sleepButton, &CustomPushButton::clicked, this, [=]() {emit next(pageID, PageID::ScreenSaver); updateModeButtons();});
    _sleepButton->setGeometry(_width-39-BUTTON_SIZE_NAVIGATION,29,BUTTON_SIZE_NAVIGATION,BUTTON_SIZE_NAVIGATION);

    _switchUserButton = new CustomPushButton(this, "sleep", BUTTON_SIZE_NAVIGATION);
    connect(_switchUserButton, &CustomPushButton::clicked, this, [=]() {emit next(pageID, PageID::UserSelection);});
    _switchUserButton->setGeometry(_width-39-BUTTON_SIZE_NAVIGATION,29,BUTTON_SIZE_NAVIGATION,BUTTON_SIZE_NAVIGATION);
    _switchUserButton->hide();

//    meteoButton = new MeteoIcon(this, {});
//    connect(meteoButton, &MeteoIcon::clicked, this, [=]() {emit next(pageID, PageID::MeteoWidget);updateModeButtons();});

    Clock *clock = new Clock(this);
//    clock->setSize(20);
    clock->setStyleSheet("Clock{border-style:none; background:rgba(0,0,0,0); color : rgba(50,50,50, 255);font-size:20px;font-weight:300}");

    _wifiIcon = new CustomPushButton(this, "wifiIcon", 25, "iconMeteoNull");
//    connect(_wifiIcon, &CustomPushButton::clicked, this, [=]() {emit next(pageID, PageID::WifiSettings); updateModeButtons();});

    _greetingsLabel = new QLabel("", this);
    _greetingsLabel->setStyleSheet("font-size:25px; font-weight:400px");

    QGridLayout *topLayout = new QGridLayout();
    topLayout->setRowMinimumHeight(0, 10);
    topLayout->setRowMinimumHeight(1, BUTTON_SIZE_NAVIGATION);
    topLayout->setColumnMinimumWidth(0, 39+BUTTON_SIZE_NAVIGATION);
//    topLayout->addWidget(meteoButton , 1 , 1, Qt::AlignLeft|Qt::AlignCenter);
    topLayout->setColumnStretch(2, 1);
    topLayout->setColumnMinimumWidth(3, 40);
    topLayout->addWidget(clock , 1 , 4, Qt::AlignCenter|Qt::AlignCenter);
    topLayout->addWidget(_wifiIcon , 1 , 5, Qt::AlignCenter|Qt::AlignCenter);
    topLayout->setColumnMinimumWidth(6, 39+BUTTON_SIZE_NAVIGATION);
    topLayout->setRowMinimumHeight(2, 60);
    topLayout->addWidget(_greetingsLabel , 3 , 0, 1, 7, Qt::AlignCenter|Qt::AlignTop);

    _mainLayout->addLayout(topLayout, 0, 0);

    _cartridgeChangeWidget = new EmptyCartridgeAlertWidget(this, 160, 50);
    _cartridgeChangeWidget->setGeometry(_width/2 - 80, 180, 160, 50);
    _cartridgeChangeWidget->hide();
    _cartridgeChangeWidget->raise();
    connect(_cartridgeChangeWidget, &EmptyCartridgeAlertWidget::clicked, this, [=](){emit next(pageID, PageID::CartridgesChange);});
}


// Executed when one of the mode buttons is clicked
// If its the current selected mode:
//      - Emits signal to PageRouter to display the next page (DeliveryInfoView)
//      - Emits signal to DeliveryManager to update the machine current delivery mode
// If its an alternative mode, switch the current mode to the mode which was selected
void HomeView::onModeSelected(QString modeName){
    emit next(pageID, PageID::DeliveryInfo, {{"___", modeName.toStdString()}});
    emit send(pageID, {{"___", modeName.toStdString()}, {"___", DELIVERY::TYPE::NORMAL}});
}

// Executed when clicking on the button showed when no program is available for the user, redirect to ProgramDownload page
void HomeView::onRedirectToProgramDownloadClicked(){
    emit next(pageID, PageID::ProgramDownload);
}

// Return the current minute of the day, used by the updateModeButtons method (defined in the base class)
int HomeView::getMinuteForModeTimeSlot(){
    QTime time = QTime::currentTime();
    return 60*time.hour() + time.minute();
}

// Executed when receiving the user config model
// Hide/show the user switch button if the machine is in single/multi user mode
// Displays a customized welcome message
void HomeView::onUserConfigModelReceived(json userConfigModel){
    if(userConfigModel.size()>1){
        _switchUserButton->show();
        _sleepButton->hide();
    }
    else {
        _switchUserButton->hide();
        _sleepButton->show();
    }
    QString greetingsText;
    int hour = QTime::currentTime().hour();
    if (hour >= 18) {
        greetingsText = tr("Bonsoir, ");
    }
    else {
        greetingsText = tr("Bonjour, ");
    }
    QStringList nameElements = QString::fromStdString(userConfigModel[g_userIndex]["___"]).split("_");
    QString userName;
    if(nameElements.size()>3){
        userName = capitalizeFirstLetter(nameElements[1]) + " " + capitalizeFirstLetter(nameElements[2]);
    }
    else {
        userName = QString::fromStdString(userConfigModel[g_userIndex]["___"]);
    }
    greetingsText += userName +" !";
    _greetingsLabel->setText(greetingsText);
}


// Executed when receiving meteo model data
// Update meteo icon
void HomeView::onMeteoModelReceived(json meteoModel){
//    meteoButton->updateFromModel(meteoModel);
}

// Executed when receiving empty cartridges signal from stock model
// display empty cartridge icon
// TO DO : statute on utility of this
void HomeView::onEmptyCartridgesReceived(json emptyCartridges){
//    if(emptyCartridges.is_null()){
//        _cartridgeChangeWidget->hide();
//        LogParser::writeLog("HOME", Q_FUNC_INFO, "No empty cartridge detected, hiding warning on home page", LOGLEVEL::DEBUG);
//    }
//    else {
//        _cartridgeChangeWidget->show();
//        LogParser::writeLog("HOME", Q_FUNC_INFO, "Empty cartridge detected, displaying warning on home page", LOGLEVEL::INFO);
//    }
//    _cartridgeChangeWidget->raise();
}

// Executed when receiving successfull network connection signal from WifiManager
// Update mode buttons (in case the clock wasn't on time)
// Ask meteo model data to update meteo icon
void HomeView::onWifiConnectionResult(WIFI_RETURN_CODE result, QString wifiName){
    if(result == WIFI_RETURN_CODE::SUCCESS){
        LogParser::writeLog("HOME", Q_FUNC_INFO, "Successfull wifi connection signal received, updating mode buttons and météo", LOGLEVEL::DEBUG);
        updateModeButtons(_currentModeName);
        emit askForMeteo();
//        emit getCurrentWifi();
    }
}

// Executed when receiving current wifi information from a WifiManager signal
// Update wifi icon depending on wifi strength
void HomeView::onCurrentWifiReceived(QString wifiName, int signalStrength){
    QString iconName = WifiSettingsView::signalStrengthToIconName(signalStrength);
    _wifiIcon->changeIcon(iconName);
}


void HomeView::updateTimeline(json modesModel){
    if(modesModel.is_null() || modesModel.size()==0){
        _timeline->hide();
        return;
    }
    if(!modesModel[0].contains("___") || !modesModel[0].contains("___")){
        _timeline->hide();
        return;
    }
    QDate startDate = QDate::fromString(QString::fromStdString(modesModel[0]["___"]), "yyyy-MM-dd");
    QDate endDate = QDate::fromString(QString::fromStdString(modesModel[0]["___"]), "yyyy-MM-dd");
    _timeline->setUpTimeLine(startDate, endDate);
    _timeline->show();
}

