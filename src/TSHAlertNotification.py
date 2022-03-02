import unicodedata
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import requests
import os
import traceback
import json
import time


class TSHAlertNotificationSignals(QObject):
    alerts = pyqtSignal(object)


class TSHAlertNotification(QObject):
    instance: "TSHAlertNotification" = None

    def __init__(self) -> None:
        super().__init__()
        self.signals = TSHAlertNotificationSignals()
        self.signals.alerts.connect(self.ShowAlerts)

    def UiMounted(self):
        class AlertThread(QThread):
            def run(self):
                alerts = None

                try:
                    response = requests.get(
                        "https://raw.githubusercontent.com/joaorb64/TournamentStreamHelper/next/assets/alerts.json")
                    alerts = json.loads(response.text)
                except Exception as e:
                    print(traceback.format_exc())

                try:
                    alerts_red = json.load(
                        open('./assets/alerts_red.json', encoding='utf-8'))
                except Exception as e:
                    print(traceback.format_exc())

                filtered = {}

                if alerts is not None and alerts_red is not None:
                    for alertId, alert in alerts.items():
                        if alertId not in alerts_red:
                            if alert.get("dateStart", None):
                                if time.time() > alert.get("dateStart"):
                                    continue
                            if alert.get("dateEnd", None):
                                if time.time() > alert.get("dateEnd"):
                                    continue

                            filtered[alertId] = alert

                self.parent().signals.alerts.emit(filtered)

        thread = AlertThread(self)
        thread.start()

    def ShowAlerts(self, alerts):
        i = 1

        for alertId, alert in alerts.items():
            message = QDialog()
            message.setWindowModality(
                Qt.WindowModality.ApplicationModal)
            vbox = QVBoxLayout()
            message.setLayout(vbox)
            message.setWindowTitle(
                f"Notifications ({i}/{len(alerts.keys())})")
            message.layout().addWidget(QLabel(alert.get("alert")))

            hbox = QHBoxLayout()
            vbox.addLayout(hbox)

            btOk = QPushButton("OK")
            hbox.addWidget(btOk)
            btRemindLater = QPushButton("Remind later")
            hbox.addWidget(btRemindLater)

            message.setMinimumWidth(500)
            message.setMinimumHeight(200)

            btOk.clicked.connect(
                lambda: message.close())
            btRemindLater.clicked.connect(
                lambda: message.close())

            message.exec()

            i += 1


if not os.path.exists("./assets/alerts_red.json"):
    with open("./assets/alerts_red.json", 'w') as outfile:
        outfile.write("[]")

TSHAlertNotification.instance = TSHAlertNotification()
