#!/usr/bin/python2

## Remember to use "pyuic4 -o objseg_ui.py objseg_ui.ui"
from PyQt4 import QtCore
from PyQt4 import QtGui
from objseg_ui import Ui_MainWindow
import simplejson
import pickle
import sys, Image, os
import numpy as np

class DesignerMainWindow(QtGui.QMainWindow, Ui_MainWindow):

  def __init__(self, configFile='', parent=None):
    super(DesignerMainWindow, self).__init__(parent)
    self.setupUi(self)

    self.parseConfig(configFile)

    self.clouds_file = self.params['root_directory'] + '/points/clouds.pkl'
    
    try:
      ff = open(self.clouds_file)
      self.clouds = pickle.load(ff)
      ff.close()
      print 'Read existing point match file.'
    except:
      print 'No point match file exists.'
      self.clouds = {}
      for k in range(self.Nframes):
        self.clouds[0] = {}

    self.Nset = 5

    self.img1IndexBox.setMinimum(0)
    self.img1IndexBox.setMaximum(self.Nframes-1)
    self.img1IndexBox.setValue(0)

    self.setIndexBox.setMinimum(0)
    self.setIndexBox.setMaximum(self.Nset-1)
    self.setIndexBox.setValue(0)
    self.working_object = 0

    self.changeImage1(self.img1IndexBox.value())

    QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.parseConfig)
    QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL('triggered()'), QtGui.qApp, QtCore.SLOT("quit()"))
    QtCore.QObject.connect(self.actionSave, QtCore.SIGNAL('triggered()'), self.save_matches)
    QtCore.QObject.connect(self.actionClear_matches, QtCore.SIGNAL('triggered()'), self.clear_matches)
    QtCore.QObject.connect(self.setIndexBox, QtCore.SIGNAL("valueChanged(int)"), self.change_working_object)
    QtCore.QObject.connect(self.img1IndexBox, QtCore.SIGNAL("valueChanged(int)"), self.changeImage1)
    self.im1.canvas.mpl_connect('pick_event', self.onpick)
    self.im1.canvas.mpl_connect('button_press_event', self.onclick)

    self.did_pick = False



  def onclick(self, event):
    ## Test if something was just picked from this click. In this
    ## case, do nothing.
    if self.did_pick:
      self.did_pick = False
      return

    ## Not a left click, just ignore
    if event.button != 1:
      return

    if event.canvas == self.im1.canvas:
      print event.xdata, event.ydata
      
      self.update_selected_object(1)


  def onpick(self, event):
    ## Not a left click, just ignore
    if event.mouseevent.button != 1:
      return

    if event.artist == self.line1:
      self.point_matches[self.img1_who,self.working_object] = event.ind[0]
      self.did_pick = True
      im = 1
    else:
      return

    if self.did_pick == True:
      if self.autoFeed.isChecked():
        self.setIndexBox.setValue((self.working_object+1)%self.Nset)
      else:
        self.update_selected_object(im)

  def change_working_object(self, wp):
    self.working_object = wp
    self.update_selected_object(1)

  def changeImage1(self, newfig):
    print "change 1 to ", newfig
    self.img1_who = newfig
    self.im1.axes.clear()
    self.im1.axes.imshow(self.frames[newfig])
    
    self.im1.canvas.draw()
    self.plot_selected_points(1)
    self.update_selected_object(1)

  def clear_matches(self):
    print 'Erasing current match matrix'
    self.Nset = 54
    self.point_matches = -1*np.ones((self.Nframes, self.Nset), dtype=np.int)
    self.update_selected_object(1)
    
  def save_matches(self):
    print 'Saving current match matrix'
    np.savez(self.params['root_directory'] + '/points/matches.npz', matches=self.point_matches)

  def parseConfig(self,configFile=''):
    ## Opens dialog box if no config file name is provided.
    if configFile == '':
      configFile = str(QtGui.QFileDialog.getOpenFileName())

    self.params = simplejson.load(open(configFile))

    self.Nframes = self.params['last_frame']+1

    self.frames = [
      np.asarray(Image.open( \
        self.params['root_directory'] + '/frames/' + \
        self.params['filename_format']%k)) \
      for k in range(self.Nframes) ]

  def plot_selected_points(self, im):
    if im == 1:
      frame = self.img1_who

      pp = self.clouds[frame]
      print pp

      self.allobj, = self.im1.axes.plot([],[],
                                       'r+', picker=3)
      self.selobj, = self.im1.axes.plot([],[],
                                       'y+', picker=3)

      # self.line1, = self.im1.axes.plot(self.points[frame][:,0],
      #                                  self.points[frame][:,1],
      #                                  'bo', picker=3)
      # self.mark1, = self.im1.axes.plot([],[],
      #                                  'ys', picker=3)
      # self.wrk1, = self.im1.axes.plot([],[],
      #                                 'rs', picker=3)
      self.im1.canvas.draw()

  def update_selected_object(self, im):
    if im == 1:
      print 'hi'


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  if len(sys.argv) > 1:
    dmw = DesignerMainWindow(sys.argv[1])
  else:
    dmw = DesignerMainWindow('')
  dmw.show()
  sys.exit(app.exec_())

  
## Local variables:
## python-indent: 2
## end:
