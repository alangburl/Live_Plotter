import sys,time,winsound
import numpy as np
from PyQt5.QtWidgets import (QApplication, QPushButton,QWidget,QGridLayout,
                             QSizePolicy,QLineEdit,
                             QMainWindow,QAction,QVBoxLayout
                             ,QDockWidget,QListView,
                             QAbstractItemView,QLabel,QFileDialog,QTextEdit,
                             QInputDialog,QSlider,QMdiArea,QMdiSubWindow,QCheckBox)
from PyQt5.QtGui import QFont,QColor
from PyQt5.QtCore import Qt,QEvent
#import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class Interface(QMainWindow):
    plot_type=['Scatter Plot', 'Line Plot','Histogram','Pie Chart',
               'Bar Chart','Double Bar Chart']
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Live Plotter')
        self.size_policy=QSizePolicy.Expanding
        self.font=QFont()
        self.font.setPointSize(12)        
        self.menu()
        self.geometry()
        self.showMaximized()
        self.show()
        
    def menu(self):
        self.menuType=self.menuBar().addMenu('&Chart Type')
        self.actions={}
        for i in self.plot_type:
            self.actions[i]=QAction('&{}'.format(i),self,checkable=True)
            
            self.menuType.addAction(self.actions[i])
            
        for i in self.actions:
            self.actions[i].triggered.connect(lambda: self.action_changed(i))

    def action_changed(self,label):
        print(label)
        for i in self.actions:
            if i!=label:
                self.actions[i].setChecked(True)
    
    def geometry(self):
        #configure the main graph
        self.plot_window=QWidget()
        layout=QVBoxLayout()
        self.figure=Figure()
        self._canvas=FigureCanvas(self.figure)
        self.toolbar=NavigationToolbar(self._canvas,self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self._canvas)
        self.plot_window.setLayout(layout)
        self.setCentralWidget(self.plot_window)
        self.axis = self._canvas.figure.subplots()
        self.figure.tight_layout()
        self.setCentralWidget(self.plot_window)
        
        #now configure the right side to be a plain text editor
        right_dock=QDockWidget('Data')
        right_widget=QWidget()
        text_format=QLabel('X Data, Y Data')
        # text_format.setSizePolicy(self.size_policy)
        text_format.setFont(self.font)
        self.data_editor=QTextEdit(self)
        self.data_editor.setSizePolicy(self.size_policy, self.size_policy)
        self.data_editor.setFont(self.font)
        self.data_editor.installEventFilter(self)
        
        self.hold_plot_on=QCheckBox('Reset Graph')
        self.hold_plot_on.setChecked(True)
        self.hold_plot_on.setFont(self.font)
        
        self.process=QPushButton('Update')
        self.process.setFont(self.font)
        self.process.clicked.connect(self.update_graph)
        
        layout=QVBoxLayout()
        layout.addWidget(text_format)
        layout.addWidget(self.data_editor)
        layout.addWidget(self.hold_plot_on)
        layout.addWidget(self.process)
        right_widget.setLayout(layout)
        right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, right_dock)
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.data_editor:
            if event.key() == Qt.Key_Return or event.key()==Qt.Key_Enter \
                and self.data_editor.hasFocus():
                self.update_graph()
        return super().eventFilter(obj, event)
        
    def update_graph(self):
        if self.hold_plot_on.isChecked():
            self.axis.clear()
        #get the data from the text editor first
        data=self.data_editor.toPlainText()
        columns=data.split(sep='\n')
        first_entry=[]
        second_entry=[]
        for i in columns:
            if i!='':
                try:
                    splits=i.split(sep=',')
                    first_entry.append(float(splits[0]))
                    second_entry.append(float(splits[1]))
                except Exception as e:
                    print(e)
        
        self.axis.plot(first_entry,second_entry)
        self._canvas.draw()
        self.figure.tight_layout()
        
        
        
if __name__ =="__main__":
    app=QApplication(sys.argv)
    ex=Interface()
    sys.exit(app.exec_())