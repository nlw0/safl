from PyQt4 import QtCore
from PyQt4 import QtGui
from point_ui import Ui_MainWindow
import simplejson
import sys, Image, os
import numpy as np

class DesignerMainWindow(QtGui.QMainWindow, Ui_MainWindow):

  def __init__(self, configFile='', parent=None):
    super(DesignerMainWindow, self).__init__(parent)
    self.setupUi(self)

    self.parseConfig(configFile)

    self.Nset = 20
    self.point_matches = -1*np.ones((self.Nframes, self.Nset), dtype=np.int)

    self.img1IndexBox.setMinimum(0)
    self.img1IndexBox.setMaximum(self.Nframes-1)
    self.img2IndexBox.setMinimum(0)
    self.img2IndexBox.setMaximum(self.Nframes-1)
    self.img1IndexBox.setValue(0)
    self.img2IndexBox.setValue(1)

    self.setIndexBox.setMinimum(0)
    self.setIndexBox.setMaximum(self.Nset-1)
    self.setIndexBox.setValue(0)
    self.workingPoint = 0

    self.changeImage1(self.img1IndexBox.value())
    self.changeImage2(self.img2IndexBox.value())

    QtCore.QObject.connect(self.actionOpen, QtCore.SIGNAL("triggered()"), self.parseConfig)
    QtCore.QObject.connect(self.actionQuit, QtCore.SIGNAL('triggered()'), QtGui.qApp, QtCore.SLOT("quit()"))
    QtCore.QObject.connect(self.actionSave, QtCore.SIGNAL('triggered()'), self.save_matches)
    QtCore.QObject.connect(self.setIndexBox, QtCore.SIGNAL("valueChanged(int)"), self.selectPoint)
    QtCore.QObject.connect(self.img1IndexBox, QtCore.SIGNAL("valueChanged(int)"), self.changeImage1)
    QtCore.QObject.connect(self.img2IndexBox, QtCore.SIGNAL("valueChanged(int)"), self.changeImage2)
    self.im1.canvas.mpl_connect('pick_event', self.onpick)
    self.im2.canvas.mpl_connect('pick_event', self.onpick)

    
  def onpick(self, event):
    ## Not a left click, just ignore
    if event.mouseevent.button != 1:
      return

    if event.artist == self.line1:
      self.point_matches[self.img1_who,self.workingPoint] = event.ind[0]
      self.update_selected_points(1)
    if event.artist == self.line2:
      self.point_matches[self.img2_who,self.workingPoint] = event.ind[0]
      self.update_selected_points(2)


  def selectPoint(self, event):
    self.workingPoint = self.setIndexBox.value()
    self.update_selected_points(1)
    self.update_selected_points(2)

  def changeImage1(self, newfig):
    print "change 1 to ", newfig
    self.img1_who = newfig
    self.im1.axes.clear()
    self.im1.axes.imshow(self.frames[newfig])
    
    self.im1.canvas.draw()
    self.plot_possible_points(1)
    self.update_selected_points(1)

  def changeImage2(self, newfig):
    print "change 2 to ", newfig
    self.img2_who = newfig
    self.im2.axes.clear()
    self.im2.axes.imshow(self.frames[newfig])
    self.im2.canvas.draw()
    self.plot_possible_points(2)
    self.update_selected_points(2)

  def save_matches(self):
    print 'Saving current matching matrix'
    np.savez(self.params['root_directory'] + '/matches.npz', matches=self.point_matches)

  def parseConfig(self,configFile=''):
    ## Opens dialog box if no config file name is provided.
    if configFile == '':
      configFile = str(QtGui.QFileDialog.getOpenFileName())

    self.params = simplejson.load(open(configFile))

    self.Nframes = self.params['last_frame']+1

    self.points = [
      np.load(self.params['root_directory'] + '/points/%08d.npz'%k)['arr_0'] \
      for k in range(self.Nframes) ]

    self.frames = [
      np.asarray(Image.open( \
        self.params['root_directory'] + '/frames/' + \
        self.params['filename_format']%k)) \
      for k in range(self.Nframes) ]
    
  def plot_possible_points(self, im):
    if im == 1:
      frame = self.img1_who
      self.line1, = self.im1.axes.plot(self.points[frame][:,0],
                                       self.points[frame][:,1],
                                       'bo', picker=3)
      self.mark1, = self.im1.axes.plot([],[],
                                       'ys', picker=3)
      self.wrk1, = self.im1.axes.plot([],[],
                                      'rs', picker=3)
      self.im1.canvas.draw()
    elif im == 2:
      frame = self.img2_who
      self.line2, = self.im2.axes.plot(self.points[frame][:,0],
                                       self.points[frame][:,1],
                                       'bo', picker=3)
      self.mark2, = self.im2.axes.plot([],[],
                                       'ys', picker=3)
      self.wrk2, = self.im2.axes.plot([],[],
                                      'rs', picker=3)
      self.im2.canvas.draw()

  def update_selected_points(self, im):
    if im == 1:
      frame = self.img1_who
      sel = self.point_matches[frame]
      sel = sel[sel>=0]
      if sel == []:
        self.mark1.set_data([],[])
      else:
        self.mark1.set_data(self.points[frame][sel,0],
                            self.points[frame][sel,1])
      sel = self.point_matches[frame,self.workingPoint]
      if sel == -1:
        self.wrk1.set_data([],[])
      else:
        self.wrk1.set_data(self.points[frame][sel,0],
                           self.points[frame][sel,1])
      self.im1.canvas.draw()
    elif im == 2:
      frame = self.img2_who
      sel = self.point_matches[frame]
      sel = sel[sel>=0]
      if sel == []:
        self.mark2.set_data([],[])
      else:
        self.mark2.set_data(self.points[frame][sel,0],
                            self.points[frame][sel,1])
      sel = self.point_matches[frame,self.workingPoint]
      if sel == -1:
        self.wrk2.set_data([],[])
      else:
        self.wrk2.set_data(self.points[frame][sel,0],
                           self.points[frame][sel,1])

      self.im2.canvas.draw()


if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  if len(sys.argv) > 1:
    dmw = DesignerMainWindow(sys.argv[1])
  else:
    dmw = DesignerMainWindow('')
  dmw.show()
  sys.exit(app.exec_())

  
