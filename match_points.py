#!/usr/bin/python2.7

import simplejson
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, qApp
from pylab import *

from point_ui import Ui_MainWindow


class DesignerMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, configFile='', parent=None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.parseConfig(configFile)

        matches_file = self.params['root_directory'] + '/points/matches.npz'

        try:
            self.point_matches = np.load(matches_file)['matches']
            self.Nset = self.point_matches.shape[1]
            print('Read existing point match file exists.')
        except:
            print('No point match file exists.')
            self.Nset = 54
            self.point_matches = -1 * np.ones((self.Nframes, self.Nset), dtype=np.int)

        self.img1IndexBox.setMinimum(0)
        self.img1IndexBox.setMaximum(self.Nframes - 1)
        self.img2IndexBox.setMinimum(0)
        self.img2IndexBox.setMaximum(self.Nframes - 1)
        self.img1IndexBox.setValue(0)
        self.img2IndexBox.setValue(1)

        self.setIndexBox.setMinimum(0)
        self.setIndexBox.setMaximum(self.Nset - 1)
        self.setIndexBox.setValue(0)
        self.working_point = 0

        self.changeImage1(self.img1IndexBox.value())
        self.changeImage2(self.img2IndexBox.value())

        self.actionOpen.triggered.connect(self.parseConfig)
        self.actionQuit.triggered.connect(qApp.quit)
        self.actionSave.triggered.connect(self.save_matches)
        self.actionClear_matches.triggered.connect(self.clear_matches)
        self.setIndexBox.valueChanged.connect(self.change_working_point)
        self.img1IndexBox.valueChanged.connect(self.changeImage1)
        self.img2IndexBox.valueChanged.connect(self.changeImage2)
        self.im1.canvas.mpl_connect('pick_event', self.onpick)
        self.im2.canvas.mpl_connect('pick_event', self.onpick)
        self.im1.canvas.mpl_connect('button_press_event', self.onclick)
        self.im2.canvas.mpl_connect('button_press_event', self.onclick)

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
            self.point_matches[self.img1_who, self.working_point] = -1
            self.update_selected_points(1)
        elif event.canvas == self.im2.canvas:
            self.point_matches[self.img2_who, self.working_point] = -1
            self.update_selected_points(2)

    def onpick(self, event):
        ## Not a left click, just ignore
        if event.mouseevent.button != 1:
            return

        if event.artist == self.line1:
            self.point_matches[self.img1_who, self.working_point] = event.ind[0]
            self.did_pick = True
            im = 1
        elif event.artist == self.line2:
            self.point_matches[self.img2_who, self.working_point] = event.ind[0]
            self.did_pick = True
            im = 2
        else:
            return

        if self.did_pick == True:
            if self.autoFeed.isChecked():
                self.setIndexBox.setValue((self.working_point + 1) % self.Nset)
            else:
                self.update_selected_points(im)

    def change_working_point(self, wp):
        self.working_point = wp
        self.update_selected_points(1)
        self.update_selected_points(2)

    def changeImage1(self, newfig):
        print("change 1 to ", newfig)
        self.img1_who = newfig
        self.im1.axes.clear()
        self.im1.axes.imshow(self.frames[newfig])

        self.im1.canvas.draw()
        self.plot_possible_points(1)
        self.update_selected_points(1)

    def changeImage2(self, newfig):
        print("change 2 to ", newfig)
        self.img2_who = newfig
        self.im2.axes.clear()
        self.im2.axes.imshow(self.frames[newfig])
        self.im2.canvas.draw()
        self.plot_possible_points(2)
        self.update_selected_points(2)

    def clear_matches(self):
        print('Erasing current match matrix')
        self.Nset = 54
        self.point_matches = -1 * np.ones((self.Nframes, self.Nset), dtype=np.int)
        self.update_selected_points(1)
        self.update_selected_points(2)

    def save_matches(self):
        print('Saving current match matrix')
        np.savez(self.params['root_directory'] + '/points/matches.npz', matches=self.point_matches)

    def parseConfig(self, configFile=''):
        ## Opens dialog box if no config file name is provided.
        if configFile == '':
            configFile = str(QFileDialog.getOpenFileName())

        self.params = simplejson.load(open(configFile))

        self.Nframes = self.params['last_frame'] - self.params['first_frame'] + 1

        self.points = [
            np.load(self.params['root_directory'] + '/points/%08d.npz' % k)['arr_0'] \
            for k in range(self.Nframes)]

        self.frames = [
            np.asarray(imread(self.params['root_directory'] + '/frames/' +
                              self.params['filename_format'] % k))
            for k in range(self.Nframes)]

    def plot_possible_points(self, im):
        if im == 1:
            frame = self.img1_who
            self.line1, = self.im1.axes.plot(self.points[frame][:, 0],
                                             self.points[frame][:, 1],
                                             'bo', picker=3)
            self.mark1, = self.im1.axes.plot([], [],
                                             'ys', picker=3)
            self.wrk1, = self.im1.axes.plot([], [],
                                            'rs', picker=3)
            self.im1.canvas.draw()
        elif im == 2:
            frame = self.img2_who
            self.line2, = self.im2.axes.plot(self.points[frame][:, 0],
                                             self.points[frame][:, 1],
                                             'bo', picker=3)
            self.mark2, = self.im2.axes.plot([], [],
                                             'ys', picker=3)
            self.wrk2, = self.im2.axes.plot([], [],
                                            'rs', picker=3)
            self.im2.canvas.draw()

    def update_selected_points(self, im):
        if im == 1:
            frame = self.img1_who
            sel = self.point_matches[frame]
            sel = sel[sel >= 0]
            if sel == []:
                self.mark1.set_data([], [])
            else:
                self.mark1.set_data(self.points[frame][sel, 0],
                                    self.points[frame][sel, 1])
            sel = self.point_matches[frame, self.working_point]
            if sel == -1:
                self.wrk1.set_data([], [])
            else:
                self.wrk1.set_data(self.points[frame][sel, 0],
                                   self.points[frame][sel, 1])
            self.im1.canvas.draw()
        elif im == 2:
            frame = self.img2_who
            sel = self.point_matches[frame]
            sel = sel[sel >= 0]
            if sel == []:
                self.mark2.set_data([], [])
            else:
                self.mark2.set_data(self.points[frame][sel, 0],
                                    self.points[frame][sel, 1])
            sel = self.point_matches[frame, self.working_point]
            if sel == -1:
                self.wrk2.set_data([], [])
            else:
                self.wrk2.set_data(self.points[frame][sel, 0],
                                   self.points[frame][sel, 1])

            self.im2.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        dmw = DesignerMainWindow(sys.argv[1])
    else:
        dmw = DesignerMainWindow('')
    dmw.show()
    sys.exit(app.exec_())


## Local variables:
## python-indent: 2
## end:
