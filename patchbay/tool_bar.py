
from enum import IntFlag
from typing import TYPE_CHECKING
from PyQt5.QtWidgets import (
    QToolBar, QLabel, QMenu,
    QApplication, QAction)
from PyQt5.QtGui import QMouseEvent, QIcon
from PyQt5.QtCore import pyqtSignal, Qt, QPoint


from .base_elements import ToolDisplayed
from .patchbay_manager import PatchbayManager
from .tools_widgets import PatchbayToolsWidget

_translate = QApplication.translate


class PatchbayToolBar(QToolBar):    
    def __init__(self, parent):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.PreventContextMenu)

        default_displayed_widgets = (
            ToolDisplayed.ZOOM_SLIDER
            | ToolDisplayed.TRANSPORT_PLAY_STOP
            | ToolDisplayed.BUFFER_SIZE
            | ToolDisplayed.SAMPLERATE
            | ToolDisplayed.XRUNS
            | ToolDisplayed.DSP_LOAD)
        
        # TODO : search config here
        int_displayed_wdgs = default_displayed_widgets
        try:
            self._displayed_widgets = ToolDisplayed(int_displayed_wdgs)
        except:
            self._displayed_widgets = default_displayed_widgets
        
        self._transport_widget = None
        self._patchbay_mng : PatchbayManager = None
    
    def set_patchbay_manager(self, patchbay_manager: PatchbayManager):
        self._patchbay_mng = patchbay_manager
        patchbay_manager.change_tools_displayed(self._displayed_widgets)
    
    def _change_visibility(self):
        if self._patchbay_mng is not None:
            self._patchbay_mng.change_tools_displayed(self._displayed_widgets)

    def set_default_displayed_widgets(self, displayed_widgets: ToolDisplayed):
        self._displayed_widgets = displayed_widgets
        self._change_visibility()
        
    def get_displayed_widgets(self) -> ToolDisplayed:
        return self._displayed_widgets

    def mousePressEvent(self, event: QMouseEvent) -> None:
        child_widget = self.childAt(event.pos())
        super().mousePressEvent(event)

        if (event.button() != Qt.RightButton
                or not isinstance(child_widget, (QLabel, PatchbayToolsWidget))):
            return

        menu = QMenu()
        menu.addSection(_translate('tool_bar', 'Displayed tools'))
        
        tool_actions = {
            ToolDisplayed.PORT_TYPES_VIEW:
                QAction(QIcon.fromTheme('view-filter'),
                        _translate('tool_bar', 'Type filter')),
            ToolDisplayed.ZOOM_SLIDER:
                QAction(QIcon.fromTheme('zoom-select'),
                        _translate('tool_bar', 'Zoom slider')),
            ToolDisplayed.TRANSPORT_CLOCK:
                QAction(QIcon.fromTheme('clock'),
                        _translate('tool_bar', 'Transport clock')),
            ToolDisplayed.TRANSPORT_PLAY_STOP:
                QAction(QIcon.fromTheme('media-playback-pause'),
                        _translate('tool_bar', 'Transport Play/Stop')),
            ToolDisplayed.BUFFER_SIZE:
                QAction(QIcon.fromTheme('settings-configure'),
                        _translate('tool_bar', 'Buffer size')),
            ToolDisplayed.SAMPLERATE:
                QAction(QIcon.fromTheme('filename-sample-rate'),
                        _translate('tool_bar', 'Sample rate')),
            ToolDisplayed.LATENCY:
                QAction(QIcon.fromTheme('chronometer-lap'),
                        _translate('tool_bar', 'Latency')),
            ToolDisplayed.XRUNS:
                QAction(QIcon.fromTheme('data-error'),
                        _translate('tool_bar', 'Xruns')),
            ToolDisplayed.DSP_LOAD:
                QAction(QIcon.fromTheme('histogram-symbolic'),
                        _translate('tool_bar', 'DSP Load'))
        }
        
        for key, act in tool_actions.items():
            act.setCheckable(True)
            act.setChecked(bool(self._displayed_widgets & key))
            menu.addAction(act)
        
        # execute the menu, exit if no action
        point = event.screenPos().toPoint()
        point.setY(self.mapToGlobal(QPoint(0, self.height())).y())
        selected_act = menu.exec(point)
        if selected_act is None:
            return

        for key, act in tool_actions.items():
            if act is selected_act:
                if act.isChecked():
                    self._displayed_widgets |= key
                else:
                    self._displayed_widgets &= ~key

        self._change_visibility()