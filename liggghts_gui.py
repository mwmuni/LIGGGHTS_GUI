#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import random
from trimesh import load_mesh
import subprocess
import OpenGL
from OpenGL import GL
import pickle
from os.path import basename
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import OpenGL.GLU
from OpenGL.GLU import gluLookAt
from PyQt4 import QtCore, QtGui, uic, QtOpenGL

qtCreatorFile = 'resources/LIGGGHTS_DEM.ui'  # ui file

(Ui_MainWindow, QtBaseClass) = uic.loadUiType(qtCreatorFile)


def main():
    global app
    app = QtGui.QApplication(sys.argv)
    window = PyQtLink()
    window.show()
    app.exec_()

class PyQtLink(QtGui.QMainWindow, Ui_MainWindow, QtGui.QWidget):

    global app

    def __init__(self):
        QtGui.QMainWindow.__init__(self)  # Initialize the main windows
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # GUI Theme; options = {"plastique", "cde", "motif", "sgi", "windows",
        # "cleanlooks", "mac"}
        app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))
        self.ini_vars()

        self.glWidget = GLWidget()

        self.xSlider = self.createSlider()
        self.ySlider = self.createSlider()
        self.zSlider = self.createSlider()
        self.xSlider.valueChanged.connect(self.glWidget.setXRotation)
        self.glWidget.xRotationChanged.connect(self.xSlider.setValue)
        self.ySlider.valueChanged.connect(self.glWidget.setYRotation)
        self.glWidget.yRotationChanged.connect(self.ySlider.setValue)
        self.zSlider.valueChanged.connect(self.glWidget.setZRotation)
        self.glWidget.zRotationChanged.connect(self.zSlider.setValue)
        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        central = self.ogl
        central.setLayout(mainLayout)

        self.xSlider.setValue(0)
        self.ySlider.setValue(0)
        self.zSlider.setValue(0)

        self.btn_geometry_autofit.clicked.connect(self.autofit)
        self.pushButton_Browse.clicked.connect(self.browse)
        self.btn_geometry_stl.clicked.connect(self.openstl)
        self.tree_casesetup.itemClicked.connect(self.treecasesetup)
        self.tree_geometry.itemClicked.connect(self.treegeometry)
        self.btn_terminal.clicked.connect(self.terminal)
        self.btn_cube.clicked.connect(self.btn_cube_clicked)
        self.btn_sphere.clicked.connect(self.btn_sphere_clicked)
        self.btn_cylinder.clicked.connect(self.btn_cylinder_clicked)
        self.btn_plane.clicked.connect(self.btn_plane_clicked)
        self.btn_addinsertion.clicked.connect(self.btn_addinsertion_clicked)
        self.btn_delete_insertion.clicked.connect(self.btn_delete_insertion_clicked)
        self.btn_addPSD.clicked.connect(self.btn_addPSD_clicked)
        self.btn_removePSD.clicked.connect(self.btn_removePSD_clicked)
        self.btn_zoom_in.clicked.connect(self.btn_zoom_in_clicked)
        self.btn_zoom_out.clicked.connect(self.btn_zoom_out_clicked)
        self.btn_makefile.clicked.connect(self.fileGen)
        self.btn_saveas.clicked.connect(self.saveas)
        self.btn_open.clicked.connect(self.openFile)
        self.btn_addptcl.clicked.connect(self.btn_addptcl_clicked)
        self.btn_delptcl.clicked.connect(self.btn_delptcl_clicked)
        self.btn_add_mm_type.clicked.connect(self.btn_add_mm_type_clicked)
        self.run_prog.clicked.connect(self.run_prog_clicked)
        self.btn_solve_paraview.clicked.connect(self.btn_solve_paraview_clicked)
        self.btn_mm_del.clicked.connect(self.btn_mm_del_clicked)
        self.btn_edit_script.clicked.connect(self.btn_edit_script_clicked)
        self.btn_import_ins_mesh.clicked.connect(self.btn_import_ins_mesh_clicked)
        self.btn_log_file.clicked.connect(self.btn_log_file_clicked)
        self.pushButton_New.clicked.connect(self.new_button_clicked)
        self.pushButton_Save.clicked.connect(self.save)
        self.connect(self.pushButton_Support, QtCore.SIGNAL("clicked()"), self.popupSupport)

        self.btn_x_align.clicked.connect(self.btn_x_align_clicked)
        self.btn_y_align.clicked.connect(self.btn_y_align_clicked)
        self.btn_z_align.clicked.connect(self.btn_z_align_clicked)
        self.btn_x_align_neg.clicked.connect(self.btn_x_align_neg_clicked)
        self.btn_y_align_neg.clicked.connect(self.btn_y_align_neg_clicked)
        self.btn_z_align_neg.clicked.connect(self.btn_z_align_neg_clicked)

        self.chk_meshes_cm.stateChanged.connect(self.savemeshproperties)
        self.chk_dumpmesh.stateChanged.connect(self.savemeshproperties)
        self.chk_meshes_sv.stateChanged.connect(self.chk_meshes_sv_clicked)
        self.chk_meshes_sav.stateChanged.connect(self.chk_meshes_sav_clicked)
        self.chk_meshes_mm.stateChanged.connect(self.chk_meshes_mm_clicked)
        self.chk_meshes_sw.stateChanged.connect(self.savemeshproperties)
        
        self.radio_mpi.toggled.connect(self.flip_mpi)
        
        self.actionSupport.triggered.connect(self.popupSupport)
        self.actionAbout.triggered.connect(self.popupAbout)

        self.trolltechYellow = QtGui.QColor.fromCmykF(.00, .02, .20, .0)
        self.trolltechGrey = QtGui.QColor.fromCmykF(.4, .4, .4, 0)

        # If the value changes, the method will be called

        self.spnbox_geometry_contacttypes_totalgranulartypes\
            .valueChanged.connect(self.addContactTypes)
        self.spnbox_geometry_contacttypes_totalmeshtypes\
            .valueChanged.connect(self.addContactTypes)
        self.spnbox_insertion_fraction.valueChanged.connect(self.savePSD)

        self.combo_insertionindex.currentIndexChanged.connect(
                self.loadInsertionSettings)
        self.spnbox_psd.valueChanged.connect(
                self.updateparticletypelist)

        self.spnbox_totalmass.valueChanged.connect(
                self.insertionmasssave)
        self.spnbox_massrate.valueChanged.connect(
                self.insertionmasssave)
        self.spnbox_insertion_mass_x.valueChanged.connect(
                self.insertionmasssave)
        self.spnbox_insertion_mass_y.valueChanged.connect(
                self.insertionmasssave)
        self.spnbox_insertion_mass_z.valueChanged.connect(
                self.insertionmasssave)
        self.spnbox_insertion_extrude.valueChanged.connect(
                self.insertionmasssave)

        self.spnbox_granulartypeindex.valueChanged.connect(
                self.updateparticlelist)

        self.line_youngsmodulus.textChanged.connect(
                self.saveMaterialData)
        self.spnbox_poissonsratio.valueChanged.connect(
                self.saveMaterialData)
        self.spnbox_density.valueChanged.connect(
                self.savePSD)
        self.spnbox_diameter.valueChanged.connect(
                self.savePSD)

        self.mm_riggle_origin_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_origin_y.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_origin_z.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_axis_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_axis_y.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_axis_z.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_period.valueChanged.connect(
                self.savemeshproperties)
        self.mm_riggle_amplitude.valueChanged.connect(
                self.savemeshproperties)
        
        self.mm_rotate_origin_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_origin_y.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_origin_z.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_axis_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_axis_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_axis_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_rotate_period.valueChanged.connect(
                self.savemeshproperties)
        
        self.mm_velocity_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_velocity_y.valueChanged.connect(
                self.savemeshproperties)
        self.mm_velocity_z.valueChanged.connect(
                self.savemeshproperties)
        
        self.mm_amplitude_x.valueChanged.connect(
                self.savemeshproperties)
        self.mm_amplitude_y.valueChanged.connect(
                self.savemeshproperties)
        self.mm_amplitude_z.valueChanged.connect(
                self.savemeshproperties)
        self.mm_wiggle_period.valueChanged.connect(
                self.savemeshproperties)

        self.spnbox_meshes_sv_x.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sv_y.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sv_z.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_x.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_y.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_z.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_a_x.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_a_y.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_a_z.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_sav_omega.valueChanged.connect(self.savemeshproperties)
        self.spnbox_meshes_starttime.valueChanged.connect(
                self.savemeshproperties)

        self.combo_ced.currentIndexChanged.connect(self.listcedupdate)
        self.combo_cor.currentIndexChanged.connect(self.listcorupdate)
        self.combo_kwear.currentIndexChanged.connect(self.listkwearupdate)
        self.combo_particlefriction.currentIndexChanged \
            .connect(self.listparticleupdate)
        self.combo_rollingfriction.currentIndexChanged \
            .connect(self.listrollingupdate)
        self.combo_meshes_ct.currentIndexChanged.connect(
                self.savemeshproperties)
        self.combo_particlelist.currentIndexChanged.connect(
                self.updateparticletype)
        self.combo_conty.currentIndexChanged.connect(
                self.loadMaterialData)
        self.combo_meshes_ct.currentIndexChanged.connect(
                self.savemeshproperties)

        self.line_ced.textChanged.connect(self.changecedlist)
        self.line_cor.textChanged.connect(self.changecorlist)
        self.line_kwear.textChanged.connect(self.changekwearlist)
        self.line_particlefriction.textChanged.connect(self.changeparticlelist)
        self.line_rollingfriction.textChanged.connect(self.changerollinglist)
        
        self.list_mm_type.itemClicked.connect(self.list_mm_type_clicked)

        self.tree_geometry.viewport().installEventFilter(self)

        self.ogl.installEventFilter(self)

        self.testPage.setEnabled(False)

        self.setWindowTitle('Liggghts GUI')

    def ini_vars(self):
        self.gmt = []
        self.origPath = []
        self.currentFile = None
        self.currentDir = None
        global mesh_ref
        mesh_ref = []
        global ins_mesh_ref
        ins_mesh_ref = []
        self.meshProperties = []
        self.loading = False
        self.stlFilesLoaded = []
        self.insertionList = []
        self.objHolder = self.tree_geometry.topLevelItem(1)
        self.currentMeshType = ''
        self.fileName = ''
        self.mmList = []
        self.totalTypes = 2
        self.gmt = [['1e7', 0.3] for x in range(0, self.totalTypes)]
        self.materialdataini()
        self.addContactTypes() 

    def addContactTypes(self):
        self.meshTypeData = []
        self.totalTypes = \
            self.spnbox_geometry_contacttypes_totalgranulartypes.value() \
            + self.spnbox_geometry_contacttypes_totalmeshtypes.value()
        self.line_geometry_contacttypes_totaltypes.setText(str(self.totalTypes))
        self.gmt = [['1e7', 0.3] for x in range(0, self.totalTypes)]
        self.combo_ced.clear()
        self.combo_cor.clear()
        self.combo_kwear.clear()
        self.combo_particlefriction.clear()
        self.combo_rollingfriction.clear()
        mtx = [['' for y in range(self.totalTypes+1)] for x in range(self.totalTypes+1)]
        self.combo_conty.clear()
        for x in range(0, self.totalTypes):
            self.combo_conty.addItem(str(x+1))
        self.loading = True
        self.combo_meshes_ct.clear()
        for x in range(self.spnbox_geometry_contacttypes_totalgranulartypes.value(), self.totalTypes):
            self.combo_meshes_ct.addItem(str(x+1))
        self.loading = False
        for x in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                mtx[x][y] = str(x+1)+'_'+str(y+1)
                self.combo_ced.addItem(mtx[x][y])
                self.combo_cor.addItem(mtx[x][y])
                self.combo_kwear.addItem(mtx[x][y])
                self.combo_particlefriction.addItem(mtx[x][y])
                self.combo_rollingfriction.addItem(mtx[x][y])
        self.loading = True
        if len(self.meshProperties) > 0:
            for n in range(0, len(self.meshProperties)):
                if self.meshProperties[n][1] > self.spnbox_geometry_contacttypes_totalmeshtypes.value():
                    self.meshProperties[n][1] = 0
                    if n == self.currentMeshType:
                        self.combo_meshes_ct.setCurrentIndex(0)
        self.loading = False
        self.contactParams = [[0.2 for x in range(0, self.totalTypes**2)]]  # COR
        self.contactParams.append([0.5 for x in range(0, self.totalTypes**2)])  # ff
        self.contactParams.append([0.3 for x in range(0, self.totalTypes**2)])  # frf
        self.contactParams.append([0.0 for x in range(0, self.totalTypes**2)])  # CED
        self.contactParams.append([1.0 for x in range(0, self.totalTypes**2)])  # KWear
        self.insertionList = []
        self.combo_insertionindex.setCurrentIndex(0)
        self.stack_insertionsettings.setCurrentIndex(0)
        self.listcedupdate()
        self.listcorupdate()
        self.listkwearupdate()
        self.listparticleupdate()
        self.listrollingupdate()
        self.loadMaterialData()

    def autofit(self):
        global mesh_ref
        min_x = min_y = min_z = None
        max_x = max_y = max_z = None

        if len(mesh_ref) > 0:
            for meshes in range(0, len(mesh_ref)):
                v = mesh_ref[meshes][1].vertices
                for index in range(0, len(v)):
                    if min_x > v[index][0] or min_x is None:
                        min_x = v[index][0]
                    if min_y > v[index][1] or min_y is None:
                        min_y = v[index][1]
                    if min_z > v[index][2] or min_z is None:
                        min_z = v[index][2]
                    if max_x < v[index][0] or max_x is None:
                        max_x = v[index][0]
                    if max_y < v[index][1] or max_y is None:
                        max_y = v[index][1]
                    if max_z < v[index][2] or max_z is None:
                        max_z = v[index][2]

            shift_x = (max_x - min_x)*0.05
            min_x -= shift_x
            max_x += shift_x

            shift_y = (max_y - min_y)*0.05
            min_y -= shift_y
            max_y += shift_y

            shift_z = (max_z - min_z)*0.05
            min_z -= shift_z
            max_z += shift_z

            self.boundary_min_x.setValue(min_x)
            self.boundary_min_y.setValue(min_y)
            self.boundary_min_z.setValue(min_z)
    
            self.boundary_max_x.setValue(max_x)
            self.boundary_max_y.setValue(max_y)
            self.boundary_max_z.setValue(max_z)
        else:
            self.boundary_min_x.setValue(0.00)
            self.boundary_min_y.setValue(0.00)
            self.boundary_min_z.setValue(0.00)
    
            self.boundary_max_x.setValue(0.00)
            self.boundary_max_y.setValue(0.00)
            self.boundary_max_z.setValue(0.00)

    def browse(self):
        subprocess.Popen(['xdg-open',
                         os.path.dirname(os.path.realpath(__file__))])

    def btn_addinsertion_clicked(self):
        self.loading = True
        self.combo_insertionindex.addItem(str(len(self.insertionList)+1))
        self.stack_insertionsettings.setCurrentIndex(1)
        self.insertionList.append([[[]], [-1, None],
                                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])
        self.combo_insertionindex.setCurrentIndex(len(self.insertionList)-1)
        self.loading = True
        self.spnbox_granulartypeindex.setValue(1)
        for n in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            self.insertionList[self.combo_insertionindex.currentIndex()][0][
                     self.spnbox_psd.value()-1].append(
                        [[str(self.combo_insertionindex.currentIndex()+1)+'_'+
                          str(self.spnbox_psd.value())+'_'+'p'+str(n+1)+
                         '_1', 0.0, 0.0, 0.0]])
        self.combo_particlelist.clear()
        for n in range(0, len(self.insertionList[
                self.combo_insertionindex.currentIndex()][
                        0][self.spnbox_psd.value()-1][0])):
            self.combo_particlelist.addItem(
                    self.insertionList[
                            self.combo_insertionindex.currentIndex()][
                                    0][self.spnbox_psd.value()-1][0][n][0])
        self.spnbox_psd.setValue(1)
        adding = 0
        for n in range(0, len(self.insertionList[self.combo_insertionindex.currentIndex()
                          ][0][self.spnbox_psd.value()-1][
                                  self.spnbox_granulartypeindex.value()-1])):
            adding += self.insertionList[self.combo_insertionindex.currentIndex()
                          ][0][self.spnbox_psd.value()-1][
                                  self.spnbox_granulartypeindex.value()-1][n][1]
        self.lbl_PSDFractionTotal.setText(str(adding))
        self.loading = True
        self.resetmassproperties()
        self.loading = False
        self.updateparticletype()

    def btn_delete_insertion_clicked(self):
        if len(self.insertionList) == 0:
            return 0
        else:
            del self.insertionList[self.combo_insertionindex.currentIndex()]
            self.combo_insertionindex.clear()
            if len(self.insertionList) > 0:
                for i in range(len(self.insertionList)):
                    self.combo_insertionindex.addItem(str(i+1))
                self.renewparticlenames()
            else:
                self.stack_insertionsettings.setCurrentIndex(0)

    def btn_add_mm_type_clicked(self):
        LINEAR = 0
        RIGGLE = 1
        ROTATE = 2
        WIGGLE = 3
        n = self.currentMeshType

        if self.combo_mm_type.currentIndex() == LINEAR:
            self.stack_mm.setCurrentIndex(LINEAR+1)
            self.mmList[n].append(LINEAR)
            self.list_mm_type.addItem('Item_'+str(len(self.mmList[self.currentMeshType]))+'_Linear')
            self.meshProperties[n][19].append(self.appendNewMMEntry(LINEAR))
        elif self.combo_mm_type.currentIndex() == RIGGLE:
            self.stack_mm.setCurrentIndex(RIGGLE+1)
            self.mmList[n].append(RIGGLE)
            self.list_mm_type.addItem('Item_'+str(len(self.mmList[self.currentMeshType]))+'_Riggle')
            self.meshProperties[n][19].append(self.appendNewMMEntry(RIGGLE))
        elif self.combo_mm_type.currentIndex() == ROTATE:
            self.stack_mm.setCurrentIndex(ROTATE+1)
            self.mmList[n].append(ROTATE)
            self.list_mm_type.addItem('Item_'+str(len(self.mmList[self.currentMeshType]))+'_Rotate')
            self.meshProperties[n][19].append(self.appendNewMMEntry(ROTATE))
        else:
            self.stack_mm.setCurrentIndex(WIGGLE+1)
            self.mmList[n].append(WIGGLE)
            self.list_mm_type.addItem('Item_'+str(len(self.mmList[self.currentMeshType]))+'_Wiggle')
            self.meshProperties[n][19].append(self.appendNewMMEntry(WIGGLE))

        self.list_mm_type.setCurrentItem(
                self.list_mm_type.item(self.list_mm_type.count()-1))
        self.list_mm_type_clicked(self.list_mm_type.item(
                self.list_mm_type.count()-1))

#        print self.mmList

    def appendNewMMEntry(self, entryType):
        toReturn = ()
        if entryType == 0:
            # Save for linear
            toReturn = (0.00, 0.00, 0.00)
        elif entryType == 1:
            # Save for riggle
            toReturn = (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00)
        elif entryType == 2:
            # Save for rotate
            toReturn = (0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00)
        else:
            # Save for wiggle
            toReturn = (0.00, 0.00, 0.00, 0.00)
        return toReturn

    def btn_addPSD_clicked(self):
        if not self.loading:
            self.loading = True
            self.spnbox_psd.setValue(len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][0])+1)
            self.spnbox_granulartypeindex.setValue(1)
            self.insertionList[self.combo_insertionindex.currentIndex()][0].append(
                    [])
            for n in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
                    self.insertionList[self.combo_insertionindex.currentIndex()][0][
                         self.spnbox_psd.value()-1].append(
                            [[str(self.combo_insertionindex.currentIndex()+1)+'_'+
                              str(self.spnbox_psd.value())+'_'+'p'+str(n+1)+
                             '_1', 0.0, 0.0, 0.0]])
            self.combo_particlelist.clear()
            for n in range(0, len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1])):
                self.combo_particlelist.addItem(
                        self.insertionList[
                                self.combo_insertionindex.currentIndex()][0][
                                        self.spnbox_psd.value()-1][
                                                self.spnbox_granulartypeindex.value()-1][n][0])
            self.lbl_PSDFractionTotal.setText("0.0")
            self.loading = False
            self.updateparticletype()

    def btn_cube_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(2)

    def btn_cylinder_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(4)

    def btn_addptcl_clicked(self):
        self.insertionList[
                self.combo_insertionindex.currentIndex()][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1
                ].append([str(self.combo_insertionindex.currentIndex()+1)+'_'+
                    str(self.spnbox_psd.value())+
                    '_p'+str(self.spnbox_granulartypeindex.value())+
                    '_'+str(len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][0][
                    self.spnbox_psd.value()-1][
                    self.spnbox_granulartypeindex.value()-1])+1), 0.0, 0.0, 0.0])
        self.updateparticlelist()
        self.combo_particlelist.setCurrentIndex(
                self.combo_particlelist.count()-1)

    def btn_delptcl_clicked(self):
        if len(self.insertionList[
                self.combo_insertionindex.currentIndex()][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1]) > 1:
            del self.insertionList[
                self.combo_insertionindex.currentIndex()][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1][
                self.combo_particlelist.currentIndex()]
            self.renewparticlenames()

    def btn_edit_script_clicked(self):
        os.system('gedit '+self.currentDir+'script.py')

    def btn_import_ins_mesh_clicked(self):
        global ins_mesh_ref
        self.fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                          'Single File',
                                                          (self.currentDir if self.currentDir != None else '.'),
                                                          '*.stl')
        self.fileName = str(self.fileName)

        if self.fileName not in self.stlFilesLoaded and not repr(self.fileName) == '()' and \
                        os.path.exists(self.fileName):
            tempVar = load_mesh(self.fileName)
            ins_mesh_ref.append([self.fileName, tempVar, [.4, .4, .4, 1.0]])
            self.insertionList[self.combo_insertionindex.currentIndex()][1][0] = 0
            self.insertionList[self.combo_insertionindex.currentIndex()][1][1] = \
                self.fileName
            self.lbl_loaded_insertion.setText(basename(self.fileName))
            self.remove_unused_insertion_faces()
            self.glWidget.initializeGL()
            self.glWidget.updateGL()
            self.glWidget.paintGL()

    def remove_unused_insertion_faces(self):
        global ins_mesh_ref
        toKeep = []
        for n in self.insertionList:
            for m in ins_mesh_ref:
                if n[1][1] == m[0]:
                    toKeep.append(m)
                    break
        ins_mesh_ref = toKeep

    def btn_log_file_clicked(self):
        os.system('gedit log.liggghts')

    def btn_mm_del_clicked(self):
        n = self.currentMeshType
        if len(self.mmList[n]) == 0:
            return 0
        index = self.list_mm_type.indexFromItem(self.list_mm_type.currentItem()).row()
        del self.mmList[n][index]
        del self.meshProperties[n][19][index]
        self.list_mm_type.clear()
        for x in range(0, len(self.mmList[self.currentMeshType])):
            if self.mmList[self.currentMeshType][x] == 0:
                self.list_mm_type.addItem('Item_'+str(x+1)+'_Linear')
            elif self.mmList[self.currentMeshType][x] == 1:
                self.list_mm_type.addItem('Item_'+str(x+1)+'_Riggle')
            elif self.mmList[self.currentMeshType][x] == 2:
                self.list_mm_type.addItem('Item_'+str(x+1)+'_Rotate')
            else:
                self.list_mm_type.addItem('Item_'+str(x+1)+'_Wiggle')
        if len(self.mmList[n]) > 0:
            if index > len(self.mmList[self.currentMeshType]):
                index -= 1
            item = self.list_mm_type.item(index)
            self.list_mm_type.setCurrentItem(item)
            self.list_mm_type_clicked(item)
        else:
            self.stack_mm.setCurrentIndex(0)

    def btn_plane_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(5)

    def btn_removePSD_clicked(self):
        if len(self.insertionList[
                self.combo_insertionindex.currentIndex()][0]) > 1:
            tempInt = self.spnbox_psd.value()
            del self.insertionList[
                self.combo_insertionindex.currentIndex()][0][
                        self.spnbox_psd.value()-1]
            self.spnbox_psd.setValue(tempInt-1)
            self.renewparticlenames()

    def btn_solve_paraview_clicked(self):
        os.system("gnome-terminal -e 'bash -c \"cd "+self.currentDir+"; paraview; exec bash\"' --title=Paraview")

    def btn_sphere_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(3)

        # BOTTOM = {1440, 0, 0} | {90*16, 0, 0}
        # TOP = {4320, 0, 0} | {270*16, 0, 0}
        # FRONT = {0, 0, 0}
        # BACK = {0, 2880, 0} | {0, 180*16, 0}
        # SIDE1 = {0, 4320, 0} | {0, 270*16, 0}
        # SIDE2 = {0, 1440, 0} | {0, 90*16, 0}

    def btn_x_align_clicked(self):
        self.xSlider.setValue(0)
        self.ySlider.setValue(270*16)
        self.zSlider.setValue(0)

    def btn_x_align_neg_clicked(self):
        self.xSlider.setValue(0)
        self.ySlider.setValue(90*16)
        self.zSlider.setValue(0)

    def btn_y_align_clicked(self):
        self.xSlider.setValue(0)
        self.ySlider.setValue(0)
        self.zSlider.setValue(0)

    def btn_y_align_neg_clicked(self):
        self.xSlider.setValue(0)
        self.ySlider.setValue(180*16)
        self.zSlider.setValue(0)

    def btn_z_align_clicked(self):
        self.xSlider.setValue(270*16)
        self.ySlider.setValue(0)
        self.zSlider.setValue(0)

    def btn_z_align_neg_clicked(self):
        self.xSlider.setValue(90*16)
        self.ySlider.setValue(0)
        self.zSlider.setValue(0)

    def btn_zoom_in_clicked(self):
        self.glWidget.zoomin()

    def btn_zoom_out_clicked(self):
        self.glWidget.zoomout()

    def changecedlist(self):
        self.contactParams[3][self.combo_ced.currentIndex()] \
                          = self.line_ced.text()

    def changecorlist(self):
        self.contactParams[0][self.combo_cor.currentIndex()] \
                          = self.line_cor.text()

    def changekwearlist(self):
        self.contactParams[4][self.combo_kwear.currentIndex()] \
                          = self.line_kwear.text()

    def changeparticlelist(self):
        self.contactParams[1][self.combo_particlefriction.currentIndex()] \
            = self.line_particlefriction.text()

    def changerollinglist(self):
        self.contactParams[2][self.combo_rollingfriction.currentIndex()] \
            = self.line_rollingfriction.text()

    def chk_meshes_sv_clicked(self):
        self.stack_meshes_sv.setCurrentIndex(
                self.chk_meshes_sv.checkState()/2)
        if not self.loading:
            self.loading = True
            self.chk_meshes_sav.setCheckState(0)
            self.loading = False
            self.savemeshproperties()

    def chk_meshes_sav_clicked(self):
        self.stack_meshes_sav.setCurrentIndex(
                self.chk_meshes_sav.checkState()/2)
        if not self.loading:
            self.loading = True
            self.chk_meshes_sv.setCheckState(0)
            self.loading = False
            self.savemeshproperties()

    def chk_meshes_mm_clicked(self):
        self.stack_meshes_mm.setCurrentIndex(
                self.chk_meshes_mm.checkState()/2)
        self.savemeshproperties()

    def clearinsertionface(self):
        temp = self.insertionList[self.combo_insertionindex.currentIndex()+1][1]
        self.insertionList[self.combo_insertionindex.currentIndex()+1][1] = temp

    def  clearmeshproperties(self):
        self.loading = True
        self.stack_geometry_meshes.setCurrentIndex(0)
        self.chk_meshes_cm.setCheckState(2)
        self.chk_dumpmesh.setCheckState(2)
        self.chk_meshes_sv.setCheckState(0)
        self.spnbox_meshes_sv_x.setValue(0.00)
        self.spnbox_meshes_sv_y.setValue(0.00)
        self.spnbox_meshes_sv_z.setValue(0.00)
        self.chk_meshes_sav.setCheckState(0)
        self.spnbox_meshes_sav_x.setValue(0.00)
        self.spnbox_meshes_sav_y.setValue(0.00)
        self.spnbox_meshes_sav_z.setValue(0.00)
        self.spnbox_meshes_sav_a_x.setValue(0.00)
        self.spnbox_meshes_sav_a_y.setValue(0.00)
        self.spnbox_meshes_sav_a_z.setValue(0.00)
        self.spnbox_meshes_sav_omega.setValue(0.00)
        self.chk_meshes_mm.setCheckState(0)
        self.spnbox_meshes_starttime.setValue(0.00)
        self.combo_meshes_ct.setCurrentIndex(0)
        self.loading = False

    def createSlider(self):
        slider = QtGui.QSlider(QtCore.Qt.Vertical)

        slider.setRange(0, 360 * 16)
        slider.setSingleStep(16)
        slider.setPageStep(15 * 16)
        slider.setTickInterval(15 * 16)
        slider.setTickPosition(QtGui.QSlider.TicksRight)

        return slider

    def eventFilter(self, target, event):
        if event.type() == QtCore.QEvent.ContextMenu and target \
                     is self.tree_geometry.viewport():
            item = self.tree_geometry.itemAt(event.pos())
            if item is not None and type(item) is QtGui.QTreeWidgetItem \
                    and item.parent() is not None:
                menu = QtGui.QMenu()
                menu.addAction('Properties', lambda:
                               self.loadmeshproperties(item))
                menu.addSeparator()
                menu.addAction('Remove', lambda:
                               self.tree_remove(item))
                menu.exec_(event.globalPos())
            return True
        elif (event.type() == QtCore.QEvent.MouseButtonDblClick
              or event.type() == QtCore.QEvent.MouseButtonPress) \
                and target is self.tree_geometry.viewport():

            item = self.tree_geometry.itemAt(event.pos())
            if item is not None and type(item) is QtGui.QTreeWidgetItem \
                    and item.parent() is not None:
                self.tree_geometry.setCurrentItem(item)
                self.loadmeshproperties(item)
            else:
                self.tree_geometry.setCurrentItem(item)
                self.treegeometry()
        elif event.type() == QtCore.QEvent.Wheel \
                and str(target) == str(self.ogl):
            self.glWidget.zoomin() if event.delta() == 120 else self.glWidget.zoomout()
        return False

    def fileGen(self):
        f = open(self.currentDir+'script.py', 'w')
        f.write('# TUNRA BULK SOLIDS LIGGGHTS DEM Simulation File\n')
        f.write('# For technical support, please contact\n')
        f.write('# Wei Chen: W.Chen@newcastle.edu.au\n\n')
        f.write('#-------------------------------------------------------------------------------------------------\n')
        if self.radio_omp.isChecked():        
            f.write('variable\tNTHREADS equal '+str(self.num_threads.value())+'\t\t# OpenMP Threads\n')
            f.write('package\tomp ${NTHREADS} force/neigh thread-binding verbose\t# OpenMP Threads binding\n\n')
        f.write('# Variables - Declaration & Pass on to Simulations\n')
        f.write('variable\tpi\t\tequal\t\t3.141592654\t\t# PI\n')
        f.write('variable\ta\t\tequal\t\t1\t\t\t\t# Test number\n\n')
        f.write('# Variables - Timestep & Dumpstep\n')
        if self.chk_timestep.checkState() == 2 or not self.line_timestep.text().isEmpty():
            f.write('variable\tdt\t\t\tequal\t'+self.line_timestep.text()+
                    '\t\t\t\t# Time step\n')
        else:
            f.write('variable\tdt\t\t\tequal\t1e-4\t\t\t# Time step\n')
        f.write('variable\tfactor\t\tequal\t1/${dt}\t\t\t# Steps per second\n')
        if self.line_dumpstep.text().isEmpty():
            f.write('variable\tdumpstep\tequal\t0.05*${factor}\n\n')
        else:
            f.write('variable\tdumpstep\tequal\t'+self.line_dumpstep.text()+
                    '*${factor}\n\n')
        f.write('# Variables - Particle size distribution\n')

        for n in range(0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        f.write('variable\tdens')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('\t\t\tequal\t\t')
                        f.write(str(self.insertionList[n][0][x][y][z][2]))
                        f.write('\n')
            f.write('\n')

        for n in range(0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        f.write('variable\td')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('\t\t\tequal\t\t')
                        f.write(str(self.insertionList[n][0][x][y][z][3]))
                        f.write('\n')
            f.write('\n')
        for n in range(0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        f.write('variable\tr')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('\t\t\tequal\t\t${d')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('}/2000\n')
            f.write('\n')

        f.write('\n# Variable - particle size fractions\n')
        for n in range(0, len(self.insertionList)):
            largestVal = 0.0
            largestName = ''
            for x in range(0, len(self.insertionList[n][0])):
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        f.write('variable\tfrac')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('\t\t\tequal\t\t')
                        f.write(str(self.insertionList[n][0][x][y][z][1]))
                        if largestVal < self.insertionList[n][0][x][y][z][1] or \
                            largestName == '':
                            largestVal = self.insertionList[n][0][x][y][z][1]
                            largestName = self.insertionList[n][0][x][y][z][0]
                        f.write('\n')
            f.write('\n')
        f.write('\n# Define contact searching distance\n')
        f.write('variable\tcutoff\t\t\tequal\t\t${d'+
                largestName+'}/1000\n\n')

        f.write('# Variables - Particle and wall properties\n')
        corMtx = [[] for _ in range(0, self.totalTypes)]
        for n in range(0, self.totalTypes):
            for _ in range(0, self.totalTypes):
                corMtx[n].append(0)
        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                f.write('variable\tcor'+ str(x+1) + '_' + str(y+1) +
                        '\t\tequal\t\t'+str(self.contactParams[0][x+y])+'\n')
                corMtx[x][y] = 'cor' + str(x+1) + '_' + str(y+1)
        wffMtx = [[] for _ in range(0, self.totalTypes)]
        for n in range(0, self.totalTypes):
            for _ in range(0, self.totalTypes):
                wffMtx[n].append(0)
        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                if y == x:
                    f.write('variable\tff'+ str(x+1) + '_' + str(y+1) +
                            '\t\tequal\t\t'+str(self.contactParams[1][x+y])+'\n')
                    wffMtx[x][y] = 'ff' + str(x+1) + '_' + str(y+1)
                else:
                    f.write('variable\twf'+ str(x+1) + '_' + str(y+1) +
                            '\t\tequal\t\t'+str(self.contactParams[1][x+y])+'\n')
                    wffMtx[x][y] = 'wf' + str(x+1) + '_' + str(y+1)
        rfMtx = [[] for _ in range(0, self.totalTypes)]
        for n in range(0, self.totalTypes):
            for _ in range(0, self.totalTypes):
                rfMtx[n].append(0)
        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                f.write('variable\trf'+ str(x+1) + '_' + str(y+1) +
                        '\t\tequal\t\t'+str(self.contactParams[2][x+y])+'\n')
                rfMtx[x][y] = 'rf' + str(x+1) + '_' + str(y+1)
        edMtx = [[] for _ in range(0, self.totalTypes)]
        for n in range(0, self.totalTypes):
            for _ in range(0, self.totalTypes):
                edMtx[n].append(0)
        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                if y == x:
                    f.write('variable\tCED'+ str(x+1) + '_' + str(y+1) +
                            '\t\tequal\t\t'+str(self.contactParams[3][x+y])+'\n')
                    edMtx[x][y] = 'CED' + str(x+1) + '_' + str(y+1)
                else:
                    f.write('variable\tAED'+ str(x+1) + '_' + str(y+1) +
                            '\t\tequal\t\t'+str(self.contactParams[3][x+y])+'\n')
                    edMtx[x][y] = 'AED' + str(x+1) + '_' + str(y+1)

        f.write('# Variables - Mass flow rate\n')
        for n in range(0, len(self.insertionList)):
            f.write('variable\tm'+str(n+1)+'\t\tequal\t\t' +
                    str(self.insertionList[n][2][0])+
                    '\t\t\t# Total Mass to be inserted\n')
            f.write('variable\ttfill'+str(n+1)+'\tequal\t\t'+
                    str(self.insertionList[n][2][0]/
                    self.insertionList[n][2][1])
                    +'\t\t\t\t# Time for generating particles [s]\n')
            f.write('variable\tQ'+str(n+1)+'\t\tequal\t\t${m'+str(n+1)+'}/${tfill'+
                    str(n+1)+'}\t# Mass flow rate @ ~2000 t/h\n')

        f.write('\n')
        f.write('# Variables - Definition of times (points when simulation behaviour changes)\n')
        for n in range(0, len(self.insertionList)):
            f.write('variable\tt'+str(n+1)+'\t\tequal\t${tfill'+str(n+1)+'}\t\t\t\t# Time for inserting particles\n')
            f.write('variable\tsteps'+str(n+1)+'\tequal\t${t'+str(n+1)+'}*${factor}\t\t# Convert time to computational steps\n')
        addTempStr = ''
        for n in range(0, len(self.insertionList)):
            if n > 0:
                addTempStr += ' + ${t' + str(n+1) + '}'
            else:
                addTempStr += '${t' + str(n+1) + '}'
        f.write('variable\ttall\t\tequal\t'+(addTempStr if addTempStr != '' else '0')+'\n')
        if not self.line_totaltime.text().isEmpty():
            f.write('variable\tt'+str(len(self.insertionList)+1)+'\t\tequal\t'+self.line_totaltime.text()+'-${tall}'+'\n')
            f.write('variable\tsteps'+str(len(self.insertionList)+1)+'\tequal\t${t'+str(len(self.insertionList)+1)+'}*${factor}\n\n')

        f.write('######################################################################################################################\n\n')

        f.write('# Granular Model and Computational Setting\n')
        f.write('atom_style\t\tgranular'+('/omp' if self.radio_omp.isChecked() else '')+'\t\t# Granular style for LIGGGHTS\n\n')
        f.write('atom_modify\t\tmap array\t\t# The map keyword determines how atom ID lookup is done for molecular problems.\n')
        f.write('\t\t\t\t\t\t\t\t# When the array value is used, each processor stores a lookup table of length N,\n')
        f.write('\t\t\t\t\t\t\t\t# where N is the total # of atoms in the system. This is the fastest method,\n')
        f.write('\t\t\t\t\t\t\t\t# but a processor can run out of memory to store the table for large simulations.\n\n')

        f.write('boundary\t\t')
        if self.boundary_limit_x.currentIndex() == 0:
            f.write('f ')
        elif self.boundary_limit_x.currentIndex() == 1:
            f.write('m ')
        else:
            f.write('p ')
        if self.boundary_limit_y.currentIndex() == 0:
            f.write('f ')
        elif self.boundary_limit_y.currentIndex() == 1:
            f.write('m ')
        else:
            f.write('p ')
        if self.boundary_limit_z.currentIndex() == 0:
            f.write('f')
        elif self.boundary_limit_z.currentIndex() == 1:
            f.write('m')
        else:
            f.write('p')
        f.write('\t\t# Boundary definition in x y z (f=fixed bound., particles will be deleted,\n')
        f.write('\t\t\t\t\t\t\t# m = modified bound., boundaries will be extended,\n')
        f.write('\t\t\t\t\t\t\t# p = periodic bound.)\n\n')

        f.write('newton\t\t\toff\t\t\t\t\t# This command turns Newton\'s 3rd law on or off for pairwise interactions.\n\n')

        f.write('communicate\t\tsingle vel yes\t\t# This command sets the style of inter-processor communication\n')
        f.write('\t\t\t\t\t\t\t\t\t# that occurs each timestep as atom coordinates and other properties\n')
        f.write('\t\t\t\t\t\t\t\t\t# are exchanged between neighboring processors.\n\n')

        f.write('units\t\tsi\t\t# [s] [m] [kg] [N]\n\n')

        f.write('region\t\treg block ')
        f.write(str(self.boundary_min_x.value()) + ' ' +
                str(self.boundary_max_x.value()) + ' ' +
                str(self.boundary_min_y.value()) + ' ' +
                str(self.boundary_max_y.value()) + ' ' +
                str(self.boundary_min_z.value()) + ' ' +
                str(self.boundary_max_z.value()) + ' ')
        f.write('units box\t\t# Defines rectangular boundaries in x y z [m]\n\n')

        f.write('create_box\t\t'+str(self.totalTypes)+' reg\t\t# Number of atom (particle / wall) types\n')
        f.write('\t\t\t\t\t\t\t# type 1: inserted particles\n')
        f.write('\t\t\t\t\t\t\t# type 2: belts and walls\n\n')

        f.write('neighbor\t\t${cutoff} bin\t\t# Defines parameter for contact searching\n\n')

        f.write('neigh_modify\tdelay 0\t\t# Define the neighbor list building time\n\n')

        f.write('# Material properties required for new pair styles\n\n')

        f.write('fix\t\tm1 all property/global youngsModulus peratomtype')
        for n in range(0, len(self.gmt)):
            f.write(' ' + str(self.gmt[n][0]))
        f.write('\n\n')

        f.write('fix\t\tm2 all property/global poissonsRatio peratomtype')
        for n in range(0, len(self.gmt)):
            f.write(' ' + str(self.gmt[n][1]))
        f.write('\n\n')

        f.write('fix\t\tm3 all property/global coefficientRestitution peratomtypepair '+
                str(self.totalTypes) + ' ')

        for x in range(0, self.totalTypes):
            for y in range(0, self.totalTypes):
                if y >= x:
                    if edMtx[x][y] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(corMtx[x][y]) + '} ')
                else:
                    if edMtx[y][x] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(corMtx[y][x]) + '} ')
        f.write('\n\n')

        f.write('fix\t\tm4 all property/global coefficientFriction peratomtypepair ' +
                str(self.totalTypes) + ' ')

        for x in range(0, self.totalTypes):
            for y in range(0, self.totalTypes):
                if y >= x:
                    if edMtx[x][y] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(wffMtx[x][y]) + '} ')
                else:
                    if edMtx[y][x] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(wffMtx[y][x]) + '} ')
        f.write('\n\n')

        f.write('fix\t\tm5 all property/global coefficientRollingFriction peratomtypepair ' +
                str(self.totalTypes) + ' ')

        for x in range(0, self.totalTypes):
            for y in range(0, self.totalTypes):
                if y >= x:
                    if edMtx[x][y] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(rfMtx[x][y]) + '} ')
                else:
                    if edMtx[y][x] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(rfMtx[y][x]) + '} ')
        f.write('\n\n')

        f.write('fix\t\tm6 all property/global cohesionEnergyDensity peratomtypepair ' +
                str(self.totalTypes) + ' ')

        for x in range(0, self.totalTypes):
            for y in range(0, self.totalTypes):
                if y >= x:
                    if edMtx[x][y] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(edMtx[x][y]) + '} ')
                else:
                    if edMtx[y][x] == 0:
                        f.write('0 ')
                    else:
                        f.write('${' + str(edMtx[y][x]) + '} ')
        f.write('\n\n')

        f.write('fix\t\tm7 all property/global k_finnie peratomtypepair ')
        f.write(str(self.totalTypes) + ' ')
        for n in range(0, len(self.contactParams[4])):
            f.write(str(self.contactParams[4][n]) + ' ')
        f.write('# for wear analysis\n\n')

        f.write('# New pair style\n')

        f.write('pair_style gran'+('/omp' if self.radio_omp.isChecked() else '')+' model hertz tangential history')
        if self.cbox_ptcl_cohesionmodel.currentIndex() == 1:
            f.write(' cohesion sjkr')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 2:
            f.write(' cohesion sjkr2')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 3:
            f.write(' cohesion easo')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 4:
            f.write(' cohesion washino')
        if self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 1:
            f.write(' rolling_friction cdt')
        elif self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 2:
            f.write(' rolling_friction epsd')
        elif self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 3:
            f.write(' rolling_friction epsd2')
        f.write('\n\n')

        f.write('pair_coeff * *\n\n')

        f.write('timestep\t${dt}\n\n')

        f.write('fix\t\tgravi all gravity'+('/omp' if self.radio_omp.isChecked() else '')+' 9.81 vector ')
        if self.rad_gravity_x.isChecked():
            f.write('-1.0 0.0 0.0')
        elif self.rad_gravity_y.isChecked():
            f.write('0.0 -1.0 0.0')
        elif self.rad_gravity_z.isChecked():
            f.write('0.0 0.0 -1.0')
        f.write('\n\n')

        if self.radio_omp.isChecked():
            f.write('# Load Balancing Setting\n')
            f.write('partitioner_style\tzoltan OBJ_WEIGHT_DIM 1')

        for n in range(0, len(self.stlFilesLoaded)):
            f.write('fix\t\t' +
                    os.path.splitext(os.path.basename(self.stlFilesLoaded[n]))[0] +
                    ' all mesh/surface'+('/omp' if self.radio_omp.isChecked() and not self.meshProperties[n][14] else ''))
            if self.meshProperties[n][14]:
                f.write('/stress'+('/omp' if self.radio_omp.isChecked() else ''))
            f.write(' file ' +
                    self.stlFilesLoaded[n] +
                    ' type '+ str(self.meshProperties[n][1]+
                                  (1+self.spnbox_geometry_contacttypes_totalgranulartypes.value())) +
                    ' ')
            if self.meshProperties[n][3]:
                f.write('surface_vel ' +
                        str(self.meshProperties[n][4]) + ' ' +
                        str(self.meshProperties[n][5]) + ' ' +
                        str(self.meshProperties[n][6]) + ' ')
            elif self.meshProperties[n][7]:
                f.write('surface_ang_vel ' +
                        str(self.meshProperties[n][8]) + ' ' +
                        str(self.meshProperties[n][9]) + ' ' +
                        str(self.meshProperties[n][10]) + ' ')
            f.write('heal auto_remove_duplicates curvature 1e-8 ')
            if self.meshProperties[n][14]:
                f.write('wear finnie ')
            f.write('\n\n')

        f.write('fix\t\twall all wall/gran'+('/omp' if self.radio_omp.isChecked() else '')+' model hertz tangential history')
        if self.cbox_mesh_cohesionmodel.currentIndex() == 1:
            f.write(' cohesion sjkr')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 2:
            f.write(' cohesion sjkr2')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 3:
            f.write(' cohesion easo')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 4:
            f.write(' cohesion washino')
        if self.cbox_mesh_rollingfrictionmodel.currentIndex() == 1:
            f.write(' rolling_friction cdt')
        elif self.cbox_mesh_rollingfrictionmodel.currentIndex() == 2:
            f.write(' rolling_friction epsd')
        elif self.cbox_mesh_rollingfrictionmodel.currentIndex() == 3:
            f.write(' rolling_friction epsd2')

        f.write(' mesh n_meshes ' + str(self.objHolder.childCount()) + ' meshes')
        for items in self.stlFilesLoaded:
            f.write(' ' + os.path.splitext(os.path.basename(items))[0])
        f.write('\n\n')

        primef = open('resources/primes.txt', 'r')
        primes = [n for n in primef.read().split()]
        primef.close()

        f.write('# Particle distributions for insertion\n')
        for n in range(0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        f.write('fix\t\tpts')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write(' all particletemplate/sphere ' +
                                self.randomElement(primes)+' atom_type 1 ')
                        f.write('density constant ${dens')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('} radius constant ${r')
                        f.write(self.insertionList[n][0][x][y][z][0])
                        f.write('}\n')
            f.write('\n')
        for n in range (0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                numParticles = 0
                f.write('fix\t\tpdd'+str(n+1)+'_'+str(x+1))
                f.write(' all particledistribution/discrete ' +
                                self.randomElement(primes)+' ')
                strbuild = ''
                for y in range(0, len(self.insertionList[n][0][x])):
                    for z in range(0, len(self.insertionList[n][0][x][y])):
                        numParticles += 1
                        strbuild += ' pts' + self.insertionList[n][0][x][y][z][0]
                        strbuild += ' ${frac' + self.insertionList[n][0][x][y][z][0] + '}'
                    if y == len(self.insertionList[n][0][x])-1:
                        f.write(str(numParticles) + strbuild + '\n')
            f.write('\n')
        for n in range(0, len(self.insertionList)):
            f.write('fix\t\t'+os.path.splitext(os.path.basename(self.insertionList[n][1][1]))[0]+' all mesh/surface'+('/omp' if self.radio_omp.isChecked() else '')+' file '+self.insertionList[n][1][1]+' type '+
                    str(1+self.spnbox_geometry_contacttypes_totalgranulartypes.value())+
                    ' curvature 1e-6\n\n')
            f.write('fix\t\tins'+str(n+1)+' all insert/stream seed ' +
                                self.randomElement(primes)+' distributiontemplate pdd'+str(n+1)+'_1 &\n')
            f.write('\t\tmaxattempt 100 mass ${m'+str(n+1)+'} massrate ${Q'+str(n+1)+'} overlapcheck yes vel constant '+
                    str(self.insertionList[n][2][2])+' '+
                    str(self.insertionList[n][2][3])+' '+
                    str(self.insertionList[n][2][4])+' '+'&\n')
            f.write('\t\tinsertion_face '+os.path.splitext(os.path.basename(self.insertionList[n][1][1]))[0]+' extrude_length '+
                    str(self.insertionList[n][2][5])+'\n\n')

        f.write('fix\t\tintegr all nve/sphere'+('/omp' if self.radio_omp.isChecked() else '')+'\n\n')

        f.write('# Output settings, include total thermal energy\n')
        f.write('fix\t\t\t\tts all check/timestep/gran 1000 0.1 0.1\n')
        f.write('compute\t\t\trke all erotate/sphere\n')
        f.write('#computefix\t\tfc all pair/gran/local pos id force\n')
        f.write('thermo_style\tcustom step atoms ke c_rke f_ts[1] f_ts[2] vol\n')
        f.write('thermo\t\t\t1000\n')
        f.write('thermo_modify\tlost ignore norm no\n')

        f.write('shell rm '+ self.currentDir +'post\n')
        f.write('shell mkdir '+ self.currentDir +'post\n\n')
        stat_exists = False
        for i in self.meshProperties:
            if i[11] == 0:
                stat_exists = True
                f.write('dump\t\tdmpstl1 all mesh/stl 1 '+ self.currentDir +'post/static*.stl')
                for i in self.meshProperties:
                    if i[11] == 0:
                        f.write(' ' + os.path.splitext(i[0])[0])
                f.write('\n\n')
                break

        f.write('dump\t\tdmp_m all custom ${dumpstep} '+ self.currentDir +'post/dump_*.liggghts '+
                'id type '+
                ('x y z ' if self.chk_coordinates.checkState() == 2 else '') +
                ('ix iy iz ' if self.chk_inertia.checkState() == 2 else '') +
                ('vx vy vz ' if self.chk_velocity.checkState() == 2 else '') +
                ('fx fy fz ' if self.chk_force.checkState() == 2 else '') +
                ('omegax omegay omegaz ' if self.chk_angularvelocity.checkState() == 2 else '') +
                ('mass ' if self.chk_mass.checkState() == 2 else '') +
                ('radius' if self.chk_radius.checkState() == 2 else '') + '\n\n')

        for i in self.meshProperties:
            if i[14]:
                tempstr = os.path.splitext(i[0])[0]
                f.write('dump\t\tdumpstress_'+tempstr)
                f.write(' all mesh/gran/VTK ${dumpstep} '+ self.currentDir +'post/dump_')
                f.write(tempstr + '_*.vtk stress wear ')
                f.write(tempstr + '\n\n')

        for i in self.meshProperties:
            if i[11] == 2:
                f.write('dump\t\tdmpstl2 all mesh/stl ${dumpstep} '+ self.currentDir +'post/move*.stl')
                for i in self.meshProperties:
                    if i[11] == 2:
                        f.write(' ' + os.path.splitext(i[0])[0])
                f.write('\n\n')
                break

        f.write('run\t\t1\n\n')

        move_counter = 0
        for x in range(0, len(self.meshProperties)):
            for y in range(0, len(self.meshProperties[x][19])):
                move_counter += 1
                if self.mmList[x][y] == 0:
                    f.write('fix move'+str(move_counter)+' all move/mesh mesh ' +
                            os.path.splitext(self.meshProperties[x][0])[0] +
                            ' linear ' + str(self.meshProperties[x][19][y][0]) +
                                   ' ' + str(self.meshProperties[x][19][y][1]) +
                                   ' ' + str(self.meshProperties[x][19][y][2]) +
                                   '\n')
                elif self.mmList[x][y] == 1:
                    f.write('fix move'+str(move_counter)+' all move/mesh mesh ' +
                            os.path.splitext(self.meshProperties[x][0])[0] +
                     ' riggle origin ' + str(self.meshProperties[x][19][y][0]) +
                                   ' ' + str(self.meshProperties[x][19][y][1]) +
                                   ' ' + str(self.meshProperties[x][19][y][2]) +
                              ' axis ' + str(self.meshProperties[x][19][y][3]) +
                                   ' ' + str(self.meshProperties[x][19][y][4]) +
                                   ' ' + str(self.meshProperties[x][19][y][5]) +
                            ' period ' + str(self.meshProperties[x][19][y][6]) +
                         ' amplitude ' + str(self.meshProperties[x][19][y][7]) +
                                   '\n')
                elif self.mmList[x][y] == 2:
                    f.write('fix move'+str(move_counter)+' all move/mesh mesh ' +
                            os.path.splitext(self.meshProperties[x][0])[0] +
                     ' rotate origin ' + str(self.meshProperties[x][19][y][0]) +
                                   ' ' + str(self.meshProperties[x][19][y][1]) +
                                   ' ' + str(self.meshProperties[x][19][y][2]) +
                              ' axis ' + str(self.meshProperties[x][19][y][3]) +
                                   ' ' + str(self.meshProperties[x][19][y][4]) +
                                   ' ' + str(self.meshProperties[x][19][y][5]) +
                            ' period ' + str(self.meshProperties[x][19][y][6]) +
                                   '\n')
                else:
                    f.write('fix move'+str(move_counter)+' all move/mesh mesh ' +
                            os.path.splitext(self.meshProperties[x][0])[0] +
                  ' wiggle amplitude ' + str(self.meshProperties[x][19][y][0]) +
                                   ' ' + str(self.meshProperties[x][19][y][1]) +
                                   ' ' + str(self.meshProperties[x][19][y][2]) +
                            ' period ' + str(self.meshProperties[x][19][y][3]) +
                                   '\n')
            f.write('\n')

        if len(self.meshProperties[x][19]) > 0:
            f.write('run\t'+(str(self.meshProperties[x][12]/1e-4) if
                    self.line_timestep.text().isEmpty() else
                    str(self.meshProperties[x][12] /
                    float(self.line_timestep.text()))) + '\n\n')

        if stat_exists:
            f.write('undump\t\tdmpstl1\n\n')

        for n in range(0, len(self.insertionList)):
            f.write('run\t\t${steps'+str(n+1)+'}\n\n')

        for n in range(move_counter):
            f.write('unfix\tmove'+str(n+1)+'\n')
            if n+1==move_counter:
                f.write('\n')

        if not self.line_totaltime.text().isEmpty():
            f.write('run\t\t${steps'+str(len(self.insertionList)+1)+'}\n\n')
        
        f.write('write_restart	anyname.restart\n')

    def flip_mpi(self):
        if self.stack_mpi.currentIndex() == 1:
            self.stack_mpi.setCurrentIndex(0)
            self.stack_omp.setCurrentIndex(1)
        else:
            self.stack_mpi.setCurrentIndex(1)
            self.stack_omp.setCurrentIndex(0)

    def insertionmasssave(self):
        if not self.loading:
            self.insertionList[self.combo_insertionindex.currentIndex()][2] = [
                    self.spnbox_totalmass.value(),
                    self.spnbox_massrate.value(),
                    self.spnbox_insertion_mass_x.value(),
                    self.spnbox_insertion_mass_y.value(),
                    self.spnbox_insertion_mass_z.value(),
                    self.spnbox_insertion_extrude.value()]

    def listcedupdate(self):
        self.line_ced.setText(str(self.contactParams[3][
                self.combo_ced.currentIndex()]))

    def listcorupdate(self):
        self.line_cor.setText(str(self.contactParams[0][
                self.combo_cor.currentIndex()]))

    def listkwearupdate(self):
        self.line_kwear.setText(str(self.contactParams[4][
                self.combo_kwear.currentIndex()]))

    def listparticleupdate(self):
        self.line_particlefriction.setText(str(self.contactParams[1][
                self.combo_particlefriction.currentIndex()]))

    def listrollingupdate(self):
        self.line_rollingfriction.setText(str(self.contactParams[2][
                self.combo_rollingfriction.currentIndex()]))

    def list_mm_type_clicked(self, item):
        index = self.list_mm_type.indexFromItem(item).row()
        n = self.currentMeshType
        self.loading = True
        if self.mmList[n][index] == 0:
            self.stack_mm.setCurrentIndex(1)
            self.mm_velocity_x.setValue(self.meshProperties[n][19][index][0])
            self.mm_velocity_y.setValue(self.meshProperties[n][19][index][1])
            self.mm_velocity_z.setValue(self.meshProperties[n][19][index][2])
        elif self.mmList[n][index] == 1:
            self.stack_mm.setCurrentIndex(2)
            self.mm_riggle_origin_x.setValue(self.meshProperties[n][19][index][0])
            self.mm_riggle_origin_y.setValue(self.meshProperties[n][19][index][1])
            self.mm_riggle_origin_z.setValue(self.meshProperties[n][19][index][2])
            self.mm_riggle_axis_x.setValue(self.meshProperties[n][19][index][3])
            self.mm_riggle_axis_y.setValue(self.meshProperties[n][19][index][4])
            self.mm_riggle_axis_z.setValue(self.meshProperties[n][19][index][5])
            self.mm_riggle_period.setValue(self.meshProperties[n][19][index][6])
            self.mm_riggle_amplitude.setValue(self.meshProperties[n][19][index][7])
        elif self.mmList[n][index] == 2:
            self.stack_mm.setCurrentIndex(3)
            self.mm_rotate_origin_x.setValue(self.meshProperties[n][19][index][0])
            self.mm_rotate_origin_y.setValue(self.meshProperties[n][19][index][1])
            self.mm_rotate_origin_z.setValue(self.meshProperties[n][19][index][2])
            self.mm_rotate_axis_x.setValue(self.meshProperties[n][19][index][3])
            self.mm_rotate_axis_y.setValue(self.meshProperties[n][19][index][4])
            self.mm_rotate_axis_z.setValue(self.meshProperties[n][19][index][5])
            self.mm_rotate_period.setValue(self.meshProperties[n][19][index][6])
        else:
            self.stack_mm.setCurrentIndex(4)
            self.mm_amplitude_x.setValue(self.meshProperties[n][19][index][0])
            self.mm_amplitude_y.setValue(self.meshProperties[n][19][index][1])
            self.mm_amplitude_z.setValue(self.meshProperties[n][19][index][2])
            self.mm_wiggle_period.setValue(self.meshProperties[n][19][index][3])
        self.loading = False

    def clear_mm_type(self):
        self.loading = True

        self.mm_velocity_x.setValue(0.00)
        self.mm_velocity_y.setValue(0.00)
        self.mm_velocity_z.setValue(0.00)

        self.mm_riggle_origin_x.setValue(0.00)
        self.mm_riggle_origin_y.setValue(0.00)
        self.mm_riggle_origin_z.setValue(0.00)
        self.mm_riggle_axis_x.setValue(0.00)
        self.mm_riggle_axis_y.setValue(0.00)
        self.mm_riggle_axis_z.setValue(0.00)
        self.mm_riggle_period.setValue(0.00)
        self.mm_riggle_amplitude.setValue(0.00)

        self.mm_rotate_origin_x.setValue(0.00)
        self.mm_rotate_origin_y.setValue(0.00)
        self.mm_rotate_origin_z.setValue(0.00)
        self.mm_rotate_axis_x.setValue(0.00)
        self.mm_rotate_axis_y.setValue(0.00)
        self.mm_rotate_axis_z.setValue(0.00)
        self.mm_rotate_period.setValue(0.00)

        self.mm_amplitude_x.setValue(0.00)
        self.mm_amplitude_y.setValue(0.00)
        self.mm_amplitude_z.setValue(0.00)
        self.mm_wiggle_period.setValue(0.00)

        self.loading = False

    def loadInsertionSettings(self):
        if self.combo_insertionindex.currentIndex()+1 > len(self.insertionList):
            self.combo_insertionindex.setCurrentIndex(len(self.insertionList)-1)
            return -1
        elif self.combo_insertionindex.currentIndex()+1 < 1 and \
                len(self.insertionList) > 0:
            self.combo_insertionindex.setCurrentIndex(0)
            return -1
        if len(self.insertionList) > 0:
            currSettings = self.insertionList[self.combo_insertionindex.currentIndex()]
            if len(currSettings[0]) > 0:
                self.spnbox_psd.setValue(0)
                self.spnbox_psd.setValue(1)  # Will call valueChanged
            else:
                self.spnbox_psd.setValue(0)
            self.loading = True
            if currSettings[1][0] == 0:
                if currSettings[1][1] is not None:
                    self.lbl_loaded_insertion.setText(
                            basename(currSettings[1][1]))
                else:
                    self.lbl_loaded_insertion.setText('...')
            self.spnbox_totalmass.setValue(
                    currSettings[2][0])
            self.spnbox_massrate.setValue(
                    currSettings[2][1])
            self.spnbox_insertion_mass_x.setValue(
                    currSettings[2][2])
            self.spnbox_insertion_mass_y.setValue(
                    currSettings[2][3])
            self.spnbox_insertion_mass_z.setValue(
                    currSettings[2][4])
            self.spnbox_insertion_extrude.setValue(
                    currSettings[2][5])
            self.loading = False

    def loadMaterialData(self):
        self.loading = True
        self.line_youngsmodulus.setText(str(self.gmt[
                self.combo_conty.currentIndex()][0]))
        self.spnbox_poissonsratio.setValue(self.gmt[
                self.combo_conty.currentIndex()][1])
        self.loading = False

    def loadmeshproperties(self, item):
        global mesh_ref
        self.stack_geometry_meshes.setCurrentIndex(1)
        for index in self.origPath:
            if index[1] == item.text(0):
                self.fileName = index[0]
                break
        for n in range(0, len(mesh_ref)):
            if mesh_ref[n][0] == self.fileName:
                mesh_ref[n][2] = [1.00, .98, .80, 1.0]
            else:
                mesh_ref[n][2] = [.4, .4, .4, 0]
        self.glWidget.initializeGL()
        self.glWidget.updateGL()
        self.glWidget.paintGL()
        self.loading = True
        for i in self.meshProperties:
            if i[0] == item.text(0):
                self.currentMeshType = self.meshProperties.index(i)
                self.combo_meshes_ct.setCurrentIndex(i[1])
                self.chk_meshes_cm.setCheckState(
                        2 if i[2] else 0)
                self.chk_meshes_sv.setCheckState(
                        2 if i[3] else 0)
                self.spnbox_meshes_sv_x.setValue(i[4])
                self.spnbox_meshes_sv_y.setValue(i[5])
                self.spnbox_meshes_sv_z.setValue(i[6])
                self.chk_meshes_sav.setCheckState(
                        2 if i[7] else 0)
                self.spnbox_meshes_sav_x.setValue(i[8])
                self.spnbox_meshes_sav_y.setValue(i[9])
                self.spnbox_meshes_sav_z.setValue(i[10])
                self.chk_meshes_mm.setCheckState(
                        2 if i[11] else 0)
                self.spnbox_meshes_starttime.setValue(i[12])
                self.chk_dumpmesh.setCheckState(
                        2 if i[13] else 0)
                self.chk_meshes_sw.setCheckState(
                        2 if i[14] else 0)
                self.spnbox_meshes_sav_a_x.setValue(i[15])
                self.spnbox_meshes_sav_a_y.setValue(i[16])
                self.spnbox_meshes_sav_a_z.setValue(i[17])
                self.spnbox_meshes_sav_omega.setValue(i[18])
                self.list_mm_type.clear()
                for x in range(0, len(self.mmList[self.currentMeshType])):
                    if self.mmList[self.currentMeshType][x] == 0:
                        self.list_mm_type.addItem('Item_'+str(x+1)+'_Linear')
                    elif self.mmList[self.currentMeshType][x] == 1:
                        self.list_mm_type.addItem('Item_'+str(x+1)+'_Riggle')
                    elif self.mmList[self.currentMeshType][x] == 2:
                        self.list_mm_type.addItem('Item_'+str(x+1)+'_Rotate')
                    else:
                        self.list_mm_type.addItem('Item_'+str(x+1)+'_Wiggle')
                
                if len(self.mmList[self.currentMeshType]) > 0:
                    self.stack_mm.setCurrentIndex(self.mmList[self.currentMeshType][0]+1)
                    if self.mmList[self.currentMeshType][0] == 0:
                        self.mm_velocity_x.setValue(i[19][0][0])
                        self.mm_velocity_y.setValue(i[19][0][1])
                        self.mm_velocity_z.setValue(i[19][0][2])
                    elif self.mmList[self.currentMeshType][0] == 1:
                        self.mm_riggle_origin_x.setValue(i[19][0][0])
                        self.mm_riggle_origin_y.setValue(i[19][0][1])
                        self.mm_riggle_origin_z.setValue(i[19][0][2])
                        self.mm_riggle_axis_x.setValue(i[19][0][3])
                        self.mm_riggle_axis_y.setValue(i[19][0][4])
                        self.mm_riggle_axis_z.setValue(i[19][0][5])
                        self.mm_riggle_period.setValue(i[19][0][6])
                        self.mm_riggle_amplitude.setValue(i[19][0][7])
                    elif self.mmList[self.currentMeshType][0] == 2:
                        self.mm_rotate_origin_x.setValue(i[19][0][0])
                        self.mm_rotate_origin_y.setValue(i[19][0][1])
                        self.mm_rotate_origin_z.setValue(i[19][0][2])
                        self.mm_rotate_axis_x.setValue(i[19][0][3])
                        self.mm_rotate_axis_y.setValue(i[19][0][4])
                        self.mm_rotate_axis_z.setValue(i[19][0][5])
                        self.mm_rotate_period.setValue(i[19][0][6])
                    else:
                        self.mm_amplitude_x.setValue(i[19][0][0])
                        self.mm_amplitude_y.setValue(i[19][0][1])
                        self.mm_amplitude_z.setValue(i[19][0][2])
                        self.mm_wiggle_period.setValue(i[19][0][3])
                else:
                    self.stack_mm.setCurrentIndex(0)
                self.loading = False
                break

    def materialdataini(self):
        self.combo_particlelist.clear()
        curVal = self.combo_conty.currentIndex()
        if len(self.gmt) > 0:
            self.line_youngsmodulus.setText(str(self.gmt[curVal][0]))
            self.spnbox_poissonsratio.setValue(self.gmt[curVal][1])

    def openFile(self):
        inFile = QtGui.QFileDialog.getOpenFileName(self,
                                                   'Single File',
                                                   (self.currentDir if self.currentDir != None else '.'),
                                                   'GUI File (*.mlx)')
        inFile = str(inFile)
        if os.path.exists(inFile):
            self.new_button_clicked(True)
            self.currentFile = inFile
            self.currentDir = os.path.dirname(inFile) + "/"
            storage = pickle.load(open(inFile, 'rb'))
            self.spnbox_geometry_contacttypes_totalgranulartypes.setValue(storage[0])
            self.spnbox_geometry_contacttypes_totalmeshtypes.setValue(storage[1])
            self.origPath = storage[2]
            self.openstl(sig_catch=None, fileName=[item[0] for item in self.origPath], isNew=True)
            self.stlFilesLoaded = storage[3]
            self.meshProperties = storage[4]
            self.mmList = storage[5]
            self.boundary_min_x.setValue(storage[6][0])
            self.boundary_min_y.setValue(storage[6][1])
            self.boundary_min_z.setValue(storage[6][2])
            self.boundary_max_x.setValue(storage[6][3])
            self.boundary_max_y.setValue(storage[6][4])
            self.boundary_max_z.setValue(storage[6][5])
            self.boundary_limit_x.setCurrentIndex(storage[6][6])
            self.boundary_limit_y.setCurrentIndex(storage[6][7])
            self.boundary_limit_z.setCurrentIndex(storage[6][8])
            self.cbox_ptcl_atomstyle.setCurrentIndex(storage[7][0])
            self.cbox_ptcl_pairstyle.setCurrentIndex(storage[7][1])
            self.cbox_ptcl_rollingfrictionmodel.setCurrentIndex(storage[7][2])
            self.cbox_ptcl_cohesionmodel.setCurrentIndex(storage[7][3])
            self.cbox_mesh_atomstyle.setCurrentIndex(storage[7][4])
            self.cbox_mesh_pairstyle.setCurrentIndex(storage[7][5])
            self.cbox_mesh_rollingfrictionmodel.setCurrentIndex(storage[7][6])
            self.cbox_mesh_cohesionmodel.setCurrentIndex(storage[7][7])
            self.cbox_mesh_wearmodel.setCurrentIndex(storage[7][8])
            self.chk_gravityactive.setChecked(storage[7][9])
            self.rad_gravity_x.setChecked(storage[7][10][0])
            self.rad_gravity_y.setChecked(storage[7][10][1])
            self.rad_gravity_z.setChecked(storage[7][10][2])
            self.contactParams = storage[8]
            self.insertionList = storage[9][0]
            self.combo_insertionindex.clear()
            for i in range(storage[9][1]):
                self.combo_insertionindex.addItem(str(i+1))
            self.combo_insertionindex.setCurrentIndex(storage[9][2])
            if len(self.insertionList) > 0:
                self.stack_insertionsettings.setCurrentIndex(1)
                self.combo_insertionindex.setCurrentIndex(0)
            else:
                self.combo_insertionindex.setCurrentIndex(0)
                self.stack_insertionsettings.setCurrentIndex(0)
            self.chk_coordinates.setChecked(storage[10][0])
            self.chk_velocity.setChecked(storage[10][1])
            self.chk_force.setChecked(storage[10][2])
            self.chk_angularvelocity.setChecked(storage[10][3])
            self.chk_inertia.setChecked(storage[10][4])
            self.chk_mass.setChecked(storage[10][5])
            self.chk_radius.setChecked(storage[10][6])
            self.line_totaltime.setText(storage[11][0])
            self.line_timestep.setText(storage[11][1])
            self.line_dumpstep.setText(storage[11][2])
            self.chk_timestep.setChecked(storage[11][3])
            self.combo_writeformat.setCurrentIndex(storage[11][4])
            self.num_proc.setValue(storage[12][0])
            self.num_cpu.setValue(storage[12][1])
            self.num_threads.setValue(storage[12][2])
            self.gmt = storage[13]
            self.combo_conty.setCurrentIndex(storage[14])
            if storage[15]:
                if not self.radio_mpi.isChecked():
                    self.radio_mpi.setChecked(True)
            
            self.listcedupdate()
            self.listcorupdate()
            self.listkwearupdate()
            self.listparticleupdate()
            self.listrollingupdate()
            self.loadMaterialData()

    def new_button_clicked(self, fromOpen=False):
        confirmation = None
        confirmation_new = None
        if not fromOpen:
            if self.currentDir != None and self.currentFile != None:
                confirmation = QtGui.QMessageBox.question(None, "New Project",
                                "Are you sure you want to start a new project? "
                                "Any unsaved changes will be lost.",
                                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if (self.currentDir == None or self.currentFile == None) or \
                                     (confirmation == QtGui.QMessageBox.Yes):
                result = self.saveas(False)
                if result != 0:
                    confirmation_new = QtGui.QMessageBox.Yes
                else:
                    confirmation_new = QtGui.QMessageBox.No
        #print confirmation == QtGui.QMessageBox.Yes
        if fromOpen or confirmation == QtGui.QMessageBox.Yes or confirmation_new == QtGui.QMessageBox.Yes:
            if not confirmation_new == QtGui.QMessageBox.Yes:
                self.currentFile = None
            self.spnbox_geometry_contacttypes_totalgranulartypes.setValue(1)
            self.spnbox_geometry_contacttypes_totalmeshtypes.setValue(1)
            self.loading = True
            temp_cf = self.currentFile
            temp_cd = self.currentDir
            self.ini_vars()
            self.currentFile = temp_cf
            self.currentDir = temp_cd
            while self.objHolder.childCount() > 0:
                self.objHolder.removeChild(self.objHolder.child(0))
            self.stack_geometry_meshes.setCurrentIndex(0)
            self.loading = False
            self.glWidget.initializeGL()
            self.glWidget.updateGL()
            self.glWidget.paintGL()
            self.autofit()
            self.cbox_ptcl_atomstyle.setCurrentIndex(0)
            self.cbox_mesh_atomstyle.setCurrentIndex(0)
            self.cbox_ptcl_pairstyle.setCurrentIndex(0)
            self.cbox_mesh_pairstyle.setCurrentIndex(0)
            self.cbox_ptcl_rollingfrictionmodel.setCurrentIndex(0)
            self.cbox_mesh_rollingfrictionmodel.setCurrentIndex(0)
            self.cbox_ptcl_cohesionmodel.setCurrentIndex(0)
            self.cbox_mesh_cohesionmodel.setCurrentIndex(0)
            self.cbox_mesh_wearmodel.setCurrentIndex(0)
            self.rad_gravity_x.setChecked(True)
            self.chk_coordinates.setCheckState(0)
            self.chk_force.setCheckState(0)
            self.chk_angularvelocity.setCheckState(0)
            self.chk_inertia.setCheckState(0)
            self.chk_mass.setCheckState(0)
            self.chk_velocity.setCheckState(0)
            self.line_totaltime.setText('')
            self.line_timestep.setText('')
            self.chk_timestep.setCheckState(0)
            self.line_dumpstep.setText('')
            self.num_proc.setValue(1)
            self.combo_insertionindex.clear()
            self.stack_geometry.setCurrentIndex(0)
            self.testPage.setCurrentIndex(0)
            self.testPage.setEnabled(True)
            self.stack_geometry.setEnabled(True)
            self.pushButton_Save.setEnabled(True)
            self.btn_saveas.setEnabled(True)
            self.btn_terminal.setEnabled(True)
            self.pushButton_Browse.setEnabled(True)
            self.pushButton_Support.setEnabled(True)
            self.btn_x_align.setEnabled(True)
            self.btn_y_align.setEnabled(True)
            self.btn_z_align.setEnabled(True)
            self.btn_x_align_neg.setEnabled(True)
            self.btn_y_align_neg.setEnabled(True)
            self.btn_z_align_neg.setEnabled(True)
            self.btn_zoom_in.setEnabled(True)
            self.btn_zoom_out.setEnabled(True)
            
        else:
            return 0

    def openMenu(position):
        menu = QMenu()
        quitAction = menu.addAction('Quit')
        action = menu.exec_(tableWidget.mapToGlobal(position))
        if action == quitAction:
            exit()

    def openstl(self, sig_catch=None, fileName=None, isNew=True):
        global mesh_ref
        if fileName is None:
            self.fileName = QtGui.QFileDialog.getOpenFileNames(self,
                                                              'Multiple File',
                                                              (self.currentDir if self.currentDir != None else '.'),
                                                              'STL Files (*.stl)')
            self.fileName = [str(item) for item in self.fileName]
        else:
            self.fileName = fileName
        if isNew:
            for f in self.fileName:
                if f not in self.stlFilesLoaded and \
                        os.path.exists(f):
                    #Load model into opengl viewer
                    self.origPath.append([f, basename(f)])
                    tempVar = load_mesh(f)
                    for n in range(0, len(mesh_ref)):
                        mesh_ref[n][2] = [.4, .4, .4, 0]
                    mesh_ref.append([f, tempVar, [1., .98, .80, 1.0]])
                    self.glWidget.initializeGL()
                    self.glWidget.updateGL()
                    self.glWidget.paintGL()
                    #Create tree element
                    tempChild = QtGui.QTreeWidgetItem(self.objHolder)
                    tempChild.setText(0, QtCore.QString(basename(f)))
                    #Store name to prevent duplicates
                    self.stlFilesLoaded.append(f)
                    #Expand the parent in the tree
                    self.objHolder.setExpanded(True)
                    #Sort the children
                    self.objHolder.sortChildren(0, 0)  # (0, 0) = ASC, (0, 1) = DESC
                    #Make a new list for storing mesh data
                    self.meshProperties.append([basename(f), 0, False,
                                                False, 0.00, 0.00, 0.00,
                                                False, 0.00, 0.00, 0.00,
                                                False, 0.00, False, False,
                                                0.00, 0.00, 0.00, 0.00, []])
                    self.mmList.append([])
                    self.currentMeshType = len(self.meshProperties)-1
                    self.stack_geometry_meshes.setCurrentIndex(1)
                    self.loadmeshproperties(tempChild)
        else:
            for f in self.fileName:
                if f not in self.stlFilesLoaded and \
                        os.path.exists(f):
                    tempVar = load_mesh(f)
                    for n in range(0, len(mesh_ref)):
                        mesh_ref[n][2] = [.4, .4, .4, 0]
                    mesh_ref.append([f, tempVar, [1., .98, .80, 1.0]])
                    self.glWidget.initializeGL()
                    self.glWidget.updateGL()
                    self.glWidget.paintGL()
                    tempChild = QtGui.QTreeWidgetItem(self.objHolder)
                    tempChild.setText(0, QtCore.QString(basename(f)))
                    self.objHolder.setExpanded(True)
                    self.objHolder.sortChildren(0, 0)
                    self.currentMeshType = len(self.meshProperties)-1
                    self.loadmeshproperties(tempChild)
        
        

    def popupAbout(self):
        self.pua = MyPopupAbout(self)
        self.pua.show()

    def popupSupport(self):
        self.pus = MyPopupSupport(self)
        self.pus.show()

    def randomElement(self, listIn):
        rand = listIn[int(len(listIn)*random.random())]
        listIn.remove(rand)
        return rand

    def relDirSolver(self, dirList):
        relDir = []
        cwd = os.path.split(os.getcwd())[1]
        for paths in dirList:
            prev = []
            split = os.path.split(paths)
            dir = split[0]
            searcher = split[1]
            while searcher != cwd:
                prev.append(searcher)
                split = os.path.split(dir)
                dir = split[0]
                searcher = split[1]
            prev.reverse()
            strbuild = ''
            for n in range(0, len(prev)):
                if(n == len(prev)-1):
                    strbuild += prev[n]
                else:
                    strbuild += prev[n] + '/'
            relDir.append(strbuild)
        return relDir

    def renewparticlenames(self):
        for n in range(0, len(self.insertionList)):
            for x in range(0, len(self.insertionList[n][0])):
                    for y in range(0, len(self.insertionList[n][0][x])):
                        for z in range(0, len(self.insertionList[n][0][x][y])):
                            self.insertionList[n][0][x][y][z][0] = \
                                    str(n+1)+'_'+str(x+1)+ \
                                    '_p'+str(y+1)+'_'+str(z+1)
        self.updateparticlelist()

    def resetmassproperties(self):
        self.loading = True
        self.spnbox_totalmass.setValue(0.00)
        self.spnbox_massrate.setValue(0.00)
        self.spnbox_insertion_mass_x.setValue(0.00)
        self.spnbox_insertion_mass_y.setValue(0.00)
        self.spnbox_insertion_mass_z.setValue(0.00)
        self.spnbox_insertion_extrude.setValue(0.00)
        self.loading = False

    def run_prog_clicked(self):
        cmmmd = 'mpirun -np ' + str(self.num_proc.value()) + \
                        ' LIGGGHTS <' + self.currentDir + 'script.py'

        os.system("gnome-terminal -e 'bash -c \" "+cmmmd+"; exec bash\"' --title=Simulation")

    def save(self, outFile=None):
        if self.currentFile is None:
            self.saveas(True)
        if os.path.exists(self.currentFile) or self.currentFile is not None:
            storage = []
            storage.append(int(self.spnbox_geometry_contacttypes_totalgranulartypes.value()))
            storage.append(int(self.spnbox_geometry_contacttypes_totalmeshtypes.value()))
            storage.append(self.origPath)
            storage.append(self.stlFilesLoaded)
            storage.append(self.meshProperties)
            storage.append(self.mmList)
            storage.append([float(self.boundary_min_x.value()),
                            float(self.boundary_min_y.value()),
                            float(self.boundary_min_z.value()),
                            float(self.boundary_max_x.value()),
                            float(self.boundary_max_y.value()),
                            float(self.boundary_max_z.value()),
                            int(self.boundary_limit_x.currentIndex()),
                            int(self.boundary_limit_y.currentIndex()),
                            int(self.boundary_limit_z.currentIndex())])
            storage.append([self.cbox_ptcl_atomstyle.currentIndex(),
                            self.cbox_ptcl_pairstyle.currentIndex(),
                            self.cbox_ptcl_rollingfrictionmodel.currentIndex(),
                            self.cbox_ptcl_cohesionmodel.currentIndex(),
                            self.cbox_mesh_atomstyle.currentIndex(),
                            self.cbox_mesh_pairstyle.currentIndex(),
                            self.cbox_mesh_rollingfrictionmodel.currentIndex(),
                            self.cbox_mesh_cohesionmodel.currentIndex(),
                            self.cbox_mesh_wearmodel.currentIndex(),
                            self.chk_gravityactive.checkState(),
                            (self.rad_gravity_x.isChecked(),
                             self.rad_gravity_y.isChecked(),
                             self.rad_gravity_z.isChecked(),)])
            storage.append(self.contactParams)
            storage.append([self.insertionList, len(self.insertionList), self.combo_insertionindex.currentIndex()])
            storage.append((self.chk_coordinates.isChecked(),
                            self.chk_velocity.isChecked(),
                            self.chk_force.isChecked(),
                            self.chk_angularvelocity.isChecked(),
                            self.chk_inertia.isChecked(),
                            self.chk_mass.isChecked(),
                            self.chk_radius.isChecked()))
            storage.append((str(self.line_totaltime.text()),
                           str(self.line_timestep.text()),
                           str(self.line_dumpstep.text()),
                           self.chk_timestep.isChecked(),
                           self.combo_writeformat.currentIndex()))
            storage.append((int(self.num_proc.value()),
                            int(self.num_cpu.value()),
                            int(self.num_threads.value())))
            storage.append(self.gmt)
            storage.append(self.combo_conty.currentIndex())
            storage.append(self.radio_mpi.isChecked())
            
            outFile = open(self.currentFile, 'wb')
            pickle.dump(storage, outFile)

    def saveas(self, fromSave=False):
        outFile = QtGui.QFileDialog.getSaveFileName(self, 'Save As', (self.currentDir if self.currentDir != None else '.'), 'GUI File (*.mlx)')
        outFile = str(outFile)
        #print (outFile, self.currentFile)
        if outFile != '':
            self.currentFile = outFile
            #print self.currentFile
            self.currentDir = os.path.dirname(outFile) + "/"
            if not fromSave:
                self.save(outFile)
        else:
            return 0
#        print 'saveas'

    def saveMaterialData(self):
        if not self.loading:
            curval = self.gmt[self.combo_conty.currentIndex()]
            curval[0] = self.line_youngsmodulus.text()
            curval[1] = self.spnbox_poissonsratio.value()

    def savemeshproperties(self):
        if not self.loading:
            n = self.currentMeshType
            self.meshProperties[n][1] = self.combo_meshes_ct.currentIndex()
            self.meshProperties[n][2] = True if self.chk_meshes_cm.checkState() == 2 \
                               else False
            self.meshProperties[n][3] = True if self.chk_meshes_sv.checkState() == 2 \
                               else False
            self.meshProperties[n][4] = self.spnbox_meshes_sv_x.value()
            self.meshProperties[n][5] = self.spnbox_meshes_sv_y.value()
            self.meshProperties[n][6] = self.spnbox_meshes_sv_z.value()
            self.meshProperties[n][7] = True if self.chk_meshes_sav.checkState() == \
                2 else False
            self.meshProperties[n][8] = self.spnbox_meshes_sav_x.value()
            self.meshProperties[n][9] = self.spnbox_meshes_sav_y.value()
            self.meshProperties[n][10] = self.spnbox_meshes_sav_z.value()
            self.meshProperties[n][11] = True if self.chk_meshes_mm.checkState() == \
                2 else False
            self.meshProperties[n][12] = self.spnbox_meshes_starttime.value()
            self.meshProperties[n][13] = True if self.chk_dumpmesh.checkState() == \
                2 else False
            self.meshProperties[n][14] = True if self.chk_meshes_sw.checkState() == \
                2 else False
            self.meshProperties[n][15] = self.spnbox_meshes_sav_a_x.value()
            self.meshProperties[n][16] = self.spnbox_meshes_sav_a_y.value()
            self.meshProperties[n][17] = self.spnbox_meshes_sav_a_z.value()
            self.meshProperties[n][18] = self.spnbox_meshes_sav_omega.value()

            if len(self.meshProperties[n][19]) > 0:
                if self.stack_mm.currentIndex() == 1:
                    # Save for linear
                    self.meshProperties[n][19][self.list_mm_type.indexFromItem(
                            self.list_mm_type.currentItem()).row()] = \
                        (self.mm_velocity_x.value(),
                         self.mm_velocity_y.value(),
                         self.mm_velocity_z.value())
                elif self.stack_mm.currentIndex() == 2:
                    # Save for riggle
                    self.meshProperties[n][19][self.list_mm_type.indexFromItem(
                            self.list_mm_type.currentItem()).row()] = \
                        (self.mm_riggle_origin_x.value(),
                         self.mm_riggle_origin_y.value(),
                         self.mm_riggle_origin_z.value(),
                         self.mm_riggle_axis_x.value(),
                         self.mm_riggle_axis_y.value(),
                         self.mm_riggle_axis_z.value(),
                         self.mm_riggle_period.value(),
                         self.mm_riggle_amplitude.value())
                elif self.stack_mm.currentIndex() == 3:
                    # Save for rotate
                    self.meshProperties[n][19][self.list_mm_type.indexFromItem(
                            self.list_mm_type.currentItem()).row()] = \
                        (self.mm_rotate_origin_x.value(),
                         self.mm_rotate_origin_y.value(),
                         self.mm_rotate_origin_z.value(),
                         self.mm_rotate_axis_x.value(),
                         self.mm_rotate_axis_y.value(),
                         self.mm_rotate_axis_z.value(),
                         self.mm_rotate_period.value())
                else:
                    # Save for wiggle
                    self.meshProperties[n][19][self.list_mm_type.indexFromItem(
                            self.list_mm_type.currentItem()).row()] = \
                        (self.mm_amplitude_x.value(),
                         self.mm_amplitude_y.value(),
                         self.mm_amplitude_z.value(),
                         self.mm_wiggle_period.value())

    def savePSD(self):
        if self.spnbox_psd.value() is not 0 and self.loading is not True:
            self.insertionList[self.combo_insertionindex.currentIndex()][0][
                    self.spnbox_psd.value()-1][
                            self.spnbox_granulartypeindex.value()-1][
                            self.combo_particlelist.currentIndex()] = \
                                [str(self.combo_particlelist.currentText()),
                                    self.spnbox_insertion_fraction.value(),
                                    self.spnbox_density.value(),
                                    self.spnbox_diameter.value()]
            adding = 0
            for n in range(0, len(self.insertionList[self.combo_insertionindex.currentIndex()
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1])):
                adding += self.insertionList[self.combo_insertionindex.currentIndex()
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1][n][1]
            self.lbl_PSDFractionTotal.setText(str(adding))

    def terminal(self):
        os.system("gnome-terminal -e 'bash -c \" cd "+self.currentDir+"; exec bash\"' --title='Current Project Terminal'")

    def tree_remove(self, item):
        global mesh_ref
        for f in self.stlFilesLoaded:
            if basename(f) == item.text(0):
                for i in self.meshProperties:
                    if i[0] == item.text(0):
                        if self.meshProperties[
                                self.meshProperties.index(i)][0] == i[0]:
                            self.clearmeshproperties()
                        del self.meshProperties[
                                self.meshProperties.index(i)]
                        for n in mesh_ref:
                            if i[0] == os.path.basename(n[0]):
                                del mesh_ref[mesh_ref.index(n)]
                                break
                self.stlFilesLoaded.remove(f)
                for i in self.origPath:
                    if i[1] == item.text(0):
                        del self.origPath[
                                self.origPath.index(i)]
                break
        self.glWidget.initializeGL()
        self.glWidget.updateGL()
        self.glWidget.paintGL()
        item.parent().removeChild(item)

    def treecasesetup(self):
        self.stack_casesetup.setCurrentIndex(self.tree_casesetup.indexFromItem(
                self.tree_casesetup.currentItem()).row())

    def treegeometry(self):
        if self.tree_geometry.currentItem() is not None and \
                    self.tree_geometry.currentItem().parent() is None:
            self.stack_geometry.setCurrentIndex(
                    self.tree_geometry.indexFromItem(
                            self.tree_geometry.currentItem()).row())
        elif self.tree_geometry.currentItem() is not None:
            (self.stack_geometry.setCurrentIndex(
                     self.tree_geometry.indexFromItem(
                             self.tree_geometry.currentItem().parent()).row()))

    def updateparticlelist(self):
        if not self.loading:
            self.loading = True
            if self.spnbox_granulartypeindex.value() == 0:
                self.spnbox_granulartypeindex.setValue(1)
            elif self.spnbox_granulartypeindex.value() > \
                    self.spnbox_geometry_contacttypes_totalgranulartypes.value():
                self.spnbox_granulartypeindex.setValue(
                    self.spnbox_geometry_contacttypes_totalgranulartypes.value())
            self.combo_particlelist.clear()
            for n in range(0, len(
                    self.insertionList[self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1])):
                self.combo_particlelist.addItem(
                        self.insertionList[
                                self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            n][0])
            adding = 0
            for n in range(0, len(self.insertionList[self.combo_insertionindex.currentIndex()
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1])):
                adding += self.insertionList[self.combo_insertionindex.currentIndex()
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1][n][1]
            self.lbl_PSDFractionTotal.setText(str(adding))
            self.loading = False
            self.updateparticletype()

    def updateparticletype(self):
        if not self.loading and len(self.insertionList) > 0:
            self.loading = True
            self.spnbox_insertion_fraction.setValue(
                    self.insertionList[
                                self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][1])
            self.spnbox_density.setValue(
                    self.insertionList[
                                self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][2])
            self.spnbox_diameter.setValue(
                    self.insertionList[
                                self.combo_insertionindex.currentIndex()][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][3])
            self.loading = False

    def updateparticletypelist(self):
        if not self.loading:
            self.loading = True
            if self.spnbox_psd.value() > len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][0]):
                self.spnbox_psd.setValue(len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][0]))
            if self.spnbox_psd.value() == 0 and len(self.insertionList[
                    self.combo_insertionindex.currentIndex()][0]) > 0:
                    self.spnbox_psd.setValue(1)
            if self.spnbox_granulartypeindex.value() == 0:
                self.spnbox_granulartypeindex.setValue(1)

            self.loading = False
            self.updateparticlelist()

class GLWidget(QtOpenGL.QGLWidget):
    xRotationChanged = QtCore.pyqtSignal(int)
    yRotationChanged = QtCore.pyqtSignal(int)
    zRotationChanged = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.object = 0.
        self.xRot = 0.
        self.yRot = 0.
        self.zRot = 0.

        self.lastPos = QtCore.QPoint()

        self.cameraLookAt = [0.,0.,0.1,0.,0.,0.,0.,1.,0]

        self.scale = [.25, .25, .25]

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.trolltechParaview = QtGui.QColor.fromCmykF(.67, .66, .57, 0.0)
        self.trolltechYellow = QtGui.QColor.fromCmykF(.00, .02, .20, .0)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.updateGL()

    def initializeGL(self):
        self.qglClearColor(self.trolltechParaview)
        self.object = self.makeObject()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0., 0., -10.0)
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        gluLookAt(self.cameraLookAt[0],
                  self.cameraLookAt[1],
                  self.cameraLookAt[2],
                  self.cameraLookAt[3],
                  self.cameraLookAt[4],
                  self.cameraLookAt[5],
                  self.cameraLookAt[6],
                  self.cameraLookAt[7],
                  self.cameraLookAt[8])
        GL.glScaled(self.scale[0], self.scale[1], self.scale[2])
        GL.glCallList(self.object)

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = 0.0 -(event.x() - self.lastPos.x())
        dy = 0.0 - (event.y() - self.lastPos.y())

        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8.0 * dy)
            self.setYRotation(self.yRot + 8.0 * -dx)
        elif event.buttons() & QtCore.Qt.RightButton:
            dx = -(event.x() - self.lastPos.x())
            dy = -(event.y() - self.lastPos.y())
            mat = GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX)
            panSpeed = 150.0
            self.cameraLookAt = [self.cameraLookAt[0] + ((mat[0][0]*dx) + (mat[0][1]*dy))/panSpeed,  # move X
                                 self.cameraLookAt[1] + ((mat[1][0]*dx) + (mat[1][1]*dy))/panSpeed,  # move Y
                                 self.cameraLookAt[2] + ((mat[2][0]*dx) + (mat[2][1]*dy))/panSpeed,
                                 self.cameraLookAt[3] + ((mat[0][0]*dx) + (mat[0][1]*dy))/panSpeed,  # move X
                                 self.cameraLookAt[4] + ((mat[1][0]*dx) + (mat[1][1]*dy))/panSpeed,  # move Y
                                 self.cameraLookAt[5] + ((mat[2][0]*dx) + (mat[2][1]*dy))/panSpeed,  # move Z (-(x/2 + y/2))
                                 0.,  # facing v[0] (x) DEF: 0
                                 1.,  # facing v[1] (y) DEF: 1
                                 0.]  # facing v[2] (z) DEF: 0
            self.updateGL()

        self.lastPos = event.pos()

    def makeObject(self):

        global mesh_ref
        global ins_mesh_ref

        if len(mesh_ref) > 0 or len(ins_mesh_ref) > 0:

            genList = GL.glGenLists(1)
            GL.glNewList(genList, GL.GL_COMPILE)

            LightAmbient = [0.,0.,0.,.1]
            LightDiffuse = [5.,5.,5.,1.]
            LightPosition = [0.,1.,1.,0.]

            LightAmbient2 = [0.,0.,0.,.1]
            LightDiffuse2 = [2.,2.,2.,1.]
            LightPosition2 = [0.,-1.,-1.,0.]

            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_LIGHT0)
            GL.glEnable(GL.GL_LIGHT1)

            GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, LightAmbient2)
            GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, LightDiffuse2 )
            GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, LightPosition2 )

            GL.glLightfv( GL.GL_LIGHT1, GL.GL_AMBIENT, LightAmbient)
            GL.glLightfv( GL.GL_LIGHT1, GL.GL_DIFFUSE, LightDiffuse )
            GL.glLightfv( GL.GL_LIGHT1, GL.GL_POSITION, LightPosition )

            GL.glColorMaterial(GL.GL_FRONT, GL.GL_DIFFUSE)
            GL.glEnable(GL.GL_COLOR_MATERIAL)

            GL.glBegin(GL.GL_TRIANGLES)

            tuple(mesh_ref)
            for meshes in range(0, len(mesh_ref)):
                GL.glColor4f(mesh_ref[meshes][2][0],
                             mesh_ref[meshes][2][1],
                             mesh_ref[meshes][2][2],
                             mesh_ref[meshes][2][3])
                v = mesh_ref[meshes][1].vertices
                v = tuple(v)
                f = mesh_ref[meshes][1].faces
                f = tuple(f)
                for index in range(0, len(f)):
                    face = f[index]
                    U = (v[face[1]][0] - v[face[0]][0],
                         v[face[1]][1] - v[face[0]][1],
                         v[face[1]][2] - v[face[0]][2])
                    V = (v[face[2]][0] - v[face[0]][0],
                         v[face[2]][1] - v[face[0]][1],
                         v[face[2]][2] - v[face[0]][2])
                    Nx = U[1]*V[2] - U[2]*V[1]
                    Ny = U[2]*V[0] - U[0]*V[2]
                    Nz = U[0]*V[1] - U[1]*V[0]
                    GL.glNormal3d(Nx, Ny, Nz)
                    GL.glVertex3d(v[face[0]][0],
                                  v[face[0]][1],
                                  v[face[0]][2])
                    GL.glVertex3d(v[face[1]][0],
                                  v[face[1]][1],
                                  v[face[1]][2])
                    GL.glVertex3d(v[face[2]][0],
                                  v[face[2]][1],
                                  v[face[2]][2])
            list(mesh_ref)


            GL.glEnd()

            GL.glBegin(GL.GL_LINE_STRIP)
            
            tuple(ins_mesh_ref)
            for meshes in range(0, len(ins_mesh_ref)):
                GL.glColor4f(ins_mesh_ref[meshes][2][0],
                             ins_mesh_ref[meshes][2][1],
                             ins_mesh_ref[meshes][2][2],
                             ins_mesh_ref[meshes][2][3])
                v = ins_mesh_ref[meshes][1].vertices
                v = tuple(v)
                f = ins_mesh_ref[meshes][1].faces
                f = tuple(f)
                for index in range(0, len(f)):
                    face = f[index]
                    U = (v[face[1]][0] - v[face[0]][0],
                         v[face[1]][1] - v[face[0]][1],
                         v[face[1]][2] - v[face[0]][2])
                    V = (v[face[2]][0] - v[face[0]][0],
                         v[face[2]][1] - v[face[0]][1],
                         v[face[2]][2] - v[face[0]][2])
                    Nx = U[1]*V[2] - U[2]*V[1]
                    Ny = U[2]*V[0] - U[0]*V[2]
                    Nz = U[0]*V[1] - U[1]*V[0]
                    GL.glNormal3d(Nx, Ny, Nz)
                    GL.glVertex3d(v[face[0]][0],
                                  v[face[0]][1],
                                  v[face[0]][2])
                    GL.glVertex3d(v[face[1]][0],
                                  v[face[1]][1],
                                  v[face[1]][2])
                    GL.glVertex3d(v[face[2]][0],
                                  v[face[2]][1],
                                  v[face[2]][2])
            list(ins_mesh_ref)
            
            GL.glEnd()
            
            GL.glEndList()

            return genList

        else:
            genList = GL.glGenLists(1)
            GL.glNewList(genList, GL.GL_COMPILE)
            GL.glBegin(GL.GL_TRIANGLES)
            GL.glEnd()
            GL.glEndList()
            return genList

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.qglColor(self.trolltechGreen)

        GL.glVertex3d(x1, y1, -0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x3, y3, -0.05)
        GL.glVertex3d(x4, y4, -0.05)

        GL.glVertex3d(x4, y4, +0.05)
        GL.glVertex3d(x3, y3, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x1, y1, +0.05)

    def extrude(self, x1, y1, x2, y2):
        self.qglColor(self.trolltechGreen.dark(250 + int(100 * x1)))

        GL.glVertex3d(x1, y1, +0.05)
        GL.glVertex3d(x2, y2, +0.05)
        GL.glVertex3d(x2, y2, -0.05)
        GL.glVertex3d(x1, y1, -0.05)

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    #TODO: Fix
    def zoomin(self):
        self.scale = [self.scale[0]*1.1,self.scale[1]*1.1,self.scale[2]*1.1]
        self.updateGL()

    def zoomout(self):
        self.scale = [self.scale[0]/1.1,self.scale[1]/1.1,self.scale[2]/1.1]
        self.updateGL()

class MyPopupAbout(QtGui.QMainWindow, QtGui.QWidget, Ui_MainWindow):
    def __init__(self, parent=None):
        super(QtGui.QMainWindow, self).__init__()
        uic.loadUi('resources/About_page_Form.ui', self)
        self.btn_ok.clicked.connect(self.closeDialog)
        self.setWindowTitle('About')

    def closeDialog(self):
        self.hide()

class MyPopupSupport(QtGui.QMainWindow, QtGui.QWidget, Ui_MainWindow):
    def __init__(self, parent=None):
        super(QtGui.QMainWindow, self).__init__()
        uic.loadUi('resources/Support_page_Form.ui', self)
        self.btn_ok.clicked.connect(self.closeDialog)
        self.setWindowTitle('Support')

    def closeDialog(self):
        self.hide()

global app
out = -1
while out == -1:
    app = QtGui.QApplication(sys.argv)
    window = PyQtLink()
    window.show()
    out = app.exec_()
