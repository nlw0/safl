from PyQt4 import QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import math

class MplWidget(QtGui.QWidget):

  def __init__(self, parent = None):
    QtGui.QWidget.__init__(self, parent)
    
    self.fig = Figure()
    self.canvas = FigureCanvas(self.fig)
    self.canvas.setParent(self)
    self.canvas.mpl_connect('scroll_event',self.onWheel)
    self.canvas.mpl_connect('button_press_event', self.start_pan)
    self.canvas.mpl_connect('button_release_event', self.pan)
    
    self.axes = self.fig.add_subplot(111)

    # self.mpl_toolbar = NavigationToolbar(self.canvas, self)

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.canvas)
    #vbox.addWidget(self.mpl_toolbar)
    self.setLayout(vbox)

  def start_pan(self, event):
    if event.button == 3:
      self.dragx,self.dragy = event.x,event.y
    
  def pan(self, event):
    if event.button ==3:
      diffx,diffy  = self.dragx-event.x,self.dragy-event.y      
      x1,x2=self.axes.get_xlim()
      y1,y2=self.axes.get_ylim()
      self.axes.set_xlim(x1+diffx,x2+diffx)
      self.axes.set_ylim(y1-diffy,y2-diffy)
      self.dragx,self.dragy = event.x,event.y      
      self.canvas.draw()
  
  def _rescale(self,lo,hi,step,pt=None,bal=None,scale='linear'):
    """
    Rescale (lo,hi) by step, returning the new (lo,hi)
    The scaling is centered on pt, with positive values of step
    driving lo/hi away from pt and negative values pulling them in.
    If bal is given instead of point, it is already in [0,1] coordinates.

    This is a helper function for step-based zooming.
    """
    # Convert values into the correct scale for a linear transformation
    # TODO: use proper scale transformers
    if scale=='log':
      lo,hi = math.log10(lo),math.log10(hi)
      if pt is not None: pt = math.log10(pt)

    # Compute delta from axis range * %, or 1-% if percent is negative
    if step > 0:
      delta = float(hi-lo)*step/100
    else:
      delta = float(hi-lo)*step/(100-step)

    # Add scale factor proportionally to the lo and hi values, preserving the
    # point under the mouse
    if bal is None:
      bal = float(pt-lo)/(hi-lo)
    lo = lo - bal*delta
    hi = hi + (1-bal)*delta

    # Convert transformed values back to the original scale
    if scale=='log':
      lo,hi = math.pow(10.,lo),math.pow(10.,hi)

    return (lo,hi)

  def onWheel(self,event):
    """
    Process mouse wheel as zoom events
    """
    ax = event.inaxes

    # Older versions of matplotlib do not have event.step defined
    try:
        step = event.step
    except:
        if event.button == 'up':
            step = 1
        else:
            step = -1   

    # If in plot, use the xdata, ydata as the center point
    # If not in plot, check if we are in a plot axis
    if ax == None:
        # Event not on plot: check if it happened in an axis
        xdata,ydata = None,None
        x,y = event.x,event.y
        axes = event.canvas.figure.get_axes()
        for ax in axes:
            inx,_ = ax.xaxis.contains(event)
            if inx:
                xdata,_ = ax.transData.inverted().transform_point((x,y))
                break
            iny,_ = ax.yaxis.contains(event)
            if iny:
                _,ydata = ax.transData.inverted().transform_point((x,y))
                break
        else:
            ax = None
    else:
        xdata,ydata = event.xdata,event.ydata
   
    # Axis scrolling requires remapping the axis limits
    if xdata is not None:
        lo,hi = ax.get_xlim()
        lo,hi = self._rescale(lo,hi,step,pt=xdata,scale=ax.get_xscale())
        ax.set_xlim((lo,hi))

    if ydata is not None:
        lo,hi = ax.get_ylim()
        lo,hi = self._rescale(lo,hi,step,pt=ydata,scale=ax.get_yscale())
        ax.set_ylim((lo,hi))

    if xdata is not None or ydata is not None:
        event.canvas.draw_idle()
        
 
        