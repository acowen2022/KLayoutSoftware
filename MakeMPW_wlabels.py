
# Enter your Python code here
import pya
import klayout.db as db
import math, random
import os, glob
class LayoutDialog(pya.QDialog):
  """
  This class implements a dialog with a screenshot display area and a
  screenshot button
  """
  
  def button_clicked(self, checked):
    """ Event handler: "Screenshot" button clicked """

    view = pya.Application.instance().main_window().current_view()
    DoLayout(dirname, self.textbox.text, self.textbox2.text)


  def __init__(self, parent = None):
    """ Dialog constructor """
    
    super(LayoutDialog, self).__init__()

    self.setWindowTitle("Screenshot Saver")

    self.resize(400, 120)

    layout = pya.QVBoxLayout(self)
    self.setLayout(layout)

    self.image = pya.QLabel("Enter the X and Y pitch below.", self)
    layout.addWidget(self.image)

    button = pya.QPushButton('Complete Layout', self)
    button.setFont(pya.QFont('Times', 18, pya.QFont.Bold))
    layout.addWidget(button)
    
    # Single-line textbox (use pya.QTextEdit for multi-line)
    self.textbox = pya.QLineEdit(self)
    self.textbox.placeholderText = "X Pitch"
    layout.addWidget(self.textbox)
    self.textbox2 = pya.QLineEdit(self)
    self.textbox2.placeholderText = "Y Pitch"
    layout.addWidget(self.textbox2)
        
    # attach the event handler
    button.clicked(self.button_clicked)

def add_text(str1, layer, mag, x, y, top_cell, ly):
# Define the PCell parameters
  params = {
    "text": str1,
    "layer": db.LayerInfo(layer, 0),  # Target layer (Layer 1, Datatype 0)
    "mag": mag,                  # Magnification (scaling factor)
    # Optional parameters:
    # "font_name": "Default",
    # "inverse": False,
    # "bias": 0.0,
    # "cspacing": 0.0,
    # "lspacing": 0.0,
    # "eff_cw": 0.0,
    # "eff_ch": 0.0,
    # "eff_lw": 0.0,
    # "eff_dr": 0.0,
    # "font": 0
  }

# Create the PCell variant and insert an instance into the top cell
  pcell = ly.create_cell("TEXT", "Basic", params)
  trans = db.DTrans(db.DTrans.R0, x, y)  # Place at (x, y)
  top_cell.insert(db.DCellInstArray(pcell.cell_index(), trans))

def DoLayout(dirname, dx, dy):
  spacing = 1000.0
  y = 0.0
  ly = db.Layout()
  top_cell = ly.create_cell("NEWTOP")  
  label_cell = ly.create_cell("wafer_labels")
  #units in microns
#  dx = 11150
#  dy = 11150
  dx = float(dx)
  dy = float(dy)
  wafer_bead = 5000
  od = 75000-wafer_bead # outer_diameter
  flat_y = 69000

  floor_y = flat_y - wafer_bead
  y = floor_y-(dy/2) # put on grid
  num_y = math.floor(y/(dy/2))
  y = -num_y/2*dy
# y=-math.sqrt((floor_y*floor_y)-(dx/2*dx/2))
# y=(math.floor(y/(dy/2))*dy/2)+dy
  x =-math.floor(math.sqrt((od*od) - (floor_y*floor_y)))
  num_x = math.floor(-2*x/dx)
  num_y = 0
  x = -((num_x*dx)/2)+dx/2
  odd_even = num_x %2
# x=-dx/2
# num_x = 1
  max_x = -x
  max_dies = math.floor(od*2/dx)
  if (-max_dies%2) != odd_even: max_dies=max_dies-1
  xx=math.floor((max_dies-num_x)/2)

  cellnum=0
  target_cell = []
  for filename in glob.glob(os.path.join(dirname, '*.[gG][dD][sS]')):
    ly_import = db.Layout()
    ly_import.read(filename)
    imported_top_cell = ly_import.top_cell()
    print(imported_top_cell.name)
    target_cell.append(ly.create_cell(imported_top_cell.name))
    target_cell[cellnum].copy_tree(imported_top_cell)
    ly_import._destroy()
    cellnum = cellnum+1

  while y < od - dy/2:
    # frees the resources of the imported layout
#    dx = target_cell.dbbox().width() + spacing  
#    dy = target_cell.dbbox().height() + spacing
          k = random.randint(0, cellnum-1)
          inst = db.DCellInstArray(target_cell[k].cell_index(), db.DTrans(db.DVector(x, y)))
  
          top_cell.insert(inst)
          str1 = "COL" + str(xx) + " ROW" + str(num_y)
          print(target_cell[k].name, (xx), num_y, str1)
          add_text(str1, 10, 100, x, y, label_cell, ly)
          if x >= max_x:
             y=y+dy
             num_y=num_y+1
             x=-math.sqrt((od*od)-(y*y))
             num_x = math.floor(2*x/dx)+2
             if (-num_x%2) != odd_even: num_x=num_x+1
             xx=math.floor((max_dies+num_x)/2)
#          x = num_x*dx/2
             x = ((num_x*dx)/2)+dx/2
             max_x = -x
          else: 
             x=x+dx
             xx=xx+1

  ly.write("C:/Users/allen/KLayout/tmplayouts/t28.gds")
  
    
# dirname = "C:/Users/allen/KLayout/MPW/Poly140/"
dirname = pya.QFileDialog.getExistingDirectory()

# Instantiate the dialog and make it visible initially.
# Passing the main_window will make it stay on top of the main window.
dialog = LayoutDialog(pya.Application.instance().main_window())
dialog.windowTitle = "Input Box"
dialog.show()


