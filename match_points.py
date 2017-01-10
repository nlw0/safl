#!/usr/bin/python2.7

import os.path
import scipy.ndimage
import simplejson
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, qApp
from pylab import *

from point_ui import Ui_MainWindow


class DesignerMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, configFile='', parent=None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)

        self.params = {}
        self.Nframes = 0
        self.points = []
        self.frames = []
        self.change_image_semaphore = False
        self.parseConfig(configFile)

        matches_file = self.params['root_directory'] + '/points/matches.npz'

        try:
            self.point_matches = np.load(matches_file)['matches']
            self.Nset = self.point_matches.shape[1]
            print('Read existing point match file exists.')
        except IOError:
            print('No point match file exists.')
            self.Nset = 54
            self.point_matches = -1 * np.ones((self.Nframes, self.Nset), dtype=np.int)

        self.img1_who = 0
        self.img2_who = 1
        self.img1 = self.im1.axes.imshow(self.frames[0], cmap=cm.bone, vmin=-50, vmax=50)
        self.line1 = self.im1.axes.plot([], [], 'bo', picker=3)[0]
        self.mark1 = self.im1.axes.plot([], [], 'ys')[0]
        self.wrk1 = self.im1.axes.plot([], [], 'rs')[0]
        self.img2 = self.im2.axes.imshow(self.frames[1], cmap=cm.bone, vmin=-50, vmax=50)
        self.line2 = self.im2.axes.plot([], [], 'bo', picker=3)[0]
        self.mark2 = self.im2.axes.plot([], [], 'ys')[0]
        self.wrk2 = self.im2.axes.plot([], [], 'rs')[0]

        self.img1IndexBox.setMinimum(0)
        self.img1IndexBox.setMaximum(self.Nframes - 1)
        self.img1IndexBox.setValue(self.params['first_frame'])
        self.img2IndexBox.setMinimum(0)
        self.img2IndexBox.setMaximum(self.Nframes - 1)
        self.img2IndexBox.setValue(self.params['first_frame'] + 1)

        self.setIndexBox.setMinimum(0)
        self.setIndexBox.setMaximum(self.Nset)
        self.setIndexBox.setValue(0)
        self.working_point = 0

        self.actionOpen.triggered.connect(self.parseConfig)
        self.actionQuit.triggered.connect(self.quit)
        self.actionSave.triggered.connect(self.save_data)
        self.actionClear_matches.triggered.connect(self.clear_matches)
        self.setIndexBox.valueChanged.connect(self.change_working_point)
        self.img1IndexBox.valueChanged.connect(self.changeImage1)
        self.img2IndexBox.valueChanged.connect(self.changeImage2)
        self.im1.canvas.mpl_connect('pick_event', self.onpick)
        self.im2.canvas.mpl_connect('pick_event', self.onpick)
        # self.im1.canvas.mpl_connect('button_press_event', self.onclick)
        # self.im2.canvas.mpl_connect('button_press_event', self.onclick)
        self.im1.canvas.mpl_connect('key_press_event', self.onkey)
        self.im2.canvas.mpl_connect('key_press_event', self.onkey)

        self.img1IndexBox.setSingleStep(1)
        self.img2IndexBox.setSingleStep(1)
        self.changeImage1(self.img1IndexBox.value())
        self.changeImage2(self.img2IndexBox.value())

        self.did_pick = False

    def quit(self):
        self.save_data()
        qApp.quit()

    # def onclick(self, event):
    #     # Test if something was just picked from this click. In this
    #     # case, do nothing.
    #     if self.did_pick:
    #         self.did_pick = False
    #         return
    #
    #     # Not a left click, just ignore
    #     if event.button != 1:
    #         return
    #
    #         # if event.canvas == self.im1.canvas:
    #         #     self.point_matches[self.img1_who, self.working_point] = -1
    #         #     self.update_selected_points(1)
    #         # elif event.canvas == self.im2.canvas:
    #         #     self.point_matches[self.img2_who, self.working_point] = -1
    #         #     self.update_selected_points(2)

    def onpick(self, event):
        # Not a left click, just ignore
        if event.mouseevent.button == 3 and (event.artist == self.line1 or event.artist == self.line2):
            frame = self.img1_who if event.artist == self.line1 else self.img2_who if event.artist == self.line2 else -1
            im = 1 if event.artist == self.line1 else 2 if event.artist == self.line2 else -1
            self.delete_point(frame, event.ind[0])
            self.update_plotted_points(im)

        elif event.mouseevent.button == 1 and (event.artist == self.line1 or event.artist == self.line2):
            frame = self.img1_who if event.artist == self.line1 else self.img2_who if event.artist == self.line2 else -1
            im = 1 if event.artist == self.line1 else 2 if event.artist == self.line2 else -1
            self.toggle_point_label(frame, self.working_point, event.ind[0])

            if self.autoFeed.isChecked():
                self.setIndexBox.setValue((self.working_point + 1) % self.Nset)
            else:
                self.update_selected_points(im)

        self.save_data()

    def toggle_point_label(self, frame, label, point_index):
        self.point_matches[frame, label] = -1 if self.point_matches[frame, label] == point_index else point_index

    def delete_point(self, frame, point_index):
        print("Delete point frm {} idx {}".format(frame, point_index))
        self.points[frame] = vstack((self.points[frame][0:point_index], self.points[frame][point_index + 1:]))
        for j in range(len(self.point_matches[frame])):
            if self.point_matches[frame, j] > point_index:
                self.point_matches[frame, j] -= 1
            elif self.point_matches[frame, j] == point_index:
                self.point_matches[frame, j] = -1

    def onkey(self, event):
        if event.key != 'q':
            return

        if event.canvas == self.im1.canvas and event.xdata is not None and event.ydata is not None:
            print('Create point at image {} ({},{})'.format(self.img1_who, event.xdata, event.ydata))
            self.points[self.img1_who] = vstack((self.points[self.img1_who], [[event.xdata, event.ydata]]))
            self.update_plotted_points(1)

        elif event.canvas == self.im2.canvas and event.xdata is not None and event.ydata is not None:
            print('Create point at image {} ({},{})'.format(self.img2_who, event.xdata, event.ydata))
            self.points[self.img2_who] = vstack((self.points[self.img2_who], [[event.xdata, event.ydata]]))
            self.update_plotted_points(2)

        self.save_data()

    def change_working_point(self, wp):
        self.working_point = wp
        self.update_selected_points(1)
        self.update_selected_points(2)

    def changeImage1(self, frame):
        print("Got change image 1 event")
        self.do_change_image(1, frame)

    def changeImage2(self, frame):
        print("Got change image 2 event")
        self.do_change_image(2, frame)

    def do_change_image(self, im, newframe):
        print("change {} to {} {}".format(im, newframe, self.change_image_semaphore))
        if im == 1:
            self.img1_who = newframe
            self.img1.set_data(self.frames[newframe])
            self.im1.canvas.draw_idle()
            self.update_plotted_points(1, async_draw=True)
        elif im == 2:
            self.img2_who = newframe
            self.img2.set_data(self.frames[newframe])
            self.im2.canvas.draw_idle()
            self.update_plotted_points(2, async_draw=True)

    def clear_matches(self):
        print('Erasing current match matrix')
        self.Nset = 54
        self.point_matches = -1 * np.ones((self.Nframes, self.Nset), dtype=np.int)
        self.update_selected_points(1)
        self.update_selected_points(2)

    def save_data(self):
        print('Saving current match matrix')
        np.savez(self.params['root_directory'] + '/points/matches.npz', matches=self.point_matches)
        print('Saving current point coordinates')
        for k in range(self.Nframes):
            points_filename = self.get_points_filename(k)
            np.savez(points_filename, self.points[k])

    def parseConfig(self, config_filename=''):
        print("Reading set config file")
        # Opens dialog box if no config file name is provided.
        if config_filename == '':
            config_filename, _ = QFileDialog.getOpenFileName(parent=self, caption="Set configuration file",
                                                             filter="*.json")
            print(config_filename)

        self.params = simplejson.load(open(config_filename))

        self.Nframes = self.params['last_frame'] - self.params['first_frame'] + 1

        self.points = [self.get_frame_points(k) for k in range(self.Nframes)]

        # self.frames = [np.asarray(imread(self.frame_filename(k))) for k in range(self.Nframes)]

        self.frames = [self.get_frame_image(k) for k in range(self.Nframes)]

    def get_frame_image(self, k):
        # return np.asarray(imread(self.frame_filename(k)))
        print("Reading image {}".format(k))
        frm = scipy.ndimage.imread(self.frame_filename(k), 'L')
        grm = scipy.ndimage.gaussian_filter(frm, 50.0)
        return np.asarray(frm - grm)

    def get_frame_points(self, frame_number):
        points_filename = self.get_points_filename(frame_number)
        if os.path.isfile(points_filename):
            return np.load(points_filename)['arr_0']
        else:
            return zeros((0, 2), dtype=float)

    def get_points_filename(self, frame_number):
        return self.params['root_directory'] + '/points/%08d.npz' % frame_number

    def frame_filename(self, frame_number):
        return self.params['root_directory'] + '/frames/' + self.params['filename_format'] % frame_number

    def update_plotted_points(self, im, async_draw=False):
        if im != 1 and im != 2:
            return

        frame = self.img1_who if im == 1 else self.img2_who if im == 2 else None
        line = self.line1 if im == 1 else self.line2 if im == 2 else None
        line.set_data(self.points[frame][:, 0], self.points[frame][:, 1])

        self.update_selected_points(im, async_draw)

    def update_selected_points(self, im, async_draw=False):
        if im != 1 and im != 2:
            return

        frame = self.img1_who if im == 1 else self.img2_who if im == 2 else -1
        imx = self.im1 if im == 1 else self.im2 if im == 2 else None
        mark = self.mark1 if im == 1 else self.mark2 if im == 2 else None
        wrk = self.wrk1 if im == 1 else self.wrk2 if im == 2 else None

        frame_selections = self.point_matches[frame]
        wp_sel = mgrid[0:len(frame_selections)] == self.working_point

        sel = frame_selections[(frame_selections > -1) * (wp_sel != True)]
        mark.set_data(self.points[frame][sel, 0], self.points[frame][sel, 1])

        sel = frame_selections[(frame_selections > -1) * wp_sel]
        wrk.set_data(self.points[frame][sel, 0], self.points[frame][sel, 1])

        if async_draw:
            imx.canvas.draw_idle()
        else:
            imx.canvas.draw_idle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        dmw = DesignerMainWindow(sys.argv[1])
    else:
        dmw = DesignerMainWindow('')
    dmw.show()
    sys.exit(app.exec_())
