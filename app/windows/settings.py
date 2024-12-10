# -*- coding: utf-8 -*-
#############################################################################
## Call-A-Ball: an open-source demonstrator of 3D object localization
## based on camera images and the geometric camera calibration,
## completed with the help of the Radiant Metrics cloud service.
##
## Copyright (C) 2024 HS High Stake GmbH
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program. If not, see <https://www.gnu.org/licenses/>.
##
## Contact: call-a-ball@high-stake.de
#############################################################################

import logging

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDialog, QDialogButtonBox
from PyQt6.uic import loadUi

from app.config.config import config
from app.components.labeled_slider_widget import LabeledSliderWidget

logger = logging.getLogger(__name__)


class SettingsWindow(QDialog):
    def __init__(self):
        logger.debug("__init__")
        super(SettingsWindow, self).__init__()

        self.widget_k_size = None
        self.widget_sigma_x = None
        self.widget_threshold_1 = None
        self.widget_threshold_2 = None
        self.widget_kernel = None
        self.widget_iterations = None
        self.widget_dp = None
        self.widget_min_dist = None
        self.widget_param_1 = None
        self.widget_param_2 = None
        self.widget_min_radius = None
        self.widget_max_radius = None

        loadUi("ui/settings.ui", self)

        self.button_box = self.findChild(QDialogButtonBox)
        self.button_box.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(
            self.reset
        )

        QTimer.singleShot(0, self.init_ui)

    def init_ui(self):
        logger.info("init_ui")
        self.widget_k_size = self.findChild(LabeledSliderWidget, "widget_k_size")
        self.widget_k_size.set_min(config.k_size["min"])
        self.widget_k_size.set_max(config.k_size["max"])

        self.widget_sigma_x = self.findChild(LabeledSliderWidget, "widget_sigma_x")
        self.widget_sigma_x.set_min(config.sigma_x["min"])
        self.widget_sigma_x.set_max(config.sigma_x["max"])

        self.widget_threshold_1 = self.findChild(
            LabeledSliderWidget, "widget_threshold_1"
        )
        self.widget_threshold_1.set_min(config.threshold_1["min"])
        self.widget_threshold_1.set_max(config.threshold_1["max"])

        self.widget_threshold_2 = self.findChild(
            LabeledSliderWidget, "widget_threshold_2"
        )
        self.widget_threshold_2.set_min(config.threshold_2["min"])
        self.widget_threshold_2.set_max(config.threshold_2["max"])

        self.widget_kernel = self.findChild(LabeledSliderWidget, "widget_kernel")
        self.widget_kernel.set_min(config.kernel["min"])
        self.widget_kernel.set_max(config.kernel["max"])

        self.widget_iterations = self.findChild(
            LabeledSliderWidget, "widget_iterations"
        )
        self.widget_iterations.set_min(config.iterations["min"])
        self.widget_iterations.set_max(config.iterations["max"])

        self.widget_dp = self.findChild(LabeledSliderWidget, "widget_dp")
        self.widget_dp.set_min(config.dp["min"])
        self.widget_dp.set_max(config.dp["max"])

        self.widget_min_dist = self.findChild(LabeledSliderWidget, "widget_min_dist")
        self.widget_min_dist.set_min(config.min_dist["min"])
        self.widget_min_dist.set_max(config.min_dist["max"])

        self.widget_min_dist = self.findChild(LabeledSliderWidget, "widget_min_dist")
        self.widget_min_dist.set_min(config.min_dist["min"])
        self.widget_min_dist.set_max(config.min_dist["max"])

        self.widget_param_1 = self.findChild(LabeledSliderWidget, "widget_param_1")
        self.widget_param_1.set_min(config.param_1["min"])
        self.widget_param_1.set_max(config.param_1["max"])

        self.widget_param_2 = self.findChild(LabeledSliderWidget, "widget_param_2")
        self.widget_param_2.set_min(config.param_2["min"])
        self.widget_param_2.set_max(config.param_2["max"])

        self.widget_min_radius = self.findChild(
            LabeledSliderWidget, "widget_min_radius"
        )
        self.widget_min_radius.set_min(config.min_radius["min"])
        self.widget_min_radius.set_max(config.min_radius["max"])

        self.widget_max_radius = self.findChild(
            LabeledSliderWidget, "widget_max_radius"
        )
        self.widget_max_radius.set_min(config.max_radius["min"])
        self.widget_max_radius.set_max(config.max_radius["max"])

        self.__update_value()

    def accept(self):
        logger.info("accept")
        config.k_size = self.widget_k_size.get_value()
        config.sigma_x = self.widget_sigma_x.get_value()
        config.threshold_1 = self.widget_threshold_1.get_value()
        config.threshold_2 = self.widget_threshold_2.get_value()
        config.kernel = self.widget_kernel.get_value()
        config.iterations = self.widget_iterations.get_value()
        config.dp = self.widget_dp.get_value()
        config.min_dist = self.widget_min_dist.get_value()
        config.min_dist = self.widget_min_dist.get_value()
        config.param_1 = self.widget_param_1.get_value()
        config.param_2 = self.widget_param_2.get_value()
        config.min_radius = self.widget_min_radius.get_value()
        config.max_radius = self.widget_max_radius.get_value()

        config.save()
        super().accept()

    def reset(self):
        logger.info("reset")
        config.reset()
        self.__update_value()

    def __update_value(self):
        self.widget_k_size.set_value(config.k_size["value"])
        self.widget_sigma_x.set_value(config.sigma_x["value"])
        self.widget_threshold_1.set_value(config.threshold_1["value"])
        self.widget_threshold_2.set_value(config.threshold_2["value"])
        self.widget_kernel.set_value(config.kernel["value"])
        self.widget_iterations.set_value(config.iterations["value"])
        self.widget_dp.set_value(config.dp["value"])
        self.widget_min_dist.set_value(config.min_dist["value"])
        self.widget_min_dist.set_value(config.min_dist["value"])
        self.widget_param_1.set_value(config.param_1["value"])
        self.widget_param_2.set_value(config.param_2["value"])
        self.widget_min_radius.set_value(config.min_radius["value"])
        self.widget_max_radius.set_value(config.max_radius["value"])
