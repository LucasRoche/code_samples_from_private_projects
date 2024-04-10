#!/usr/bin/env python3

from http import client
from nbformat import current_nbformat
import requests
import datetime
import dateutil.relativedelta
import pandas as pd
import json
import xlsxwriter
import locale
import pprint
import time
import statistics
import numpy as np
import matplotlib.pyplot as plt
from airium import Airium
import pdfkit
from math import ceil


# Needs:
# sudo apt install wkhtmltopdf pdfkit
# pip install airium numpy matplotlib xlsxwriter pprint json pandas

URL_LOGIN = '___'
URL_PDS_GETALL = "___"
URL_PATIENT_GET = "___"
URL_PATIENT_GETALL = "___"
URL_PATIENT_GETBYPDS = "___"
URL____ACCOUNT_GET = "___"
URL_SUBSCRIPTION_GETBYPATIENT = "___"
URL_PRESCRIPTION_GETBY___ACCOUNTID = "___"
URL_CARTRIDGES_GETALL = "___"
URL_DELIVERY_GETBY___ACCOUNTID = "___"
URL____STATE_GETALLFOR___ACCOUNTID = "___"
URL_TUBEVOLUME_GETBY___ACCOUNTID = "___"
URL____STATE_GETALLFORPHYSICAL___ = "___"
URL_PRESCRIPTION_GETBY___ACCOUNTID = "___"


PATIENT_INCLUDE_PARTIAL = ["___"]
TEST_ACCOUNTS = ["_________"]


sep = ";"
lb = "\n"

class AdminApiSeesion():
    def __init__(self) -> None:
        #Create session to store authentication cookies
        self.session = requests.Session()
        #Authenticate using admin account identifiers
        with open("./accountAuthenticationInfo.json", "r") as loginFile:
            LOGIN_INFO = json.load(loginFile)
            r = self.session.post(URL_LOGIN, data=LOGIN_INFO)

    def get(self, address, params = {}):
        tries = 3
        while tries > 0:
            try:
                return self.session.get(address, params=params).json()
            except:
                tries -= 1
                time.sleep(1)
        raise "hell"

    def post(self, address, params = {}):
        tries = 3
        while tries > 0:
            try:        
                return self.session.post(address, data=params).json()
            except:
                tries -= 1
                time.sleep(1)
        raise "hell"
        
class PdsProfile():
    def __init__(self, session, pdsProfile) -> None:
        #get pds info (name)
        self.pdsPersonnalProfile = session.get(URL_PATIENT_GET, params={"id": pdsProfile["___"]})["___"]
        if(self.pdsPersonnalProfile == None):
            return
        self.pdsName = self.pdsPersonnalProfile["___"].title()  + " " + self.pdsPersonnalProfile["___"].title() 
        self.isClient = "Non"
        subscriptionInfo = session.get(URL_SUBSCRIPTION_GETBYPATIENT, params={"___": pdsProfile["___"]})
        if len(subscriptionInfo)>0 and "status" in subscriptionInfo[0]:
            self.isClient = "Oui"

        # get pds patient list
        self.patientList = []
        self.patientList = session.get(URL_PATIENT_GETBYPDS, params={"id": pdsProfile["___"]})

        #create file for export
        self.fileNameHtml = "./recaps/recap_pds_" + self.pdsPersonnalProfile["___"]  + "_" + self.pdsPersonnalProfile["___"] + "_" + datetime.date.today().strftime("%Y-%m-%d") + ".html" 
        self.fileNamePdf = "./recaps/recap_pds_" + self.pdsPersonnalProfile["___"]  + "_" + self.pdsPersonnalProfile["___"] + "_" + datetime.date.today().strftime("%Y-%m-%d") + ".pdf" 
        self.recapWorkSheet = self.excelFile.add_worksheet("recap")


# convenience class to create matplotlib graph and store them in a file to use later for the pdf creation
class GraphFormatter():
    def __init__(self) -> None:
        self.histogramColorMorning = "#25a6d9"
        self.histogramColorEvening = "#0f70b7"
        self.histogramColorLine = "#585858"
        self.fontName = "Calibri"
        self.fontColor = "#5F676D"
        self.fontSize = 12
        self.titleFontSize = 15


    def createHistogramFromObservance(self, pdsName, patientName, category, observanceData):
        if category.find("Mensuelle") != -1:
            xlabel = "MOIS"
        else:
            xlabel = "SEMAINE"
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_axes([0.15, 0.15, 0.8, 0.75]) 
        ax.grid(axis='y', color = self.fontColor)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(self.fontColor)
        ax.tick_params(axis = "x", colors=self.fontColor, labelsize = "15")
        ax.tick_params(axis = "y", colors=self.fontColor, labelsize = "15")
        ax.set_xlabel(xlabel, color=self.fontColor, fontname="Calibri", fontsize = "16", fontweight="bold")
        ax.set_ylabel('OBSERVANCE (%)', color=self.fontColor, fontname="Calibri", fontsize = "16", fontweight="bold")
        # ax.set_title('Observance '+category+' - '+patientName, color=self.fontColor, y = 1.13, fontname="Calibri", fontsize = "20")
        
        times = observanceData.keys()
        morning = [observanceData[time]["MORNING"] for time in times]
        evening = [observanceData[time]["EVENING"] for time in times]
        X = np.arange(len(times))
        morningSeries = ax.bar(X + 0.00, morning, color = self.histogramColorMorning, width = 0.25)
        eveningSeries = ax.bar(X + 0.25, evening, color = self.histogramColorEvening, width = 0.25)
        horizontalLine = ax.plot([-1, len(times)], [100, 100], color = self.histogramColorLine, linewidth = 2)
        plt.xticks(X + 0.125, times, color=self.fontColor)
        plt.ylim([0, 1.05*max(100, max(morning), max(evening))])
        plt.xlim([-0.5, len(times)-0.5])

        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.y0*0.25,
                        box.width, box.height * 1])
        ax.legend([morningSeries, eveningSeries, horizontalLine[0]],
            ["Observance Matin", "Observance Soir", "100%"],
            loc='upper center', bbox_to_anchor=(0.5, 1.10), ncol=3,
            fontsize = "14", labelcolor = self.fontColor, frameon=False)
        imagePath = "figures/"+pdsName+"_"+patientName+".png"
        fileName = "./recaps/" + imagePath
        fig.savefig(fileName)
        return imagePath
        
        
        
# format the user report using HTML then export to pdf format
class HtmlExport():
    def __init__(self) -> None:
        pass

    def generateHtmlRecap(self, pdsName, fileNameHtml, fileNamePdf, pdsRecapDict, patientInfoDataFrame, patientHtmlDataDict):
        patientInfoDataFrame = patientInfoDataFrame.sort_values("Date d'inscription", ignore_index=1)

        a = Airium()

        a('<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">')
        with a.html():
            with a.head():
                a.title(_t='Bilan PDS ' + pdsName)
                a.link(href='styling/recapStyling.css', rel='stylesheet')
                a.meta(charset="utf-8")
            with a.body():
                with a.div(klass='page'):
                    a.p(klass="bold", _t='Bonjour '+pdsName+', voici le bilan de vos patients au '+datetime.date.today().strftime("%Y-%m-%d")+':')
                    a.br()
                    with a.table(klass='recapPatients'):
                        with a.tr(klass='firstRow', height="80px"):
                            a.td(klass='italic', _t='Patient')
                            a.td(klass='italic', _t="Inscription")
                            a.td(klass='italic', _t='Début de cure')
                            a.td(klass='italic', _t='Fin de cure')
                            a.td(klass='italic', _t="Durée de cure")
                            a.td(klass='italic', _t='Observance </br> (Matin)')
                            a.td(klass='italic', _t='Observance </br> (Soir)')
                        currentCellClass = "normal"
                        for i in range(patientInfoDataFrame["Nom"].size):
                            if patientInfoDataFrame["Date d'inscription"].iloc[i] == "-":
                                continue               
                            if patientInfoDataFrame["Date de début de cure"].iloc[i] == "-" and (datetime.datetime.today() - datetime.datetime.strptime(patientInfoDataFrame["Date d'inscription"].iloc[i], "%Y-%m-%d") > datetime.timedelta(weeks=12)):
                                continue
                            with a.tr(klass="row", height="60px"):
                                if patientInfoDataFrame["Etat"].iloc[i] == "En cure":
                                    currentCellClass = "bold"
                                else:
                                    currentCellClass = "light"
                                a.td(klass=currentCellClass, _t=patientInfoDataFrame["Nom"].iloc[i])

                                if patientInfoDataFrame["Etat"].iloc[i] == "En cure":
                                    currentCellClass = "normal"
                                else:
                                    currentCellClass = "light"
                                a.td(klass=currentCellClass, _t=datetime.datetime.strptime(patientInfoDataFrame["Date d'inscription"].iloc[i], "%Y-%m-%d").strftime("%d.%m.%y")  )
                                if patientInfoDataFrame["Date de début de cure"].iloc[i] != "-":
                                    a.td(klass=currentCellClass, _t=datetime.datetime.strptime(patientInfoDataFrame["Date de début de cure"].iloc[i], "%Y-%m-%d").strftime("%d.%m.%y") )
                                else:
                                    a.td(klass=currentCellClass, _t=patientInfoDataFrame["Date de début de cure"].iloc[i])
                                a.td(klass=currentCellClass, _t=patientInfoDataFrame["Fin de cure"].iloc[i])
                                a.td(klass=currentCellClass, _t=patientInfoDataFrame["Durée de cure"].iloc[i])
                                a.td(klass=currentCellClass, _t=patientInfoDataFrame["Observance moyenne récente (Matin)"].iloc[i])
                                a.td(klass=currentCellClass, _t=patientInfoDataFrame["Observance moyenne récente (Soir)"].iloc[i])
                    
                    a.br()
                    with a.p(klass="bold"):
                        a("Cures en cours: ")
                        a.span(klass="patientName", _t=len(patientHtmlDataDict))
                
                for i in range(patientInfoDataFrame["___AccountId"].size):
                    userId = patientInfoDataFrame["___AccountId"].iloc[i]
                    if userId not in patientHtmlDataDict:
                        continue
                # for userId in patientHtmlDataDict:
                    with a.div(klass='pageEnd'):
                        with a.p(klass="bold"):
                            if pdsName == patientHtmlDataDict[userId]["name"]:
                                a("Votre bilan:")
                            else:
                                a("Votre patient(e): ")
                                a.span(klass="patientName", _t=patientHtmlDataDict[userId]["name"])
                        a.br()
                        a.p(klass="bold", _t="Programme micronutritionnel en cours :")

                        with a.table(klass="prescriptionPatient"):
                            with a.tr(height="40px"):
                                a.td()
                                a.td(klass="blueBold", _t="___", width="180px")
                                a.td(klass="heavyBlueBold", _t="___", width="180px")
                                a.td(klass="yellowBold", _t="Libre", width="180px")
                            for cartridge in patientHtmlDataDict[userId]["prescription"]:
                                with a.tr(height="55px"):
                                    a.td(klass="normalBorder",_t=cartridge)
                                    for mode in ["___", "___", "Libre"]:
                                        dose = ""
                                        if mode not in patientHtmlDataDict[userId]["prescription"][cartridge]:
                                            dose = ""
                                        else:
                                            if patientHtmlDataDict[userId]["prescription"][cartridge][mode] > 0:
                                                dose = str(patientHtmlDataDict[userId]["prescription"][cartridge][mode])
                                        a.td(klass="normalBorderCentered",_t=dose)
                        a.br()
                        a.br()
                        a.br()
                        a.p(klass="bold", _t="Observance mensuelle:")
                        with a.div():
                            a.img(klass="graph", src=patientHtmlDataDict[userId]["graphImagePath"])


                        
        with open(fileNameHtml, "w") as fp:
            fp.write(str(a))

        options = {
            'page-size':'A4',
            'encoding':'utf-8', 
            'margin-top':'0',
            'margin-bottom':'0',
            'margin-left':'0',
            'margin-right':'0',
            'disable-smart-shrinking': '',
            "dpi" : 600,
            'user-style-sheet' : "../pdsNewsletter/recaps/styling/recapStyling.css"
        }
        pdfkit.from_file(fileNameHtml, fileNamePdf, options=options)



def main():
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
    # Create session for authentication (token stored in session)
    session = AdminApiSeesion()


    # # Get cartridge information
    cartridgeInfo = session.get(URL_CARTRIDGES_GETALL)
    cartridgeIdToNameDict = {}
    cartridgeNameToIdDict = {}
    for cartridgeDict in cartridgeInfo:
        cartridgeIdToNameDict[cartridgeDict["refillId"]] = cartridgeDict["refillName"]
        cartridgeNameToIdDict[cartridgeDict["refillName"]] = cartridgeDict["refillId"]
    cartridgeIdToNameDict["Aroma"] = "Aromatisation pêche"
    cartridgeNameToIdDict["Aromatisation pêche"] = "Aroma"


    nbRecoTotal = 0
    nbSubsTotal = 0
    nbActiveSubsTotal = 0
    nbCancelTotal = 0
    nbCurePdsTotal = 0
    allPatientsObservances = {}

    graphFormatter = GraphFormatter()
    htmlFormatter = HtmlExport()

    # Get the list of all pds
    pdsArray = session.get(URL_PDS_GETALL)

    #For each pds
    for pds in pdsArray:
        patientInfoDict = []

        pdsInfoClass = PdsProfile(session, pds)
        if(pdsInfoClass.pdsPersonnalProfile == None):
            continue
        print(pdsInfoClass.pdsName)

        if len( pdsInfoClass.patientList) <= 1:
            continue

        patientHtmlDataDict = {}

        if(pdsInfoClass.isClient == "Oui"):
            nbCurePdsTotal += 1

        #For each patient of the pds
        for patientProfile in pdsInfoClass.patientList:
            patientDataAnalyser = DataAnalyserForUser(session, cartridgeIdToNameDict, patientProfile)
            if( patientDataAnalyser.___AccountId == None or patientDataAnalyser.___AccountId in TEST_ACCOUNTS):
                print("test patient, skipping")
                continue
            patientInfoDict.append({"Nom" : patientDataAnalyser.patientName, 
                                    "___AccountId" : patientDataAnalyser.___AccountId,
                                    "Date d'inscription" : patientDataAnalyser.inscriptionDate, 
                                    "Date de début de cure" : patientDataAnalyser.validationDate, 
                                    "Etat" : patientDataAnalyser.status, 
                                    "Fin de cure" : patientDataAnalyser.endDate,
                                    "Durée de cure" : patientDataAnalyser.cureDuration,
                                    "Date de modification" : patientDataAnalyser.lastModificationDate,
                                    "Observance moyenne récente (Matin)" : "-",
                                    "Observance moyenne récente (Soir)" : "-"
                                    })
            if(patientDataAnalyser.deliveriesForUserDataFrame.size < 1): # no deliveries for patient are found
                continue

            sheetName = "Obs_" + patientDataAnalyser.patientFirstName + "_" + patientDataAnalyser.patientLastName
            sheetName = sheetName.replace(" ", "")
            if len(sheetName)>30:
                sheetName = sheetName[:30]
            clientSheet = pdsInfoClass.excelFile.add_worksheet(sheetName)  #create new sheet in excel for patient
            clientSheet.hide_gridlines(2)

             #get observance by month
            observanceByMonth = patientDataAnalyser.getMonthlyObservanceDataForUser()

            if patientDataAnalyser.status == "En cure":
                patientHtmlDataDict[patientDataAnalyser.___AccountId] = {}
                patientHtmlDataDict[patientDataAnalyser.___AccountId]["name"] = patientDataAnalyser.patientName
                patientHtmlDataDict[patientDataAnalyser.___AccountId]["prescription"] = patientDataAnalyser.prescription
                patientHtmlDataDict[patientDataAnalyser.___AccountId]["graphImagePath"] = graphFormatter.createHistogramFromObservance(pdsInfoClass.pdsName, patientDataAnalyser.patientName, "Mensuelle", observanceByMonth)

            outputFormatter.addHistogramToFile(pdsInfoClass.excelFile, clientSheet, patientDataAnalyser.patientName, 1, "Mensuelle", observanceByMonth)

            #create histogram for observance by week
            observanceByWeek = patientDataAnalyser.getWeeklyObservanceForUser()   
            outputFormatter.addHistogramToFile(pdsInfoClass.excelFile, clientSheet, patientDataAnalyser.patientName, 12 + len(observanceByMonth), "Hebdomadaire", observanceByWeek)

            # add data for global observance
            if len(observanceByWeek) > 0:
                meanObservanceForPatient = {"MORNING" : 0, "EVENING" : 0}
                for week in observanceByWeek:
                    meanObservanceForPatient["MORNING"] += observanceByWeek[week]["MORNING"]
                    meanObservanceForPatient["EVENING"] += observanceByWeek[week]["EVENING"]
                meanObservanceForPatient["MORNING"] /= len(observanceByWeek)
                meanObservanceForPatient["EVENING"] /= len(observanceByWeek)      
                allPatientsObservances[patientDataAnalyser.patientName] = meanObservanceForPatient
                (patientInfoDict[-1]["Observance moyenne récente (Matin)"], patientInfoDict[-1]["Observance moyenne récente (Soir)"]) = patientDataAnalyser.getMeanRecentObservances(observanceByWeek)

            # Get cartridge use by cure
            cartridgeUseByCure = patientDataAnalyser.getCartridgeUseByCureForPatient()
            outputFormatter.addCartridgeUseChartToFile(pdsInfoClass.excelFile, clientSheet, patientDataAnalyser.patientName, 22 + len(observanceByMonth) + len(observanceByWeek), cartridgeUseByCure)

        # concatenate all patients info in dataframe
        patientInfoDataFrame = pd.DataFrame.from_dict(patientInfoDict, orient='columns')
        print("\nPds : " + pdsInfoClass.pdsPersonnalProfile["___"]  + " " + pdsInfoClass.pdsPersonnalProfile["___"])
        print("Is client : " + pdsInfoClass.isClient)
        print("Number of recommandations : " + str(len(patientInfoDataFrame)))
        print("Number of subscriptions : " + str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] != "-"])))
        print("Number of active subscriptions : " + str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "En cure"])))
        print("Number of cancelled subscriptions : " + str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "Arrêt de cure"])))
        print(patientInfoDataFrame)

        # add global data
        nbRecoTotal += len(patientInfoDataFrame)
        nbSubsTotal += len(patientInfoDataFrame[patientInfoDataFrame["Etat"] != "-"])
        nbActiveSubsTotal += len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "En cure"])
        nbCancelTotal += len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "Arrêt de cure"])


        pdsRecapDict = {"PDS" : pdsInfoClass.pdsName, "Statut" : "Actif", "Cure personnelle" :  pdsInfoClass.isClient, "Nb de Recommandations" : str(len(patientInfoDataFrame)), 
            "Nb de Souscriptions" : str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] != "-"])), 
            "Nb de patients en cure": str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "En cure"])), 
            "Arrêts de cure" : str(len(patientInfoDataFrame[patientInfoDataFrame["Etat"] == "Arrêt de cure"])) }


        htmlFormatter.generateHtmlRecap(pdsInfoClass.pdsName, pdsInfoClass.fileNameHtml, pdsInfoClass.fileNamePdf, pdsRecapDict, patientInfoDataFrame, patientHtmlDataDict)

    print("Observance for all patients")
    pprint.pprint(allPatientsObservances)
    globalObs = {"MORNING" : 0, "EVENING" : 0}
    for patient in allPatientsObservances:
        globalObs["MORNING"] += allPatientsObservances[patient]["MORNING"]
        globalObs["EVENING"] += allPatientsObservances[patient]["EVENING"]
    globalObs["MORNING"] /= len(allPatientsObservances)
    globalObs["EVENING"] /= len(allPatientsObservances)
    print("Mean global Observance : ", globalObs)


    # create global recap file
    fileName = "./recap_pds_global_" + datetime.date.today().strftime("%Y-%m-%d") + ".csv"
    with open(fileName, "w") as recapFile:
        recapFile.write("Bilan des recommmandations" +lb)
        recapFile.write("Date"+sep+"Cure PDS"+sep+"Nb de Recommmandations"+sep+"Nb de souscription de cures Totales"+sep+"Nb d'abonnements en cours"+sep+"Nb d'arrets de cures"+sep+"\% de souscriptions de cure globale" + sep + "\% de commandes en cours"+lb)
        recapFile.write(datetime.date.today().strftime("%d/%m/%Y") +sep+ str(nbCurePdsTotal) +sep+ str(nbRecoTotal) +sep+ str(nbSubsTotal) +sep+ str(nbActiveSubsTotal) +sep+ str(nbCancelTotal) +sep+ str(nbSubsTotal/nbRecoTotal*100) +sep+ str(nbActiveSubsTotal/nbRecoTotal*100) +lb)


class DataAnalyserForUser():
    def __init__(self, session, cartridgeIdToNameDict, patientProfile) -> None:
        self.session = session
        self.cartridgeIdToNameDict = cartridgeIdToNameDict

                # get patient name
        self.patientProfile = patientProfile
        self.patientFirstName = patientProfile["___"]
        self.patientLastName = patientProfile["___"]
        print(self.patientFirstName + " " + self.patientLastName)
        self.lastModificationDate = "-"
        self.inscriptionDate = "-"
        self.validationDate = "-"
        self.endDate = "-"
        self.cureDuration = "-"
        self.___AccountId = None
        #get patient inscription date (account creation) and validation date (first ___ use)
        if "___" in patientProfile:
            self.inscriptionDate = datetime.datetime.from___(patientProfile["___"]).strftime("%Y-%m-%d") 
        if "___" in patientProfile:
            self.___AccountId = patientProfile["___"]
            ___Account  = session.get(URL____ACCOUNT_GET, params={"id": self.___AccountId})
            
        if( self.___AccountId == None or self.___AccountId in TEST_ACCOUNTS): # don't get info for test patient since they are skipped in the analysis
            return
                    
        #get patient subscription info (active, cancelled ...)
        subscriptionInfo = session.get(URL_SUBSCRIPTION_GETBYPATIENT, params={"___": patientProfile["___"]})
        if len(subscriptionInfo)>0 and "status" in subscriptionInfo[-1]:
            self.status = subscriptionInfo[-1]["status"]
            if self.status == "active":
                self.status = "En cure"
            elif self.status == "canceled":
                self.status = "Arrêt de cure"
            elif self.status == "requestedCancellation":
                self.status = "Arrêt demandé"
        else:
            self.status = "-"

        if "___" in ___Account:
            self.validationDate = datetime.datetime.strptime(___Account["___"], "%Y-%m-%d").strftime("%Y-%m-%d")
            if self.status == "En cure":
                self.endDate = "En cure"
                self.cureDuration = self.formatCureDuration(datetime.datetime.strptime(self.validationDate, "%Y-%m-%d"), datetime.datetime.today())
                self.lastModificationDate = self.getLastModificationDateForUser()
                tempPrescription = session.get(URL_PRESCRIPTION_GETBY___ACCOUNTID, params={"id": self.___AccountId})[-1]["___"]
                self.prescription = {}
                for i in range(len(tempPrescription)):
                    cartridgeName = self.cartridgeIdToNameDict[tempPrescription[i]["___"]]
                    self.prescription[cartridgeName] = {}
                    for j in range(len(tempPrescription[i]["___"])):
                        ___ = tempPrescription[i]["___"][j]["___"]
                        self.prescription[cartridgeName][___] = tempPrescription[i]["___"][j]["___"]
            elif self.status == "Arrêt de cure" or self.status == "Arrêt demandé":
                self.endDate = self.getEndDateForUser()
                self.cureDuration = self.formatCureDuration(datetime.datetime.strptime(self.validationDate, "%Y-%m-%d"), datetime.datetime.strptime(self.endDate, "%d.%m.%y"))



        self.patientName = (self.patientFirstName + " " + self.patientLastName).title()

        if self.___AccountId == None:
            self.deliveriesForUserDataFrame = pd.DataFrame()
            return

        # get delivery history for user
        self.deliveriesForUserDataFrame = self.getDeliveriesForUser()
        # print(self.deliveriesForUserDataFrame)

        # get activity history for user
        self.activityForUserDataFrame = self.getDaysOfActivityForUser()

    def formatCureDuration(self, startCure, endCure):
        timeDelta = dateutil.relativedelta.relativedelta(endCure, startCure)
        years = int(timeDelta.years)
        months = int(timeDelta.months)
        string = ""
        if years == 0:
            if months == 0:
                string = str(timeDelta.weeks) + " semaines"
            else:
                string = str(months)  + " mois"
        elif years == 1:
            if months == 0:
                string = "1 an"
            else:
                string = "1 an " + str(months) + " mois"
        else: 
            if months == 0:
                string = str(years) + " ans"
            else:
                string = str(years) + " ans " + str(months) + " mois"    
        return string


    def getDaysOfActivityForUser(self):
        daysOfActivityDatabase = pd.DataFrame(columns=["user", "___", "___"])

        # Get the tube-volume history
        tubeVolumesForUser = self.session.get(URL_TUBEVOLUME_GETBY___ACCOUNTID, params={"id" : self.___AccountId})
        if(len(tubeVolumesForUser) == 0):
            return daysOfActivityDatabase
        tubeVolumesForUser = sorted(tubeVolumesForUser, key=lambda d: d['___']) 

        #Creates an history of ___ for the ___AccountId, by keeping one entry (___, ___) for each ___ in the list
        ___History = []
        for tubeVolumeEntry in tubeVolumesForUser:
            if len(___History) == 0 or tubeVolumeEntry["___"] != ___History[-1]["___"]:
                ___History.append( {"___" : tubeVolumeEntry["___"], "___" :  tubeVolumeEntry["___"]} )
        
        # print(___History)
        cure = self.session.get(URL_PRESCRIPTION_GETBY___ACCOUNTID, params={"id" : self.___AccountId})[-1]
        if "___" in cure:
            lastDayOfCure = datetime.datetime.strptime(cure["___"], "%Y-%m-%d")
        else:
            lastDayOfCure = datetime.datetime.now()

        # For each ___ in the ___ history
        for i in range(len(___History)):
            # Get the ___-state history for the ___ and sort by date
            ___StateHistoryComplete = self.session.get( URL____STATE_GETALLFORPHYSICAL___, params={"id" : ___History[i]["___"]})
            ___StateHistoryComplete = sorted(___StateHistoryComplete, key=lambda d: d['___']) 

            # Only keep entries that are in the ___ use period for this account
            lastDayStored = datetime.datetime(year=1900, month=1, day=1)
            for ___State in ___StateHistoryComplete:
                if ___State["___"] < ___History[i]["___"]: # Entry before period of use, continue
                    continue
                if i < len(___History) - 1 and ___State["___"] > ___History[i+1]["___"]: # Entry after period of use, stop
                    break

                activityDate = datetime.datetime.from___(___State["___"])
                if(activityDate > lastDayOfCure): #Entry after last day of cure for user, stop
                    break

                # entry in period, keep
                # check if day alreay in the dataframe
                if activityDate.day == lastDayStored.day and activityDate.month == lastDayStored.month and activityDate.month == lastDayStored.month:
                    continue
                else: #if new day, add a row in the dataframe
                    lastDayStored = activityDate
                    newRow = pd.DataFrame({"___" : ___History[i]["___"][:___History[i]["___"].find("-")], "user" : self.___AccountId, "___" : lastDayStored.strftime("%Y-%m-%d")}, index=[0])
                    daysOfActivityDatabase = pd.concat([daysOfActivityDatabase.loc[:], newRow])

        daysOfActivityDatabase = daysOfActivityDatabase.reset_index(drop=True)
        return daysOfActivityDatabase

    def getDeliveriesForUser(self):
        deliveriesFromDataBaseForUser = self.session.get(URL_DELIVERY_GETBY___ACCOUNTID, params={"id": self.___AccountId})
        deliveriesFromDataBaseForUser = sorted(deliveriesFromDataBaseForUser, key=lambda d: d['___']) 
        for i in reversed(range(len(deliveriesFromDataBaseForUser))):
            delivery = deliveriesFromDataBaseForUser[i-1]
            delivery["___"] = datetime.datetime.from___(delivery["___"]).strftime("%Y-%m-%d.%H:%M:%S:%f")
            # deliveryDate = datetime.datetime.from___(delivery["___"])
            if "___" not in delivery:
                deliveriesFromDataBaseForUser.pop(i-1)
                continue
            deliveryMode = delivery["___"]
            if (deliveryMode != "___" and deliveryMode != "___"):
                deliveriesFromDataBaseForUser.pop(i-1)
                continue
            if delivery["___"] != "success" and self.___AccountId not in PATIENT_INCLUDE_PARTIAL:
                deliveriesFromDataBaseForUser.pop(i-1)
                continue   
        deliveriesFromDataBaseForUser = pd.DataFrame.from_dict(deliveriesFromDataBaseForUser)
        return deliveriesFromDataBaseForUser

        
    def getObservanceForUserForDay(self, day, index = 0):
        # Search in combined deliveries dataframe for a delivery on this day
        startOfDay = datetime.datetime(year = day.year, month = day.month, day = day.day, hour = 0, minute = 0, second= 0)
        endOfDay = datetime.datetime(year = day.year, month = day.month, day = day.day, hour = 23, minute = 59, second= 59)
        numberOfDeliveriesMorning = 0
        numberOfDeliveriesEvening = 0
        activityForDay = 0

        if( index >= self.deliveriesForUserDataFrame["___"].size or index < 0):
            raise( "Index out of range for deliveries dataframe")

        for i in range(index, self.deliveriesForUserDataFrame["___"].size):
            delivery = self.deliveriesForUserDataFrame.iloc[i]
            deliveryDate = datetime.datetime.strptime(delivery["___"], "%Y-%m-%d.%H:%M:%S:%f")
            if deliveryDate <= startOfDay: # deliveries too early
                continue
            elif deliveryDate > endOfDay: #reached next day
                break                
                
            # discard failed deliveries
            if delivery["___"] != "success" and self.___AccountId not in PATIENT_INCLUDE_PARTIAL:
                continue

            # increment number of deliveries if delivery was successful and in the right day
            # do not discriminate between trip kits and normal deliveries for now
            if delivery["___"] == "___":
                numberOfDeliveriesMorning += 1
            elif delivery["___"] == "___":
                numberOfDeliveriesEvening += 1

        # At least one delivery, return number of deliveries and set activity count to 1
        if numberOfDeliveriesMorning+numberOfDeliveriesEvening > 0:
            activityForDay = 1
            return i-1, numberOfDeliveriesMorning, numberOfDeliveriesEvening, activityForDay

        # If no delivery, search for activity in ___ log recap
        dayString = day.strftime("%Y-%m-%d")
        for d in range(self.activityForUserDataFrame["___"].size):
            # If activity in log, add 1 to activity count
            if(dayString == self.activityForUserDataFrame.iloc[d]["___"]):
                activityForDay = 1
                return i-1, numberOfDeliveriesMorning, numberOfDeliveriesEvening, activityForDay

        # If no activity, returns 0 for all
        return i-1, 0, 0, 0
        


        
    def getMonthlyObservanceDataForUser(self):
        if(self.deliveriesForUserDataFrame.size < 1):
            return "Patient id not found in delivery data"
                    
        firstDeliveryDate = datetime.datetime.strptime(self.deliveriesForUserDataFrame["___"].iloc[0], "%Y-%m-%d.%H:%M:%S:%f")
        lastDayOfMonth = self.getLastDayOfMonth(firstDeliveryDate)
        numberOfDeliveriesMorning = 0
        numberOfDeliveriesEvening = 0
        observanceByMonth = {}
        numberOfDaysActive = 0
        numberOfDaysTotal = 0
        lastDayOfActivity = datetime.datetime.strptime(self.activityForUserDataFrame["___"].iloc[-1], "%Y-%m-%d")
        
        day = firstDeliveryDate
        lastIndexInDeliveryDataFrame = 0
        while day <= lastDayOfActivity:   
            if(day >lastDayOfMonth or day.date() >= (lastDayOfActivity + datetime.timedelta(hours=-1)).date()): 
                if(numberOfDaysActive == 0):
                    observanceByMonth[lastDayOfMonth.strftime("%b -\n %Y")] = {"MORNING": 0, "EVENING" : 0}
                else:
                    observanceByMonth[lastDayOfMonth.strftime("%b -\n %Y")] = {"MORNING": round(numberOfDeliveriesMorning/numberOfDaysActive*100, 1), "EVENING" : round(numberOfDeliveriesEvening/numberOfDaysActive*100, 1)}
                numberOfDeliveriesMorning = 0
                numberOfDeliveriesEvening = 0  
                numberOfDaysActive = 0
                lastDayOfMonth = self.getLastDayOfMonth(lastDayOfMonth + datetime.timedelta(days=1)) 

            (lastIndexInDeliveryDataFrame, dailyObservanceMorning, dailyObservanceEvening, activityForDay) = self.getObservanceForUserForDay(day, lastIndexInDeliveryDataFrame)
            numberOfDeliveriesMorning += dailyObservanceMorning
            numberOfDeliveriesEvening += dailyObservanceEvening
            numberOfDaysActive += activityForDay
            numberOfDaysTotal += 1
            day = day + datetime.timedelta(days=1)

        return observanceByMonth

    def getLastDayOfMonth(self, date):
        if date.month == 12:
            return date.replace(day=31, hour=23, minute=59)
        return date.replace(month=date.month+1, day=1, hour=23, minute=59) - datetime.timedelta(days=1)

    def getWeeklyObservanceForUser(self):
        if(self.deliveriesForUserDataFrame.size < 1):
            return "Patient id not found in delivery data"
                    
        firstDeliveryDate = datetime.datetime.strptime(self.deliveriesForUserDataFrame["___"].iloc[0], "%Y-%m-%d.%H:%M:%S:%f")
        lastDayOfWeek = self.getLastDayOfWeek(firstDeliveryDate)
        numberOfDeliveriesMorning = 0
        numberOfDeliveriesEvening = 0
        observanceByWeek = {}
        numberOfDaysActive = 0
        numberOfDaysTotal = 0
        lastDayOfActivity = datetime.datetime.strptime(self.activityForUserDataFrame["___"].iloc[-1], "%Y-%m-%d")
        
        day = firstDeliveryDate
        lastIndexInDeliveryDataFrame = 0
        while day <= lastDayOfActivity:
            if(day >lastDayOfWeek or day.date() >= (lastDayOfActivity + datetime.timedelta(hours=-1)).date()): 
                if(numberOfDaysActive == 0):
                    observanceByWeek["S" + str(lastDayOfWeek.isocalendar()[1]) + " -\n" + lastDayOfWeek.strftime("%Y")] = {"MORNING": 0, "EVENING" : 0}
                else:
                    observanceByWeek["S" + str(lastDayOfWeek.isocalendar()[1]) + " -\n" + lastDayOfWeek.strftime("%Y")] = {"MORNING": round(numberOfDeliveriesMorning/numberOfDaysActive*100, 1), "EVENING" : round(numberOfDeliveriesEvening/numberOfDaysActive*100, 1)}
                numberOfDeliveriesMorning = 0
                numberOfDeliveriesEvening = 0  
                numberOfDaysActive = 0
                lastDayOfWeek = self.getLastDayOfWeek(lastDayOfWeek + datetime.timedelta(days=1)) 

            (lastIndexInDeliveryDataFrame, dailyObservanceMorning, dailyObservanceEvening, activityForDay) = self.getObservanceForUserForDay(day, lastIndexInDeliveryDataFrame)
            numberOfDeliveriesMorning += dailyObservanceMorning
            numberOfDeliveriesEvening += dailyObservanceEvening
            numberOfDaysActive += activityForDay
            numberOfDaysTotal += 1
            day = day + datetime.timedelta(days=1)

        return observanceByWeek

    def getLastDayOfWeek(self, date):
        return date + datetime.timedelta(days=7-date.weekday()-1)


    def getCartridgeUseByCureForPatient(self):
        deliveriesForUser = self.session.get(URL_DELIVERY_GETBY___ACCOUNTID, params={"id": self.___AccountId})
        self.cartridgeIdToNameDict["VOID"] = "VOID"


        deliveriesForUser = sorted(deliveriesForUser, key=lambda d: d['___']) 
        for i in reversed(range(len(deliveriesForUser))):
            delivery = deliveriesForUser[i-1]
            deliveryDate = datetime.datetime.from___(delivery["___"])
            if "___" not in delivery:
                deliveriesForUser.pop(i-1)
                continue
            deliveryMode = delivery["___"]
            if (deliveryMode != "___" and deliveryMode != "___") or delivery["___"] != "success":
                deliveriesForUser.pop(i-1)
                continue

        cartridgeUsageByCure = {}
        numberOfDeliveriesForCure = {}
        prescriptionsForUser = self.session.get(URL_PRESCRIPTION_GETBY___ACCOUNTID, params={"id": self.___AccountId})
        lastPrescritpionId = ""
        curePeriodString = ""
        prescriptionForDelivery = {}
        cartridgesInCure = []
        for i in range(len(deliveriesForUser)):
            delivery = deliveriesForUser[i]
            deliveryDate = datetime.datetime.from___(delivery["___"])
            deliveryMode = delivery["___"]

            # Get correct prescription for the delivery
            for prescription in prescriptionsForUser: # for all prescription in cure for user
                prescriptionStartDate = datetime.datetime.strptime(prescription["___"], "%Y-%m-%d")
                if "___" in prescription:
                    prescriptionEndDate = datetime.datetime.strptime(prescription["___"], "%Y-%m-%d")
                else:
                    prescriptionEndDate = datetime.datetime.now()
                if prescriptionStartDate <= deliveryDate and deliveryDate < prescriptionEndDate: # correct prescription
                    if lastPrescritpionId != prescription["_id"]: # check if deliveries reached new prescription
                        if(lastPrescritpionId != ""): # not first iteration
                            for cartridgeInPrescription in cartridgesInCure: 
                                if numberOfDeliveriesForCure[cartridgeInPrescription] < 1:
                                    numberOfDeliveriesForCure[cartridgeInPrescription] = 1
                                cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]] = round(cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]]/numberOfDeliveriesForCure[cartridgeInPrescription]*100.,1)
                            numberOfDeliveriesForCure = {}
                        lastPrescritpionId = prescription["_id"]
                        curePeriodString = prescriptionStartDate.strftime("%Y-%m-%d") + " à " + prescriptionEndDate.strftime("%Y-%m-%d") 
                        cartridgeUsageByCure[curePeriodString] = {}
                        # print("\nnew period : " + curePeriodString)
                        cartridgesInCure = []

                    prescriptionForDelivery = {}
                    for cartridge in prescription["supplements"]: # get all cartridges in the prescription for the mode of the current delivery
                        cartridgeId = cartridge["cartridgeId"]
                        for mode in cartridge["modes"]:
                            if (mode["name"] == deliveryMode and mode["dose"] > 0):
                                prescriptionForDelivery[cartridgeId] = mode["dose"]
                    break


            for cartridgeInPrescription in prescriptionForDelivery.keys(): # for all cartridge that should be used
                if cartridgeInPrescription in cartridgesInCure: #increments number of expected uses for each cartridge
                    numberOfDeliveriesForCure[cartridgeInPrescription] += 1
                else:
                    numberOfDeliveriesForCure[cartridgeInPrescription] = 1

                if(self.cartridgeIdToNameDict[cartridgeInPrescription] not in cartridgeUsageByCure[curePeriodString]):
                    cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]] =0
                    cartridgesInCure.append(cartridgeInPrescription)
                cartridgeWasDetected = 0
                for cartridgeDelivered in delivery["deliveredSupplements"]:
                    if( cartridgeInPrescription == cartridgeDelivered["cartridgeId"]): # cartridge in prescription was in the ___
                        cartridgeWasDetected = 1
                        if (cartridgeDelivered["quantityDeliveredMl"] > 0): # cartridge in prescription was used
                            cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]] += 1
                        break  
                if cartridgeWasDetected == 0:
                    numberOfDeliveriesForCure[cartridgeInPrescription] -= 1 # Do not count if the cartridge wasn't physically detected in the ___     

            if i == len(deliveriesForUser) -1:
                for cartridgeInPrescription in cartridgesInCure: 
                    if numberOfDeliveriesForCure[cartridgeInPrescription] < 1:
                        numberOfDeliveriesForCure[cartridgeInPrescription] = 1
                    cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]] = round(cartridgeUsageByCure[curePeriodString][self.cartridgeIdToNameDict[cartridgeInPrescription]]/numberOfDeliveriesForCure[cartridgeInPrescription]*100.,1)
    
        return cartridgeUsageByCure

# get date of last prescription modification for user
    def getLastModificationDateForUser(self):
        prescriptionsForUser = self.session.get(URL_PRESCRIPTION_GETBY___ACCOUNTID, params={"id": self.___AccountId})
        prescriptionsForUser = sorted(prescriptionsForUser, key=lambda d: d['sequenceNumber']) 
        # Get correct prescription for the delivery
        if "___" in prescriptionsForUser[-1]:
            lastPrescriptionEndDate = datetime.datetime.strptime(prescriptionsForUser[-1]["___"], "%Y-%m-%d")
            lastModifDate = lastPrescriptionEndDate - datetime.timedelta(days=6)
            while lastModifDate <= datetime.datetime.now():
                lastModifDate = lastModifDate + dateutil.relativedelta.relativedelta(months=+1)
            lastModifDate = lastModifDate.strftime("%A %d %B %Y")
        else:
            lastModifDate = "-"
        return lastModifDate

# 
    def getEndDateForUser(self):
        prescriptionsForUser = self.session.get(URL_PRESCRIPTION_GETBY___ACCOUNTID, params={"id": self.___AccountId})
        prescriptionsForUser = sorted(prescriptionsForUser, key=lambda d: d['sequenceNumber']) 
        # Get correct prescription for the delivery
        if "___" in prescriptionsForUser[-1]:
            endDate = datetime.datetime.strptime(prescriptionsForUser[-1]["___"], "%Y-%m-%d").strftime("%d.%m.%y")
        else:
            endDate = "-"
        return endDate       

# return average observance for patient (morning and evening)
    def getMeanRecentObservances(self, observanceDataByWeek):
        obsMorning = 0
        obsEvening = 0
        i = 0
        for week in observanceDataByWeek:
            if i > len(observanceDataByWeek) - 13:
                obsMorning += observanceDataByWeek[week]["MORNING"]
                obsEvening += observanceDataByWeek[week]["EVENING"]
            i+=1

        obsMorning /= min(12, len(observanceDataByWeek))
        obsEvening /= min(12, len(observanceDataByWeek))
        return (round(obsMorning, 2), round(obsEvening,2))

if __name__ == "__main__":
    main()
        

