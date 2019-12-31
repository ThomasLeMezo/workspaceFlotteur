# -*- coding: utf-8 -*-°
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
from PyQt5.QtCore import pyqtSignal, QTimer, QFile, QFileInfo
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QTreeWidgetItem
from PyQt5.QtGui import QIcon

from seabot.src.seabotLayerLivePosition import SeabotLayerLivePosition
from seabot.src.boatLayerLivePosition import BoatLayerLivePosition
from seabot.src.seabotMission import *
from seabot.src.missionLayer import *
from seabot.src.seabotIridiumIMAP import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'seabot_dockwidget_base.ui'))

class SeabotDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    timer_seabot = QTimer()
    timer_boat = QTimer()
    timer_mission = QTimer()
    timer_IMAP = QTimer()
    flag = False
    count = 0

    layerLivePosition = SeabotLayerLivePosition()
    boatLivePosition = BoatLayerLivePosition()
    seabotMission = SeabotMission()
    missionLayer = MissionLayer()
    dataBaseConnection = DataBaseConnection()
    imapServer = ImapServer()

    def __init__(self, parent=None):
        """Constructor."""
        super(SeabotDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # print(self.__dir__)
        self.setupUi(self)

        ### Timer handle
        self.timer_seabot.timeout.connect(self.process_seabot)
        self.timer_seabot.setInterval(5000)

        self.timer_boat.timeout.connect(self.process_boat)
        self.timer_boat.setInterval(1000)

        self.timer_mission.timeout.connect(self.process_mission)
        self.timer_mission.setInterval(1000)

        self.timer_IMAP.timeout.connect(self.process_IMAP)
        self.timer_IMAP.setInterval(1000)

        ### UI pushButton handle

        self.pushButton_seabot.clicked.connect(self.enable_timer_seabot)
        self.pushButton_boat.clicked.connect(self.enable_timer_boat)
        self.pushButton_mission.clicked.connect(self.enable_timer_mission)

        self.pushButton_open_mission.clicked.connect(self.open_mission)

        self.pushButton_server_save.clicked.connect(self.server_save)
        self.pushButton_server_delete.clicked.connect(self.server_delete)
        self.comboBox_config_email.currentIndexChanged.connect(self.select_server)
        self.pushButton_server_connect.clicked.connect(self.server_connect)

        ## Init iridium data
        # self.treeWidget_iridium.setColumnCount(2)
        # tree = self.treeWidget_iridium.setHeaderLabels(["Parameter","Data"])
        # item = QTreeWidgetItem(tree)
        # item.setText(0, "IMEI")
        # item.setText(1, "10000")
        # item_sub = QTreeWidgetItem(item)
        # item_sub.setText(0, "Heading")
        # item_sub.setText(1, "10")
        # self.treeWidget_iridium.addTopLevelItem(item)
        # self.treeWidget_iridium.expandItem(item)
        # self.treeWidget_iridium.setHeaderLabel("Data")

        # Fill list of email account
        self.update_server_list()

    def server_save(self, event):
        email = self.lineEdit_email.text()
        password = self.lineEdit_password.text()
        server_ip = self.lineEdit_server_ip.text()
        server_port = self.lineEdit_server_port.text()
        self.dataBaseConnection.save_server(email, password, server_ip, server_port)
        self.update_server_list()
        return True

    def server_delete(self, event):
        id_config = self.comboBox_config_email.currentData()
        self.dataBaseConnection.delete_server(id_config)
        self.update_server_list()
        return True

    def update_server_list(self):
        self.comboBox_config_email.clear()
        email_list = self.dataBaseConnection.get_email_list()
        for email in email_list:
            self.comboBox_config_email.addItem(str(email["id"]) + " - " + email["email"], email["id"])

    def select_server(self, index):
        if index != -1:
            server_id = self.comboBox_config_email.currentData()
            server_data = self.dataBaseConnection.get_server_data(server_id)
            self.lineEdit_email.setText(server_data["email"])
            self.lineEdit_password.setText(server_data["password"])
            self.lineEdit_server_ip.setText(server_data["server_ip"])
            self.lineEdit_server_port.setText(server_data["server_port"])

    def open_mission(self, event):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Mission Files (*.xml);;All Files (*)", options=options)
        print("filename=", fileName)
        self.seabotMission.load_mission_xml(fileName)

        file_info = QFileInfo(fileName)
        self.label_mission_file.setText(file_info.fileName())
        self.missionLayer.update_mission_layer(self.seabotMission)

    def closeEvent(self, event):
        self.timer_seabot.stop()
        self.timer_boat.stop()
        self.timer_IMAP.stop()
        self.timer_mission.stop()

        self.imapServer.stop_server()

        self.pushButton_seabot.setChecked(False)
        self.closingPlugin.emit()
        event.accept()

    def set_enable_form_connect(self, enable):
        if(enable):
            self.comboBox_config_email.setEnabled(True)
            self.lineEdit_email.setEnabled(True)
            self.lineEdit_password.setEnabled(True)
            self.lineEdit_server_ip.setEnabled(True)
            self.lineEdit_server_port.setEnabled(True)
            self.pushButton_server_save.setEnabled(True)
            self.pushButton_server_delete.setEnabled(True)
        else:
            self.comboBox_config_email.setEnabled(False)
            self.lineEdit_email.setEnabled(False)
            self.lineEdit_password.setEnabled(False)
            self.lineEdit_server_ip.setEnabled(False)
            self.lineEdit_server_port.setEnabled(False)
            self.pushButton_server_save.setEnabled(False)
            self.pushButton_server_delete.setEnabled(False)

    ###########################################################################
    ### Handler Button

    def enable_timer_seabot(self):
        if(self.pushButton_seabot.isChecked()):
            self.timer_seabot.start()
        else:
            self.timer_seabot.stop()

    def enable_timer_boat(self):
        if(self.pushButton_boat.isChecked()):
            self.boatLivePosition.start()
            self.timer_boat.start()
        else:
            self.timer_boat.stop()
            self.boatLivePosition.stop()

    def enable_timer_mission(self):
        if(self.pushButton_mission.isChecked()):
            # self.boatLivePosition.start()
            self.timer_mission.start()
        else:
            self.timer_mission.stop()
            # self.boatLivePosition.stop()

    def server_connect(self):
        if(self.pushButton_server_connect.isChecked()):
            self.set_enable_form_connect(False)
            self.imapServer.set_server_id(self.comboBox_config_email.currentData())
            
            ## Thread IMAP
            self.imapServer.start_server()
            
            ## UI update
            self.timer_IMAP.start()
        else:
            self.set_enable_form_connect(True)
            self.label_server_log.setText("Disconnected")

            ## Thread IMAP
            self.imapServer.stop_server()
            self.timer_IMAP.stop()

    ###########################################################################
    ## TIMERS processing

    def process_seabot(self):
        if(self.layerLivePosition.update()):
            self.label_status.setText("Connected - " + str(self.count))
            self.count += 1
        else:
            self.label_status.setText("Error")
            self.count = 0

    def process_boat(self):
        self.boatLivePosition.update()

    def process_IMAP(self):
        self.label_server_log.setText(self.imapServer.get_log())
    
    def process_mission(self):
        # Update mission set point on map
        self.missionLayer.update_mission_set_point(self.seabotMission)

        # Update IHM with mission data set point
        wp = self.seabotMission.get_current_wp()
        # print(wp)
        if(wp!=None):
            if(wp.get_depth()==0.0):
                self.label_mission_status.setText("SURFACE")
            else:
                self.label_mission_status.setText("UNDERWATER")

            self.label_mission_start_time.setText(str(wp.get_time_start()))
            self.label_mission_end_time.setText(str(wp.get_time_end()))
            self.label_mission_depth.setText(str(wp.get_depth()))
            self.label_mission_waypoint_id.setText(str(wp.get_id())+"/"+str(self.seabotMission.get_nb_wp()))
            self.label_mission_time_remain.setText(str(wp.get_time_end()-datetime.datetime.now()))

            wp_next = self.seabotMission.get_next_wp()
            if(wp_next != None):
                self.label_mission_next_depth.setText(str(wp_next.get_depth()))
            else:
                self.label_mission_next_depth.setText("-")
        else:
            self.label_mission_status.setText("NO WAYPOINTS")
            self.label_mission_waypoint_id.setText(str(self.seabotMission.get_current_wp_id()+1) + "/"+str(self.seabotMission.get_nb_wp()))
