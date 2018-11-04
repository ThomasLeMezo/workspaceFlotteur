# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SeabotDockWidget
                                 A QGIS plugin
 Seabot
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-10-31
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Thomas Le Mézo
        email                : thomas.le_mezo@ensta-bretagne.org
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, time

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal, QTimer

from .seabotLayerLivePosition import SeabotLayerLivePosition

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'seabot_dockwidget_base.ui'))


class SeabotDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    timer = QTimer()
    flag = False
    count = 0

    layerLivePosition = SeabotLayerLivePosition()

    def __init__(self, parent=None):
        """Constructor."""
        super(SeabotDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        print(self.__dir__)
        self.setupUi(self)

        self.timer.timeout.connect(self.process)
        self.timer.setInterval(1000)
        # self.timer.start()

        self.pushButton.clicked.connect(self.enable_timer)

    def closeEvent(self, event):
        self.timer.stop()
        self.pushButton.setChecked(False)
        self.closingPlugin.emit()
        event.accept()

    def enable_timer(self):
        if(self.pushButton.isChecked()):
            self.timer.start()
        else:
            self.timer.stop()

    def process(self):
        if(self.layerLivePosition.update_position()):
            self.label.setText("Connected - " + str(self.count))
            self.count += 1
        else:
            self.label.setText("Error")
            self.count = 0
        