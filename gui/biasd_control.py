# -*- coding: utf-8 -*-®
import sys

# Make sure that we are using QT5
import matplotlib
matplotlib.use('Qt5Agg')

# PyQt5 imports
from PyQt5.QtWidgets import QApplication, QColumnView, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMainWindow, QFileDialog, QLabel, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt, QTimer


# Other UIs 
from priors2 import ui_priors
from smd_loader import ui_loader
from preferences import ui_preferences
from traces import ui_traces, ui_set_tau

# BIASD Path
biasd_path = '../'
sys.path.append(biasd_path)
import biasd as b

__version__ = "0.1.1"

class _logfile():
	from time import ctime
	def __init__(self):
		self.log = []
	def new(self,entry):
		try:
			self.log.append(_logfile.ctime() + " - " + str(entry))
		except:
			pass
	def format(self):
		return ''.join(ll+"\n" for ll in self.log)

class prefs():
	def __init__(self):
		class _x(): pass
		self.default = _x()
		self.default.eps = b.likelihood._eps
		self.default.n_threads = 1
		self.default.speed_n = 10
		self.default.speed_d = 5000
		self.default.tau = 1.
		self.reset()

	def reset(self):
		self.eps = self.default.eps
		self.n_threads = self.default.n_threads
		self.speed_n = self.default.speed_n
		self.speed_d = self.default.speed_d
		self.tau = self.default.tau

class biasd_control(QWidget):
	def __init__(self,parent=None):
		super(QWidget,self).__init__(parent)
		self.initialize()
		self.__version__ = __version__

	def initialize(self):

		self.bprior = QPushButton("Priors")	
		bnew = QPushButton("New")
		bload = QPushButton("Open")
		bexplore = QPushButton("Explore")
		breset = QPushButton("Reset")
		bprefs = QPushButton('Preferences')
		btest = QPushButton('test')
		self.btraces = QPushButton('Traces')
#		bset_tau = QPushButton(u'&Set τ')

		# Overall Layout
		vbox = QVBoxLayout()
		
		# Box 1
		qtemp = QWidget()
		hbox1 = QHBoxLayout()
		[hbox1.addWidget(bbb) for bbb in [bnew,bload,bexplore]]
		hbox1.addStretch(1)
		qtemp.setLayout(hbox1)
		vbox.addWidget(qtemp)
		
		# Middle Buttons
#		vbox.addWidget(bset_tau)
		vbox.addWidget(self.btraces)
		vbox.addWidget(btest)
		vbox.addWidget(self.bprior)
		
		# Box 2
		qtemp = QWidget()
		hbox2 = QHBoxLayout()
		[hbox2.addWidget(bbb) for bbb in [breset,bprefs]]
		qtemp.setLayout(hbox2)
		vbox.addWidget(qtemp)
		
		self.setLayout(vbox)
		
		## Connect the buttons
		self.bprior.clicked.connect(self.launch_priors)
		bnew.clicked.connect(self.new_smd)
		bload.clicked.connect(self.load_smd)
		bexplore.clicked.connect(self.explore_smd)
		btest.clicked.connect(self.test)
		bprefs.clicked.connect(self.launch_preferences)
		breset.clicked.connect(self.reset)
		self.btraces.clicked.connect(self.launch_traces)
#		bset_tau.clicked.connect(self.launch_set_tau)
		
		self.bprior.setEnabled(False)
		self.btraces.setEnabled(False)
		
		self.priors = b.distributions.empty_parameter_collection()
		self.log = _logfile()
		self.prefs = prefs()
		
		self.filename = ''
	
	def launch_traces(self):
		if self.filename != "":
			# try:
			# 	if not self.ui_traces.isVisible():
			# 		self.ui_traces.setVisible(True)
			# 	self.ui_traces.raise_()
			# except:
			self.ui_traces = ui_traces(self)
		
	
	def reset(self):
		try:
			self.ui_explore.close()
		except:
			pass
		try:
			self.ui_priors.close()
		except:
			pass
		self.priors = b.distributions.empty_parameter_collection()
		self.bprior.setEnabled(False)
		self.btraces.setEnabled(False)
		self.parent().statusBar().showMessage('Reset')

		self.log.new('Reset GUI')
	
	def new_smd(self):
		oname = QFileDialog.getSaveFileName(self,"Create new HDF5 SMD file",'./','HDF SMD (*.hdf5 *.SMD *.smd *.HDF5 *.HDF *.hdf *.dat *.biasd)')

		try:
			if not oname[0]:
				return
			f = b.smd.new(oname[0],force=True)
			b.smd.save(f)
			self.reset()
			self.set_filename(oname[0])
			self.bprior.setEnabled(True)
			self.btraces.setEnabled(True)
		except:
			QMessageBox.critical(None,"Could Not Make New File","Could not make new file: %s\n."%(oname[0]))
		
	def load_smd(self):
		fname = str(QFileDialog.getOpenFileName(self,"Choose HDF5 SMD file to load","./",filter='HDF5 SMD (*.smd *.SMD *.HDF5 *.HDF *.hdf5 *.hdf *.dat *.biasd)')[0])
		data = False
		if fname:
			try:
				f = b.smd.load(fname)
				f.close()
				data = True
			except:
				QMessageBox.critical(None,'Could Not Load File','Could not load file: %s.\nMake sure to use an HDF5 file'%fname)
		if data:
			self.reset()
			self.set_filename(fname)
			self.bprior.setEnabled(True)
			self.btraces.setEnabled(True)
			
	def set_filename(self,fname):
		self.filename = fname
		if len(self.filename) > 25:
			dispfname ="....."+self.filename[-25:]
		else:
			dispfname = self.filename
		# self.lfilename.setText(dispfname)
		self.parent().statusBar().showMessage('Loaded %s'%(dispfname))
		self.log.new('Loaded %s'%(self.filename))
	
	def get_smd_filename(self):
		return self.filename

	def explore_smd(self):
		try:
			self.ui_explore.close()
		except:
			pass
		self.ui_explore = ui_loader(parent = self, select = False)
		self.ui_explore.show()
		
	
	def launch_preferences(self):
		try:
			if not self.ui_prefs.isVisible():
				self.ui_pref.setVisible(True)
			self.ui_prefs.raise_()
		except:
			self.ui_prefs = ui_preferences(self)
			self.ui_prefs.show()
	
#	def launch_set_tau(self):
#		try:
#			self.ui_tau.close()
#		except:
#			pass
#		self.ui_tau = ui_set_tau(self)
#		self.ui_tau.setParent(self)
		
	
	def test(self):
		# self.ui_priors.ui.update_dists()
		print self.log.format()
		# print self.prefs.n_threads,self.prefs.eps,self.prefs.speed_n,self.prefs.speed_d,self.prefs.default.speed_d
	
	def launch_priors(self):
		try:
			if not self.ui_priors.isVisible():
				self.ui_priors.setVisible(True)
			self.ui_priors.raise_()
		except:
			self.ui_priors = ui_priors(self)
			self.ui_priors.show()
	
class gui(QMainWindow):
	def __init__(self):
		super(QMainWindow,self).__init__()
		self.initialize()

	def initialize(self):
		self.bc = biasd_control(self)
		self.setCentralWidget(self.bc)
		self.statusBar().showMessage("Ready")
		
		self.setWindowTitle("BIASD - 0.1.1")
		self.setWindowIcon(QIcon('biasd_icon-01.png'))
		self.setGeometry(250,250,250,150)
		self.show()
	
	def closeEvent(self,event):
		reply = QMessageBox.question(self,'Quit',"Are you sure you want to quit?")
		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()
		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle('fusion')
	app.setWindowIcon(QIcon('b_arrows-01.png'))
	g = gui()
	sys.exit(app.exec_())