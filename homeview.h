#ifndef HOMEVIEW_H
#define HOMEVIEW_H
#include "logs/logparser.h"
#include <QWidget>
#include <QGridLayout>
#include "widgetElements/clock.h"
#include "widgetElements/custompushbutton.h"
#include "templates/modeselectionviewtemplate.h"
#include "utilities/globalvariables.h"
#include "meteoWidget/meteoicon.h"
#include <QTime>
#include "widgetElements/checkablelabel.h"
#include "emptycartridgealertwidget.h"
#include "wifiSettingsWidget/wifisettingsview.h"
#include "models/config/userconfigmodel.h"
#include "utilities/capitalizefirstletter.h"
#include "wifi/wifimanager.h"
#include "pages/widgetElements/curetimelinewidget.h"

class HomeView : public ModeSelectionViewTemplate
{
    Q_OBJECT
public:
    explicit HomeView(QWidget *parent = nullptr);
    static QString pageID;
//    MeteoIcon *meteoButton;
    void createTopLayout();

signals:
    void askForMeteo();
    void checkForEmptyCartridges();
    void getCurrentWifi();
    void askForUserConfigModel();

public slots:
    void sendAskForMeteo(){emit askForMeteo();}
    void onEmptyCartridgesReceived(json emptyCartridges);
    void onWifiConnectionResult(WIFI_RETURN_CODE result, QString wifiName);
    void onCurrentWifiReceived(QString wifiName, int signalStrength);
    void onMeteoModelReceived(json meteoModel);
    void onModeSelected(QString modeName);
    void onUserConfigModelReceived(json model);
    void onRedirectToProgramDownloadClicked();
    void updateTimeline(json modesModel);

protected:
    EmptyCartridgeAlertWidget *_cartridgeChangeWidget;
    CustomPushButton *_wifiIcon;
    int getMinuteForModeTimeSlot();
    CustomPushButton *_sleepButton;
    CustomPushButton *_switchUserButton;
    QLabel *_greetingsLabel;
    CureTimelineWidget *_timeline;
};

#endif // HOMEVIEW_H
