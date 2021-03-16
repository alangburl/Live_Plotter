from PyQt5.QtWidgets import (QApplication, QPushButton,QWidget,QSizePolicy,
                             QMainWindow,QAction,QVBoxLayout,QDockWidget,
                             QLabel,QFileDialog,QTextEdit,QCheckBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt,QEvent
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

class Interface(QMainWindow):
    current_graph='Scatter Plot'
    plot_type=['Scatter Plot', 'Line Plot','Histogram','Pie Chart',
               'Bar Chart','Double Bar Chart']
    header_labels={'Scatter Plot':'X Data, Y Data', 
                   'Line Plot':'X Data, Y Data',
                   'Histogram':'X Data, Y Data',
                   'Pie Chart':'Percent',
                   'Bar Chart':'X Label, Height',
                   'Double Bar Chart':'X Label, Height1, Height2'}
    data_types={'Scatter Plot':['float','float'], 
                   'Line Plot':['float','float'],
                   'Histogram':['float','float'],
                   'Pie Chart':['float'],
                   'Bar Chart':['str','float'],
                   'Double Bar Chart':['str','float','float']}
    function_calls={'Scatter Plot':'scatter', 
                   'Line Plot':'plot',
                   'Histogram':'hist',
                   'Pie Chart':'pie',
                   'Bar Chart':'bar',
                   'Double Bar Chart':'beast'}
    function_kwargs={'Scatter Plot':None, 
                   'Line Plot':None,
                   'Histogram':None,
                   'Pie Chart':"autopct='%1.1f%%'",
                   'Bar Chart':None,
                   'Double Bar Chart':None}
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Live Plotter')
        self.size_policy=QSizePolicy.Expanding
        self.font=QFont()
        self.font.setPointSize(12)        
        self.geometry()
        self.menu()
        self.showMaximized()
        self.show()
        
    def menu(self):
        self.menuType=self.menuBar().addMenu('&Chart Type')
        self.actions={}
        for i in self.plot_type:
            self.actions[i]=self.action_definer(i)
            self.menuType.addAction(self.actions[i])
            
    def action_definer(self,label):
        action=QAction('&{}'.format(label),self,checkable=True)
        action.setFont(self.font)
        action.triggered.connect(lambda: self.action_changed(label))
        if label==self.plot_type[0]:
            action.setChecked(True)
        return action

    def action_changed(self,label):
        self.text_format.setText(self.header_labels[label])
        for i in self.actions:
            if i!=label:
                self.actions[i].setChecked(False)
            else:
                self.actions[i].setChecked(True)
                self.current_graph=i
                self.update_graph()
    
    def geometry(self):
        #configure the main graph
        self.plot_window=QWidget()
        layout=QVBoxLayout()
        self.figure=Figure()
        self._canvas=FigureCanvas(self.figure)
        self.toolbar=CustomToolbar(self._canvas,self)
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
        self.text_format=QLabel(self.header_labels['Scatter Plot'])
        self.text_format.setFont(self.font)
        
        # self.data_editor=QTextEdit(self)
        self.data_editor=Custom_Text_Editor(self)
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
        layout.addWidget(self.text_format)
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
        data=self.data_import(self.data_editor.toPlainText())
        #now actually plot the data
        d_lists=''
        for i in range(len(data)-1):
            d_lists+='data[{}],'.format(i)
        d_lists+='data[{}]'.format(len(data)-1)
        if self.function_kwargs[self.current_graph]!=None:
            d_lists+=',{}'.format(self.function_kwargs[self.current_graph])
        try:
            exec('{}.{}({})'.format('self.axis',
                                        self.function_calls[self.current_graph],
                                        d_lists))
        except Exception as e:
            print(e)
        #now handle the various options for the pie charts and bar charts            
        self._canvas.draw()
        self.figure.tight_layout()
        
    def data_import(self,text):
        columns=text.split(sep='\n')
        #get the data types to try and convert based on the selected
        #graph style
        d_type=self.data_types[self.current_graph]
        data={}
        for i in range(len(d_type)):
            data[i]=[]
        
        for i in columns:
            splitr=i.split(sep=',')
            for j in range(len(splitr)):
                value=splitr[j]
                if value!='':
                    try:
                        if d_type[j]!='str':
                            data[j].append(eval('{}({})'.format(d_type[j],value)))
                        else:
                            data[j].append(value)
                    except Exception as e: 
                        print(e)  
        return data
    
class Custom_Text_Editor(QTextEdit):
    def __init__(self,parent):
        super().__init__(parent)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.read_file(file_path)
            event.accept()
        else:
            event.ignore()
            
    def read_file(self,path):
        self.clear()
        f=open(path,'r')
        data=f.readlines()
        f.close()
        for i in data:
            self.append(i.split(sep='\n')[0])
            
class CustomToolbar(NavigationToolbar):
    def __init__(self,canvas_,parent_):
        NavigationToolbar.__init__(self,canvas_,parent_)
        
    def save_figure(self,*args):
        filetypes = self.canvas.get_supported_filetypes_grouped()
        sorted_filetypes = sorted(filetypes.items())
        default_filetype = self.canvas.get_default_filetype()
        des_extens=[]
        for name,exts in sorted_filetypes:
            name_exts=''.join(['*{}'.format(i) for i in exts])
            vals='{} ({})'.format(name, name_exts)
            if default_filetype in name_exts:
                default=vals
            des_extens.append(vals)
        des_extens=';;'.join(des_extens)
        file_name,ok=QFileDialog.getSaveFileName(self,'Image Saving','',
                                                 des_extens,default)
        if ok:
            self.canvas.figure.savefig(file_name,dpi=600)
        
if __name__ =="__main__":
    app=QApplication(sys.argv)
    ex=Interface()
    sys.exit(app.exec_())