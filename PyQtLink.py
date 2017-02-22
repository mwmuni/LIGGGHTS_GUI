#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
#import math
import os
#import ttk
#import numpy
#import stl
from stl import mesh
from Tkinter import *
import tkFileDialog
import subprocess
import OpenGL
import pickle
from os.path import basename
from OpenGL.arrays import vbo
#from OpenGL.GL import *
from OpenGL.GL import shaders
import OpenGL.GLU
#from OpenGL.GLU import *
from OpenGL.GLU import gluLookAt
#import OpenGL.GLUT
#from OpenGL.GLUT import *
from PyQt4 import QtCore, QtGui, uic, QtOpenGL
#from PyQt4.QtCore import Qt
#from PyQt4.QtOpenGL import *

qtCreatorFile = 'LIGGGHTS_DEM.ui'  # ui file

# Imports OpenGl, otherwise throws an error

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, 'OpenGL PyQtLink',
                               'PyOpenGL must be installed' +
                               ' to run this program.')
    sys.exit(1)

# Assign ui file <QtBaseClass is currently unused>
(Ui_MainWindow, QtBaseClass) = uic.loadUiType(qtCreatorFile)


class PyQtLink(QtGui.QMainWindow, Ui_MainWindow, QtGui.QWidget):

    def __init__(self):

        QtGui.QMainWindow.__init__(self)  # Initialize the main windows

        Ui_MainWindow.__init__(self)
        self.setupUi(self)  # Final ui initial setup

        # GUI Theme; options = {"plastique", "cde", "motif", "sgi", "windows",
        # "cleanlooks", "mac"}
        app.setStyle(QtGui.QStyleFactory.create("cleanlooks"))

        self.origPath = []

        global mesh_ref

        mesh_ref = []

#        new_mesh.normals
#
#        new_mesh.v0, new_mesh.v1, new_mesh.v2
#
#        print new_mesh.points

        #Modify this for loading new files
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

#        central = self.centralWidget()
        central = self.ogl
        central.setLayout(mainLayout)

#        mainLayout = QtGui.QHBoxLayout()
#        mainLayout.addWidget(self.glWidget)
#        mainLayout.addWidget(self.xSlider)
#        mainLayout.addWidget(self.ySlider)
#        mainLayout.addWidget(self.zSlider)
#        container = QtGui.QWidget()
#        self.setCentralWidget(container)
#        layout = QtGui.QVBoxLayout()
#        container.setLayout(layout)
        #self.setLayout(mainLayout)

#        self.xSlider.setValue(15 * 16)
#        self.ySlider.setValue(345 * 16)
#        self.zSlider.setValue(0 * 16)

        self.xSlider.setValue(0)
        self.ySlider.setValue(0)
        self.zSlider.setValue(0)

        # *.clicked is for a button click event
        # *.itemClicked is used for QtTreeWidget entries
        # *.*.connect(self.method) means that when the event happens,
        # that method is called

        self.addContactTypes()
        self.btn_geometry_autofit.clicked.connect(self.autofit)
        self.pushButton_Browse.clicked.connect(self.browse)
        self.btn_geometry_stl.clicked.connect(self.openstl)
        self.treeTest.itemClicked.connect(self.treeclick)
        self.tree_casesetup.itemClicked.connect(self.treecasesetup)
        self.tree_solve.itemClicked.connect(self.treesolve)
        self.tree_geometry.itemClicked.connect(self.treegeometry)
        self.btn_terminal.clicked.connect(self.terminal)
        self.btn_cube.clicked.connect(self.btn_cube_clicked)
        self.btn_sphere.clicked.connect(self.btn_sphere_clicked)
        self.btn_cylinder.clicked.connect(self.btn_cylinder_clicked)
        self.btn_plane.clicked.connect(self.btn_plane_clicked)
        self.btn_addinsertion.clicked.connect(self.btn_addinsertion_clicked)
        self.btn_addPSD.clicked.connect(self.btn_addPSD_clicked)
        self.btn_insertion_loadstl.clicked.connect(self.btn_insertion_loadstl_clicked)
        self.btn_insertion_rect.clicked.connect(self.btn_insertion_rect_clicked)
        self.btn_insertion_circle.clicked.connect(self.btn_insertion_circle_clicked)
        self.btn_removePSD.clicked.connect(self.btn_removePSD_clicked)
        self.btn_zoom_in.clicked.connect(self.btn_zoom_in_clicked)
        self.btn_zoom_out.clicked.connect(self.btn_zoom_out_clicked)
        self.btn_makefile.clicked.connect(self.fileGen)
        self.btn_saveas.clicked.connect(self.saveas)
        self.btn_open.clicked.connect(self.open)
        self.btn_addptcl.clicked.connect(self.btn_addptcl_clicked)
        self.btn_delptcl.clicked.connect(self.btn_delptcl_clicked)

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

        self.trolltechYellow = QtGui.QColor.fromCmykF(.00, .02, .20, .0)
        self.trolltechGrey = QtGui.QColor.fromCmykF(.4, .4, .4, 0)

#        a = (1, [2, 4], 3)
#        print a
#        a = list(a)
#        a[2] = 4
#        print a
#        a = tuple(a)
#        print a

        # If the value changes, the method will be called

        self.spnbox_geometry_contacttypes_totalgranulartypes\
            .valueChanged.connect(self.addContactTypes)
        self.spnbox_geometry_contacttypes_totalmeshtypes\
            .valueChanged.connect(self.addContactTypes)
        self.spnbox_insertion_fraction.valueChanged.connect(self.savePSD)

        self.spnbox_insertionindex.valueChanged.connect(
                self.loadInsertionSettings)
        self.spnbox_psd.valueChanged.connect(
                self.updateparticletypelist)

        self.spnbox_insertion_rect_centre_x.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_rect_centre_y.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_rect_centre_z.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_length.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_width.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_rect_normal_x.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_rect_normal_y.valueChanged.connect(
                self.insertionrectsave)
        self.spnbox_insertion_rect_normal_z.valueChanged.connect(
                self.insertionrectsave)

        self.spnbox_insertion_circle_centre_x.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_circle_centre_y.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_circle_centre_z.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_diameter.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_circle_normal_x.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_circle_normal_y.valueChanged.connect(
                self.insertioncirclesave)
        self.spnbox_insertion_circle_normal_z.valueChanged.connect(
                self.insertioncirclesave)

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

        self.line_ced.textChanged.connect(self.changecedlist)
        self.line_cor.textChanged.connect(self.changecorlist)
        self.line_kwear.textChanged.connect(self.changekwearlist)
        self.line_particlefriction.textChanged.connect(self.changeparticlelist)
        self.line_rollingfriction.textChanged.connect(self.changerollinglist)

        # If anything happens with the tree,
        # check if it was expected and perform action

        self.tree_geometry.viewport().installEventFilter(self)
        
        self.ogl.installEventFilter(self)

        self.stlFilesLoaded = []

        self.insertionList = []

        self.objHolder = self.tree_geometry.topLevelItem(1)

        self.materialdataini()

        self.loading = False

        self.meshProperties = []

        self.currentMeshType = ''

        self.fileName = ''

        # self.opengl_widget = GLWidget()

        self.setWindowTitle('LIGGGHTS GUI')

    def addContactTypes(self):
        self.meshTypeData = []
        self.totalTypes = \
            self.spnbox_geometry_contacttypes_totalgranulartypes.value() \
            + self.spnbox_geometry_contacttypes_totalmeshtypes.value()
        self.line_geometry_contacttypes_totaltypes.setText(str(self.totalTypes))
        self.combo_ced.clear()
        self.combo_cor.clear()
        self.combo_kwear.clear()
        self.combo_particlefriction.clear()
        self.combo_rollingfriction.clear()
        mtx = [['' for y in range(self.totalTypes+1)] for x in range(self.totalTypes+1)]
        self.combo_conty.clear()
        for x in range(0, self.totalTypes):
            self.combo_conty.addItem(str(x+1))
        for x in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                mtx[x][y] = str(x+1)+'_'+str(y+1)
                self.combo_ced.addItem(mtx[x][y])
                self.combo_cor.addItem(mtx[x][y])
                self.combo_kwear.addItem(mtx[x][y])
                self.combo_particlefriction.addItem(mtx[x][y])
                self.combo_rollingfriction.addItem(mtx[x][y])
        self.contactParams = [[0.0 for y in range(0, self.totalTypes**2)]
                              for x in range(0, 4)]
        self.contactParams.append([1.0 for y in range(0, self.totalTypes**2)])
        self.gmt = [[0.00, 0.00] for x in range(0, self.totalTypes)]
        self.listcedupdate()
        self.listcorupdate()
        self.listkwearupdate()
        self.listparticleupdate()
        self.listrollingupdate()
        self.loadMaterialData()
        # meshTypeData = numpy.zeros((totalTypes, 1, ))
        # index = (int(totalTypes**2/list.getIndex()),list.getIndex()%totalTypes)

    def autofit(self):
        global mesh_ref
        min_x = min_y = min_z = 99999
        max_x = max_y = max_z = 0.0
        
        for meshes in range(0, len(mesh_ref)):
            for index in range(0, len(mesh_ref[meshes][1])):
                if min_x > mesh_ref[meshes][1].points[index][0]:
                    min_x = mesh_ref[meshes][1].points[index][0]
                if min_x > mesh_ref[meshes][1].points[index][3]:
                    min_x = mesh_ref[meshes][1].points[index][3]
                if min_x > mesh_ref[meshes][1].points[index][6]:
                    min_x = mesh_ref[meshes][1].points[index][6]
                if min_y > mesh_ref[meshes][1].points[index][1]:
                    min_y = mesh_ref[meshes][1].points[index][1]
                if min_y > mesh_ref[meshes][1].points[index][4]:
                    min_y = mesh_ref[meshes][1].points[index][4]
                if min_y > mesh_ref[meshes][1].points[index][7]:
                    min_y = mesh_ref[meshes][1].points[index][7]
                if min_z > mesh_ref[meshes][1].points[index][2]:
                    min_z = mesh_ref[meshes][1].points[index][2]
                if min_z > mesh_ref[meshes][1].points[index][5]:
                    min_z = mesh_ref[meshes][1].points[index][5]
                if min_z > mesh_ref[meshes][1].points[index][8]:
                    min_z = mesh_ref[meshes][1].points[index][8]
                if max_x < mesh_ref[meshes][1].points[index][0]:
                    max_x = mesh_ref[meshes][1].points[index][0]
                if max_x < mesh_ref[meshes][1].points[index][3]:
                    max_x = mesh_ref[meshes][1].points[index][3]
                if max_x < mesh_ref[meshes][1].points[index][6]:
                    max_x = mesh_ref[meshes][1].points[index][6]
                if max_y < mesh_ref[meshes][1].points[index][1]:
                    max_y = mesh_ref[meshes][1].points[index][1]
                if max_y < mesh_ref[meshes][1].points[index][4]:
                    max_y = mesh_ref[meshes][1].points[index][4]
                if max_y < mesh_ref[meshes][1].points[index][7]:
                    max_y = mesh_ref[meshes][1].points[index][7]
                if max_z < mesh_ref[meshes][1].points[index][2]:
                    max_z = mesh_ref[meshes][1].points[index][2]
                if max_z < mesh_ref[meshes][1].points[index][5]:
                    max_z = mesh_ref[meshes][1].points[index][5]
                if max_z < mesh_ref[meshes][1].points[index][8]:
                    max_z = mesh_ref[meshes][1].points[index][8]
#                GL.glVertex3d(mesh_ref[meshes][1].points[index][0],
#                              mesh_ref[meshes][1].points[index][1],
#                              mesh_ref[meshes][1].points[index][2])
#                GL.glVertex3d(mesh_ref[meshes][1].points[index][3],
#                              mesh_ref[meshes][1].points[index][4],
#                              mesh_ref[meshes][1].points[index][5])
#                GL.glVertex3d(mesh_ref[meshes][1].points[index][6],
#                              mesh_ref[meshes][1].points[index][7],
#                              mesh_ref[meshes][1].points[index][8])
#        for n :

        self.boundary_min_x.setValue(min_x)
        self.boundary_min_y.setValue(min_y)
        self.boundary_min_z.setValue(min_z)

        self.boundary_max_x.setValue(max_x)
        self.boundary_max_y.setValue(max_y)
        self.boundary_max_z.setValue(max_z)

    def browse(self):
        subprocess.Popen(['xdg-open',
                         os.path.dirname(os.path.realpath(__file__))])

    #  insertionList = [([(particleType, particleFriction)],
    #                    (faceType<-1 to 2>, (faceParams,,,))
    #                    (massParams,,,))]
    def btn_addinsertion_clicked(self):
        self.loading = True
        self.stack_insertionsettings.setCurrentIndex(1)
#        self.insertionList.append(([], (-1, None),
#                                    (0.00, 0.00, 0, 0, 0, 0.00)))
        self.insertionList.append([[[]], [-1, None],
                                    [0.00, 0.00, 0.00, 0.00, 0.00, 0.00]])
#        print self.insertionList
        self.spnbox_insertionindex.setValue(len(self.insertionList))
        self.loading = True
        self.spnbox_granulartypeindex.setValue(1)
        for n in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            self.insertionList[self.spnbox_insertionindex.value()-1][0][
                     self.spnbox_psd.value()-1].append(
                        [[str(self.spnbox_psd.value())+'_'+'p'+str(n+1)+
                         '_1', 0.0, 0.0, 0.0]])
        self.combo_particlelist.clear()
        for n in range(0, len(self.insertionList[
                self.spnbox_insertionindex.value()-1][
                        0][self.spnbox_psd.value()-1][0])):
            self.combo_particlelist.addItem(
                    self.insertionList[
                            self.spnbox_insertionindex.value()-1][
                                    0][self.spnbox_psd.value()-1][0][n][0])
        self.spnbox_psd.setValue(1)
        adding = 0
        for n in range(0, len(self.insertionList[self.spnbox_insertionindex.value()-1
                          ][0][self.spnbox_psd.value()-1][
                                  self.spnbox_granulartypeindex.value()-1])):
            adding += self.insertionList[self.spnbox_insertionindex.value()-1
                          ][0][self.spnbox_psd.value()-1][
                                  self.spnbox_granulartypeindex.value()-1][n][1]
        self.lbl_PSDFractionTotal.setText(str(adding))
#        self.updateparticletypelist()
        self.loading = True
        self.resetinsertionface()
        self.loading = True
        self.resetmassproperties()
        self.loading = False

    # TODO: EXTEND THIS
    def btn_addPSD_clicked(self):
        if not self.loading:
            self.loading = True
            self.spnbox_psd.setValue(len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][0])+1)
            self.spnbox_granulartypeindex.setValue(1)
            self.insertionList[self.spnbox_insertionindex.value()-1][0].append(
                    [])
            for n in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
                    self.insertionList[self.spnbox_insertionindex.value()-1][0][
                         self.spnbox_psd.value()-1].append(
                            [[str(self.spnbox_psd.value())+'_'+'p'+str(n+1)+
                             '_1', 0.0, 0.0, 0.0]])
            self.combo_particlelist.clear()
            for n in range(0, len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1])):
                self.combo_particlelist.addItem(
                        self.insertionList[
                                self.spnbox_insertionindex.value()-1][0][
                                        self.spnbox_psd.value()-1][
                                                self.spnbox_granulartypeindex.value()-1][n][0])
            self.loading = False

    def btn_cube_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(2)

    def btn_cylinder_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(4)

    def btn_addptcl_clicked(self):
        self.insertionList[
                self.spnbox_insertionindex.value()-1][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1
                ].append([str(self.spnbox_psd.value())+
                    '_p'+str(self.spnbox_granulartypeindex.value())+
                    '_'+str(len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][0][
                    self.spnbox_psd.value()-1][
                    self.spnbox_granulartypeindex.value()-1])+1), 0.0, 0.0, 0.0])
        self.updateparticlelist()
        self.combo_particlelist.setCurrentIndex(
                self.combo_particlelist.count()-1)

    def btn_delptcl_clicked(self):
        if len(self.insertionList[
                self.spnbox_insertionindex.value()-1][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1]) > 1:
            del self.insertionList[
                self.spnbox_insertionindex.value()-1][0][
                self.spnbox_psd.value()-1][
                self.spnbox_granulartypeindex.value()-1][
                self.combo_particlelist.currentIndex()]
            self.renewparticlenames()
            

    def btn_insertion_circle_clicked(self):
        self.stack_insertion_face.setCurrentIndex(3)
        self.insertioncirclesave()

    def btn_insertion_loadstl_clicked(self):
        self.stack_insertion_face.setCurrentIndex(1)

    def btn_insertion_rect_clicked(self):
        self.stack_insertion_face.setCurrentIndex(2)
        self.insertionrectsave()

#    def btn_makefile_clicked(self):
#        self.fileGen()

    def btn_plane_clicked(self):
        self.stack_geometry_meshes.setCurrentIndex(5)

    def btn_removePSD_clicked(self):
        if len(self.insertionList[
                self.spnbox_insertionindex.value()-1][0]) > 1:
            tempInt = self.spnbox_psd.value()
            del self.insertionList[
                self.spnbox_insertionindex.value()-1][0][
                        self.spnbox_psd.value()-1]
            self.renewparticlenames()
            self.spnbox_psd.setValue(tempInt-1)

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
            self.savemeshproperties()
            self.loading = False

    def chk_meshes_sav_clicked(self):
        self.stack_meshes_sav.setCurrentIndex(
                self.chk_meshes_sav.checkState()/2)
        if not self.loading:
            self.loading = True
            self.chk_meshes_sv.setCheckState(0)
            self.savemeshproperties()
            self.loading = False

    def chk_meshes_mm_clicked(self):
        self.stack_meshes_mm.setCurrentIndex(
                self.chk_meshes_mm.checkState()/2)
        self.savemeshproperties

    def clearinsertionface(self):
        temp = self.insertionList[self.spnbox_insertionindex.value()][1]
        self.resetinsertionface()
        self.insertionList[self.spnbox_insertionindex.value()][1] = temp

    def  clearmeshproperties(self):
        self.loading = True
        self.stack_geometry_meshes.setCurrentIndex(0)
        # TODO: self.combo_meshes_ct {SELECT CHOSEN ITEM INDEX}
        self.chk_meshes_cm.setCheckState(0)
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
        # TODO: Load tree definitions
        self.loading = False

# ....def contextMenuEvent(self, event):
# ........self.menu = QtGui.QMenu(self)
# ........renameAction = QtGui.QAction('Rename', self)
# ........renameAction.triggered.connect(lambda: self.renameSlot(event))
# ........self.menu.addAction(renameAction)
# ........self.menu.popup(QtGui.QCursor.pos())

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
                # print 'Double click'
                self.tree_geometry.setCurrentItem(item)
                self.loadmeshproperties(item)
            else:
                self.tree_geometry.setCurrentItem(item)
                self.treegeometry()
#        self.ogl.viewport()
        elif event.type() == QtCore.QEvent.Wheel \
                and str(target) == str(self.ogl):
            self.glWidget.zoomin() if event.delta() == 120 else self.glWidget.zoomout()
        return False

    def fileGen(self):
        f = open('script.s', 'w')
        f.write('# TUNRA BULK SOLIDS LIGGGHTS DEM Simulation File\n')
        f.write('# For technical support, please contact\n')
        f.write('# Wei Chen: W.Chen@newcastle.edu.au\n\n')
        f.write('#-------------------------------------------------------------------------------------------------\n')
        f.write('# Variables - Declaration & Pass on to Simulations\n')
        f.write('variable\tpi\t\tequal\t\t3.141592654\t\t# PI\n')
        f.write('variable\ta\t\tequal\t\t1\t\t\t\t# Test number\n\n')
        f.write('# Variables - Timestep & Dumpstep\n')
        if self.chk_timestep.checkState() == 2:
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
#        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
#            for y in range(x, self.totalTypes):
#                f.write('variable\td'+ str(x+1) + '_' + str(y+1) +  # TODO: REPLACE WITH PARTICLE
#                        '\t\t\tequal\t\t'+'40'+  # TODO: REPLACE WITH PARTICLE DIAMETER
#                        '\t# d='+'40'+'mm\n')  # TODO: REPLACE WITH PARTICLE DIAMETER
#        f.write('\n')
        for x in range(0, len(self.insertionList[0][0])):
            for y in range(0, len(self.insertionList[0][0][x])):
                for z in range(0, len(self.insertionList[0][0][x][y])):
                    f.write('variable\td')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('\t\t\tequal\t\t')
                    f.write(str(self.insertionList[0][0][x][y][z][2]))
                    f.write('\n')
        f.write('\n')
#        for x in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
#            for y in range(x, self.totalTypes):
#                f.write('variable\tr'+ str(x+1) + '_' + str(y+1) +  # TODO: REPLACE WITH PARTICLE
#                        '\t\t\tequal\t\t${d'+ str(x+1) + '_' + str(y+1) +  # TODO: REPLACE WITH PARTICLE
#                        '}/2000\n')
        for x in range(0, len(self.insertionList[0][0])):
            for y in range(0, len(self.insertionList[0][0][x])):
                for z in range(0, len(self.insertionList[0][0][x][y])):
                    f.write('variable\tr')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('\t\t\tequal\t\t${d')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('}/2000\n')
        f.write('\n')

        # TODO: Add support for multiple insertions
        f.write('\n# Variable - particle size fractions\n')
#        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
#            for y in range(x, self.totalTypes):
#                f.write('variable\tfrac'+ str(x+1) + '_' + str(y+1) +  # TODO: REPLACE WITH PARTICLE
#                        '\t\t\tequal\t\t'+ str(self.insertionList[0][0][x+y][1]) +
#                        '\n')
        largestVal = 0.0
        largestName = ''
        for x in range(0, len(self.insertionList[0][0])):
            for y in range(0, len(self.insertionList[0][0][x])):
                for z in range(0, len(self.insertionList[0][0][x][y])):
                    f.write('variable\tfrac')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('\t\t\tequal\t\t')
                    f.write(str(self.insertionList[0][0][x][y][z][1]))
                    if largestVal < self.insertionList[0][0][x][y][z][1] or \
                        largestName == '':
                        largestVal = self.insertionList[0][0][x][y][z][1]
                        largestName = self.insertionList[0][0][x][y][z][0]
                    f.write('\n')
        f.write('\n')
        # TODO: FOLLOW UP CUTOFF
        f.write('\n# Define contact searching distance\n')
        f.write('variable\tcutoff\t\t\tequal\t\t${d'+
                largestName+'}/1000\n\n')

        # TODO: FOLLOW UP THIS
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
        for x in range (0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
            for y in range(x, self.totalTypes):
                f.write('variable\tdens'+ str(x+1) + '_' + str(y+1) +  # TODO: REPLACE WITH PARTICLE
                        '\t\tequal\t\t'+'4400'+'\n')  # TODO: REPLACE WITH PARTICLE DENSITY
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
        f.write('variable\tm\t\tequal\t\t' +
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][0])+
                '\t\t\t# Total Mass to be inserted\n')
        f.write('variable\ttfill\tequal\t\t'+
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][0]/
                self.insertionList[self.spnbox_insertionindex.value()-1][2][1])
                +'\t\t\t\t# Time for generating particles [s]\n')
        f.write('variable\tQ\t\tequal\t\t${m}/${tfill}\t# Mass flow rate @ ~2000 t/h\n\n')

        f.write('# Variables - Definition of times (points when simulation behaviour changes)\n')
        f.write('variable\tt1\t\tequal\t${tfill}\t\t\t\t# Time for inserting particles\n')
        if not self.line_totaltime.text().isEmpty():
            f.write('variable\tt2\t\tequal\t'+self.line_totaltime.text()+'\n')
        f.write('variable\tsteps1\tequal\t${t1}*${factor}\t\t# Convert time to computational steps\n')
        if not self.line_totaltime.text().isEmpty():
            f.write('variable\tsteps2\tequal\t${t2}*${factor}\n\n')

        f.write('######################################################################################################################\n\n')

        f.write('# Granular Model and Computational Setting\n')
        f.write('atom_style\t\tgranular\t\t# Granular style for LIGGGHTS\n\n')
        f.write('atom_modify\t\tmap_array\t\t# The map keyword determines how atom ID lookup is done for molecular problems.\n')
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

        f.write('create_box\t\t'+str(self.totalTypes)+' reg\t\t# Numbers of atome (particle / wall) types\n')
        f.write('\t\t\t\t\t\t\t# type 1: inserted particles\n')
        f.write('\t\t\t\t\t\t\t# type 2: belts and walls\n\n')

        f.write('neighbor\t\t${cutoff} bin\t\t# Defines parameter for contact searching\n\n')

        f.write('neigh_modify\tdelay 0\t\t# Define the neighbor list building time\n\n')

        f.write('# Material properties required for new pair styles\n\n')

        f.write('fix\t\tm1 all property/global youngsModulus peratomtype')
        for n in range(0, len(self.gmt)):
            f.write(' ' + str(self.gmt[n][0]))
        f.write('\n\n')

        f.write('fix\t\tm2 all property/global poissonsRatio peratomtype ')
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

        f.write('pair_style gran model hertz tangential history')
        if self.cbox_ptcl_cohesionmodel.currentIndex() == 1:
            f.write(' cohesion sjkr')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 2:
            f.write(' cohesion sjkr2')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 3:
            f.write(' cohesion easo')
        elif self.cbox_ptcl_cohesionmodel.currentIndex() == 4:
            f.write(' cohesion washino')
        if self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 1:
            f.write(' rolling_friction CDT')
        elif self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 2:
            f.write(' rolling_friction epsd')
        elif self.cbox_ptcl_rollingfrictionmodel.currentIndex() == 3:
            f.write(' rolling_friction epsd2')
        f.write('\n\n')

        f.write('pair_coeff * *\n\n')

        f.write('timestep\t${dt}\n\n')

        # TODO: Link gravity vector
        f.write('fix\t\tgravi all gravity 9.81 vector ')
        if self.rad_gravity_x.isChecked():
            f.write('-1.0 0.0 0.0')
        elif self.rad_gravity_y.isChecked():
            f.write('0.0 -1.0 0.0')
        elif self.rad_gravity_z.isChecked():
            f.write('0.0 0.0 -1.0')
        f.write('\n\n')

        f.write('############# ADD LOADED MESHES ##############\n\n')

        # Relative directory file locator
        relDir = []
        cwd = os.path.split(os.getcwd())[1]
        for paths in self.stlFilesLoaded:
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

        for n in range(0, len(relDir)):
            f.write('fix\t\t' +
                    os.path.splitext(os.path.basename(relDir[n]))[0] +
                    ' all mesh/surface')
            if self.meshProperties[n][14]:
                f.write('/stress')
            f.write(' file ' +
                    relDir[n] +
                    ' type 2 ')
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
            if self.meshProperties[n][14]:
                f.write('wear finnie ')
            f.write('curvature 1e-6\n\n')

        f.write('fix\t\twall all wall/gran model hertz tangential history')
        if self.cbox_mesh_cohesionmodel.currentIndex() == 1:
            f.write(' cohesion sjkr')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 2:
            f.write(' cohesion sjkr2')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 3:
            f.write(' cohesion easo')
        elif self.cbox_mesh_cohesionmodel.currentIndex() == 4:
            f.write(' cohesion washino')
        if self.cbox_mesh_rollingfrictionmodel.currentIndex() == 1:
            f.write(' rolling_friction CDT')
        elif self.cbox_mesh_rollingfrictionmodel.currentIndex() == 2:
            f.write(' rolling_friction epsd')
        elif self.cbox_mesh_rollingfrictionmodel.currentIndex() == 3:
            f.write(' rolling_friction epsd2')

        f.write(' mesh n_meshes ' + str(self.objHolder.childCount()) + ' meshes')
        for items in self.stlFilesLoaded:
            f.write(' ' + os.path.splitext(os.path.basename(items))[0])
        f.write('\n\n')

        f.write('# Particle distributions for insertion\n')
        for x in range(0, len(self.insertionList[0][0])):
            for y in range(0, len(self.insertionList[0][0][x])):
                for z in range(0, len(self.insertionList[0][0][x][y])):
                    f.write('fix\t\tpts')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write(' all particletemplate/sphere 1 atom_type 1 ')
                    f.write('density constant ${dens')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('} radius constant ${r')
                    f.write(self.insertionList[0][0][x][y][z][0])
                    f.write('}\n')
        f.write('\n')

        for x in range(0, len(self.insertionList[0][0])):
            numParticles = 0
            f.write('fix\t\tpdd'+'1'+'_'+str(x+1))
            f.write(' all particledistribution/discrete 1. ')
            strbuild = ''
            for y in range(0, len(self.insertionList[0][0][x])):
                for z in range(0, len(self.insertionList[0][0][x][y])):
                    numParticles += 1
                    strbuild += ' pts' + self.insertionList[0][0][x][y][z][0]
                    strbuild += ' ${frac' + self.insertionList[0][0][x][y][z][0] + '}'
                if y == len(self.insertionList[0][0][x])-1:
                    f.write(str(numParticles) + strbuild + '\n')
        f.write('\n')

        f.write('#######DEFAULT########\n\n')
        f.write('fix\t\tins_mesh1 all mesh/surface file CAD/gen_face.stl type 2 curvature 1e-6\n\n')
        f.write('fix\t\tins1 all insert/stream seed 5330 distributiontemplate pdd1 &\n')
        f.write('\t\tmaxattempt 100 mass ${m} massrate ${Q} overlapcheck yes vel constant '+
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][2])+' '+
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][3])+' '+
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][4])+' '+'.&\n')
        f.write('\t\tinsertion_face ins_mesh1 extrude_length '+
                str(self.insertionList[self.spnbox_insertionindex.value()-1][2][5])+'\n\n')
        f.write('######################\n\n')

        f.write('fix\t\tintegr all nve/sphere\n\n')

        f.write('# Output settings, include total thermal energy\n')
        f.write('fix\t\t\t\tts all check/timestep/gran 1000 0.1 0.1\n')
        f.write('compute\t\t\trke all erotate/sphere\n')
        f.write('#computefix\t\tfc all pair/gran/local pos id force\n')
        f.write('thermo_style\tcustom step atoms ke c_rke f_ts[1] f_ts[2] vol\n')
        f.write('thermo\t\t\t1000\n')
        f.write('thermo_modify\tlost ignore norm no\n')
        f.write('compute_modify\tthermo_temp dynamic yes\n\n')

        f.write('dump\t\tdmpstl1 all mesh/stl 1 post/static.stl')
        for n in range(0, len(relDir)):
            f.write(' ' + os.path.splitext(os.path.basename(relDir[n]))[0])
        f.write('\n\n')

        f.write('dump\t\tdmp_m all custom ${dumpstep} post/dump_*.liggghts '+
                'id type '+
                ('x y z ' if self.chk_coordinates.checkState() == 2 else '') +
                ('ix iy iz ' if self.chk_inertia.checkState() == 2 else '') +
                ('vx vy vz ' if self.chk_velocity.checkState() == 2 else '') +
                ('fx fy fz ' if self.chk_force.checkState() == 2 else '') +
                ('omegax omegay omegaz ' if self.chk_angularvelocity.checkState == 2 else '') +
                'radius ' +
                ('mass' if self.chk_mass.checkState() == 2 else '') + '\n\n')

        for i in self.meshProperties:
            if i[13]:
                tempstr = os.path.splitext(i[0])[0]
                f.write('dump\t\tdumpstress_'+tempstr)
                f.write(' all mesh/gran/VTK ${dumpstep} post/dump_')
                f.write(tempstr + '*.vtk stress wear ')
                f.write(tempstr + '\n\n')

        f.write('run\t\t1\n\n')

        f.write('undump\t\tdumpstl1\n\n')

        f.write('run\t\t${steps1}\n\n')

        if not self.line_totaltime.text().isEmpty():
            f.write('run\t\t${steps2}')

    def insertioncirclesave(self):
        if not self.loading:
            self.insertionList[self.spnbox_insertionindex.value()-1][1] = [2,
                    [self.spnbox_insertion_circle_centre_x.value(),
                    self.spnbox_insertion_circle_centre_y.value(),
                    self.spnbox_insertion_circle_centre_z.value(),
                    self.spnbox_insertion_diameter.value(),
                    self.spnbox_insertion_circle_normal_x.value(),
                    self.spnbox_insertion_circle_normal_y.value(),
                    self.spnbox_insertion_circle_normal_z.value()]]

    def insertionmasssave(self):
        if not self.loading:
            self.insertionList[self.spnbox_insertionindex.value()-1][2] = [
                    self.spnbox_totalmass.value(),
                    self.spnbox_massrate.value(),
                    self.spnbox_insertion_mass_x.value(),
                    self.spnbox_insertion_mass_y.value(),
                    self.spnbox_insertion_mass_z.value(),
                    self.spnbox_insertion_extrude.value()]

    def insertionrectsave(self):
        if not self.loading:
            self.insertionList[self.spnbox_insertionindex.value()-1][1] = [1,
                    [self.spnbox_insertion_rect_centre_x.value(),
                    self.spnbox_insertion_rect_centre_y.value(),
                    self.spnbox_insertion_rect_centre_z.value(),
                    self.spnbox_insertion_length.value(),
                    self.spnbox_insertion_width.value(),
                    self.spnbox_insertion_rect_normal_x.value(),
                    self.spnbox_insertion_rect_normal_y.value(),
                    self.spnbox_insertion_rect_normal_z.value()]]

    def listcedupdate(self):
        self.line_ced.setText(str(self.contactParams[3][
                self.combo_ced.currentIndex()]))

    def listcorupdate(self):
#        print self.contactParams
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

    def loadInsertionSettings(self):
        if self.spnbox_insertionindex.value() > len(self.insertionList):
            self.spnbox_insertionindex.setValue(len(self.insertionList))
            return -1
        elif self.spnbox_insertionindex.value() < 1 and \
                len(self.insertionList) > 0:
            self.spnbox_insertionindex.setValue(1)
            return -1
        currSettings = self.insertionList[self.spnbox_insertionindex.value()-1]
        if len(currSettings[0]) > 0:
            self.spnbox_psd.setValue(0)
            self.spnbox_psd.setValue(1)  # Will call valueChanged
        else:
            self.spnbox_psd.setValue(0)
        self.resetinsertionface()
        if currSettings[1][0] == -1:
            self.stack_insertion_face.setCurrentIndex(0)
        elif currSettings[1][0] == 0:
            self.stack_insertion_face.setCurrentIndex(1)
            # TODO: Add STL functionality
        elif currSettings[1][0] == 1:
            self.loading = True
            self.stack_insertion_face.setCurrentIndex(2)
            self.spnbox_insertion_rect_centre_x.setValue(
                    currSettings[1][1][0])
            self.spnbox_insertion_rect_centre_y.setValue(
                    currSettings[1][1][1])
            self.spnbox_insertion_rect_centre_z.setValue(
                    currSettings[1][1][2])
            self.spnbox_insertion_length.setValue(
                    currSettings[1][1][3])
            self.spnbox_insertion_width.setValue(
                    currSettings[1][1][4])
            self.spnbox_insertion_rect_normal_x.setValue(
                    currSettings[1][1][5])
            self.spnbox_insertion_rect_normal_y.setValue(
                    currSettings[1][1][6])
            self.spnbox_insertion_rect_normal_z.setValue(
                    currSettings[1][1][7])
        elif currSettings[1][0] == 2:
            self.loading = True
            self.stack_insertion_face.setCurrentIndex(3)
            self.spnbox_insertion_circle_centre_x.setValue(
                    currSettings[1][1][0])
            self.spnbox_insertion_circle_centre_y.setValue(
                    currSettings[1][1][1])
            self.spnbox_insertion_circle_centre_z.setValue(
                    currSettings[1][1][2])
            self.spnbox_insertion_diameter.setValue(
                    currSettings[1][1][3])
            self.spnbox_insertion_circle_normal_x.setValue(
                    currSettings[1][1][4])
            self.spnbox_insertion_circle_normal_y.setValue(
                    currSettings[1][1][5])
            self.spnbox_insertion_circle_normal_z.setValue(
                    currSettings[1][1][6])
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
        # print self.gmt
        self.loading = True
#        if(self.spnbox_casesetup_materialproperties_materialtype.value() >
#           self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
#            (self.spnbox_casesetup_materialproperties_materialtype
#                 .setValue(self.spnbox_geometry_contacttypes_totalgranulartypes.value()))
        # save current page

        # load selected page
        self.line_youngsmodulus.setText(str(self.gmt[
                self.combo_conty.currentIndex()][0]))
        self.spnbox_poissonsratio.setValue(self.gmt[
                self.combo_conty.currentIndex()][1])
#        curVal = \
#            self.spnbox_casesetup_materialproperties_materialtype.value()-1
#        self.line_youngsmodulus.setText(str(self.gmt[curVal][0]))
#        self.spnbox_poissonsratio.setValue(self.gmt[curVal][1])
        self.loading = False
        #[((0.0, 0.0), [('1_1', 0.0, 0.0)]), ((0.0, 0.0), [('2_1', 0.0, 0.0)])]

    def loadmeshproperties(self, item):
        global mesh_ref
        self.stack_geometry_meshes.setCurrentIndex(1)
        for index in self.origPath:
            if index[1] == item.text(0):
                self.fileName = index[0]
                break
#        new_mesh.mesh.Mesh.from_file(self.fileName)
        for n in range(0, len(mesh_ref)):
            if mesh_ref[n][0] == self.fileName:
                mesh_ref[n][2] = [1.00, .98, .80, 1.0]
            else:
                mesh_ref[n][2] = [.4, .4, .4, 0]
        self.glWidget.initializeGL()
#        self.glWidget.makeObject()
        self.glWidget.updateGL()
        self.glWidget.paintGL()
        self.loading = True
        for i in self.meshProperties:
#            print i[0]
            if i[0] == item.text(0):
                # Load data
                self.currentMeshType = self.meshProperties.index(i)
                # TODO: self.combo_meshes_ct {SELECT CHOSEN ITEM INDEX}
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
                # TODO: Load tree definitions
                self.loading = False
                break

    def materialdataini(self):
        self.currentMaterialType = 0
        self.combo_particlelist.clear()
        curVal = self.combo_conty.currentIndex()
        self.line_youngsmodulus.setText(str(self.gmt[curVal][0]))
        self.spnbox_poissonsratio.setValue(self.gmt[curVal][1])

    def open(self):
#        root = Tk()
#        root.fileName = \
#            tkFileDialog.askopenfilename(filetypes=(('LIGGGHTS_GUI File',
#                                                     '.proj'), ('All Files',
#                                                                '.*')))
        settings = QtCore.QSettings('myorg', 'myapp')
        self.restoreGeometry(settings.value('geometry').toByteArray())
        self.restoreState(settings.value('windowState').toByteArray())
        inFile = open('pickleTest.txt', 'rb')
        vars = pickle.load(inFile)
        self.contactParams = vars[0]
        self.currentMaterialType = vars[1]
        self.currentMeshType = vars[2]
        self.fileName = vars[3]
        self.gmt = vars[4]
        self.insertionList = vars[5]
        self.meshProperties = vars[6]
        self.meshTypeData = vars[7]
        self.origPath = vars[8]
        self.stlFilesLoaded = vars[9]
        self.totalTypes = vars[10]
#                vars = [self.contactParams, self.currentMaterialType,
#                self.currentMeshType, self.fileName, self.gmt,
#                self.insertionList, self.meshProperties, self.meshTypeData,
#                self.origPath, self.stlFilesLoaded,
#                self.totalTypes]

        # print(root.fileName)
        # Load .proj file into variables

#        root.destroy()

    def openMenu(position):
        menu = QMenu()
        quitAction = menu.addAction('Quit')
        action = menu.exec_(tableWidget.mapToGlobal(position))
        if action == quitAction:
            exit()

    def openstl(self):
        global mesh_ref
        root = Tk()
#        root.style = ttk.Style()
#        root.style.theme_use("default")
        # ('clam', 'alt', 'default', 'classic')
        self.fileName = tkFileDialog.askopenfilename(
                filetypes=(('STereoLithography files', '.stl'),
                           ('All Files', '.*')))
        if self.fileName not in self.stlFilesLoaded and \
                os.path.exists(os.path.dirname(self.fileName)):
            #Load model into opengl viewer
#            file_name = os.path.dirname(os.path.realpath(__file__))+"/Example/" + \
#                                       "deliver_belt_2.stl"
#            new_mesh = mesh.Mesh.from_file(file_name)
            self.origPath.append([self.fileName,basename(self.fileName)])
            tempVar = mesh.Mesh.from_file(self.fileName)
            for n in range(0, len(mesh_ref)):
                mesh_ref[n][2] = [.4, .4, .4, 0]
            mesh_ref.append([self.fileName, tempVar, [1., .98, .80, 1.0]])
            self.glWidget.initializeGL()
            self.glWidget.updateGL()
            self.glWidget.paintGL()
            root.destroy()
            #Create tree element
            tempChild = QtGui.QTreeWidgetItem(self.objHolder)
            tempChild.setText(0, QtCore.QString(basename(self.fileName)))
            #Store name to prevent duplicates
            self.stlFilesLoaded.append(self.fileName)
            #Expand the parent in the tree
            self.objHolder.setExpanded(True)
            #Sort the children
            self.objHolder.sortChildren(0, 0)  # (0, 0) = ASC, (0, 1) = DESC
            #Make a new list for storing mesh data
            self.meshProperties.append([basename(self.fileName), 'CT', False,
                                        False, 0.00, 0.00, 0.00,
                                        False, 0.00, 0.00, 0.00,
                                        False, 0.00, False, False,
                                        0.00, 0.00, 0.00, 0.00, []])
            # self.currentMeshType = basename(root.fileName)
            self.currentMeshType = len(self.meshProperties)-1
            self.stack_geometry_meshes.setCurrentIndex(1)
            self.loadmeshproperties(tempChild)
#        root.destroy()

    def renewparticlenames(self):
        for x in range(0, len(self.insertionList[
                self.spnbox_insertionindex.value()-1][0])):
                for y in range(0, len(self.insertionList[
                self.spnbox_insertionindex.value()-1][0][x])):
                    for z in range(0, len(self.insertionList[
                self.spnbox_insertionindex.value()-1][0][x][y])):
                        self.insertionList[
                self.spnbox_insertionindex.value()-1][0][x][y][z][0] = \
                                str(x+1)+'_p'+str(y+1)+'_'+str(z+1)
        self.updateparticlelist()

    def resetinsertionface(self):
        # Store old values
        temp = self.insertionList[self.spnbox_insertionindex.value()-1][1]

        self.loading = True

        # Reset rectangle field
        self.spnbox_insertion_rect_centre_x.setValue(0.00)
        self.spnbox_insertion_rect_centre_y.setValue(0.00)
        self.spnbox_insertion_rect_centre_z.setValue(0.00)
        self.spnbox_insertion_length.setValue(0.00)
        self.spnbox_insertion_width.setValue(0.00)
        self.spnbox_insertion_rect_normal_x.setValue(0.00)
        self.spnbox_insertion_rect_normal_y.setValue(0.00)
        self.spnbox_insertion_rect_normal_z.setValue(0.00)

        # Reset circle field
        self.spnbox_insertion_circle_centre_x.setValue(0.00)
        self.spnbox_insertion_circle_centre_y.setValue(0.00)
        self.spnbox_insertion_circle_centre_z.setValue(0.00)
        self.spnbox_insertion_diameter.setValue(0.00)
        self.spnbox_insertion_circle_normal_x.setValue(0.00)
        self.spnbox_insertion_circle_normal_y.setValue(0.00)
        self.spnbox_insertion_circle_normal_z.setValue(0.00)

        self.loading = False

        # Load old values
        self.insertionList[self.spnbox_insertionindex.value()-1][1] = temp

    def resetmassproperties(self):
        self.loading = True
        self.spnbox_totalmass.setValue(0.00)
        self.spnbox_massrate.setValue(0.00)
        self.spnbox_insertion_mass_x.setValue(0.00)
        self.spnbox_insertion_mass_y.setValue(0.00)
        self.spnbox_insertion_mass_z.setValue(0.00)
        self.spnbox_insertion_extrude.setValue(0.00)
        self.loading = False

        # objHolder.addChild(self.tree_geometry.indexFromItem(objHolder).row(),QtGui.QTreeWidgetItem(QtCore.QString().startsWith(QtCore.QLatin1String("test1"))))
        # objHolder.addChild(self.tree_geometry.indexFromItem(objHolder).row(),QtGui.QTreeWidgetItem(QtCore.QString().startsWith(QtGui.QLatin1String("test1"))))
        # objHolder.addChild(QtGui.QTreeWidgetItem(QtCore.QString().startsWith(QtCore.QLatin1String("test1"))))
        # objHolder.addChild(self.tree_geometry.indexFromItem(objHolder).row(),QtGui.QTreeWidgetItem(QtCore.QString("test")))
        # objHolder.addChild(QtGui.QTreeWidgetItem(QtCore.QString("test")))
        # objHolder.addChild(QtGui.QTreeWidgetItem(QtCore.QString("test"), QtCore.QString("test")))
        # self.tree_geometry.currentItem().addChild("test1", "test2")

    def saveas(self):
        outFile = open('pickleTest.txt', 'wb')
#        currState = QtGui.QMainWindow.saveState()
        settings = QtCore.QSettings('myorg', 'myapp')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        vars = [self.contactParams, self.currentMaterialType,
                self.currentMeshType, self.fileName, self.gmt,
                self.insertionList, self.meshProperties, self.meshTypeData,
                self.origPath, self.stlFilesLoaded,
                self.totalTypes]
        pickle.dump(vars, outFile)

    def saveMaterialData(self):
        if not self.loading:
#            curval = self.gmt[self.spnbox_casesetup_materialproperties_materialtype.value()-1]
            curval = self.gmt[self.combo_conty.currentIndex()]
            curval[0] = self.line_youngsmodulus.text()
            curval[1] = self.spnbox_poissonsratio.value()

    def savemeshproperties(self):
        if not self.loading:
            # TODO: Save contact type
            # self.currentMeshType = basename(root.fileName) | item.text(0)
            n = self.currentMeshType
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

            # TODO: save tree definitions

    def savePSD(self):
#        print str(self.spnbox_insertion_fraction.value())
        if self.spnbox_psd.value() is not 0 and self.loading is not True:
            self.insertionList[self.spnbox_insertionindex.value()-1][0][
                    self.spnbox_psd.value()-1][
                            self.spnbox_granulartypeindex.value()-1][
                            self.combo_particlelist.currentIndex()] = \
                                [str(self.combo_particlelist.currentText()),
                                    self.spnbox_insertion_fraction.value(),
                                    self.spnbox_density.value(),
                                    self.spnbox_diameter.value()]
            adding = 0
            for n in range(0, len(self.insertionList[self.spnbox_insertionindex.value()-1
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1])):
                adding += self.insertionList[self.spnbox_insertionindex.value()-1
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1][n][1]
            self.lbl_PSDFractionTotal.setText(str(adding))

    def terminal(self):

        # print()
        # os.startfile('/usr/bin/gnome-terminal')
        # subprocess.Popen(['exo-open --launch TerminalEmulator'], shell=True)

        subprocess.Popen(['gnome-terminal'], shell=True)

        # subprocess.call(['exo-open --launch TerminalEmulator'], shell=True)
        # si = subprocess.STARTUPINFO()
        # si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        # os.system("gnome-terminal -e 'sudo apt-get update'")
        # proc = si.Popen(['/bin/bash'], shell=True)
        # proc.wShowWindow();
        # subprocess.Popen(["xdg-open", 'gnome-terminal'])
        # subprocess.Popen(['gnome-terminal'], shell=True)
        # os.popen('gnome-terminal')

    def tree_remove(self, item):
        global mesh_ref
        # mesh_ref
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

    def treeclick(self):
        self.stackTest.setCurrentIndex(self.treeTest.indexFromItem(
                self.treeTest.currentItem()).row())

    def treegeometry(self):
        if self.tree_geometry.currentItem().parent() is None:
            self.stack_geometry.setCurrentIndex(
                    self.tree_geometry.indexFromItem(
                            self.tree_geometry.currentItem()).row())
#            print 'no parent, has index: ' \
#                + str(self.tree_geometry.indexFromItem(
#                        self.tree_geometry.currentItem()).row())
        else:
            (self.stack_geometry.setCurrentIndex(
                     self.tree_geometry.indexFromItem(
                             self.tree_geometry.currentItem().parent()).row()))
#            print 'has parent at index: ' \
#                + str(self.tree_geometry.indexFromItem(
#                                self.tree_geometry.
#                                currentItem().parent()).row()) \
#                + ', has index: ' \
#                + str(self.tree_geometry.indexFromItem(
#                        self.tree_geometry.currentItem()).row())

    def treesolve(self):
        self.stack_solve.setCurrentIndex(
                self.tree_solve.indexFromItem(
                        self.tree_solve.currentItem()).row())

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
                    self.insertionList[self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1])):
                self.combo_particlelist.addItem(
                        self.insertionList[
                                self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            n][0])
            adding = 0
            for n in range(0, len(self.insertionList[self.spnbox_insertionindex.value()-1
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1])):
                adding += self.insertionList[self.spnbox_insertionindex.value()-1
                              ][0][self.spnbox_psd.value()-1][
                                      self.spnbox_granulartypeindex.value()-1][n][1]
            self.lbl_PSDFractionTotal.setText(str(adding))
            self.loading = False
            self.updateparticletype()

    def updateparticletype(self):
        if not self.loading:
            self.loading = True
            self.spnbox_insertion_fraction.setValue(
                    self.insertionList[
                                self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][1])
            self.spnbox_density.setValue(
                    self.insertionList[
                                self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][2])
            self.spnbox_diameter.setValue(
                    self.insertionList[
                                self.spnbox_insertionindex.value()-1][
                            0][self.spnbox_psd.value()-1][
                                    self.spnbox_granulartypeindex.value()-1][
                                            self.combo_particlelist.currentIndex()][3])
            self.loading = False

    def updateparticletypelist(self):
        if not self.loading:
            self.loading = True
            if self.spnbox_psd.value() > len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][0]):
                self.spnbox_psd.setValue(len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][0]))
            if self.spnbox_psd.value() == 0 and len(self.insertionList[
                    self.spnbox_insertionindex.value()-1][0]) > 0:
                    self.spnbox_psd.setValue(1)
            if self.spnbox_granulartypeindex.value() == 0:
                self.spnbox_granulartypeindex.setValue(1)

            self.loading = False
            self.updateparticlelist()

#        if self.spnbox_psd.value() > len(self.insertionList[
#                self.spnbox_insertionindex.value()-1][0]):
#            self.spnbox_psd.setValue(len(self.insertionList[
#                self.spnbox_insertionindex.value()-1][0]))
#            return -1
#        self.loading = True
#        if len(self.insertionList[
#                self.spnbox_insertionindex.value()-1][0]) > 0:
#            self.spnbox_insertion_fraction.setValue(self.insertionList[
#                    self.spnbox_insertionindex.value()-1][0][
#                            self.spnbox_psd.value()-1][1])
#        else:
#            self.spnbox_insertion_fraction.setValue(0.00)
#        self.combo_insertion_particleTypeList.clear()
#        if self.spnbox_psd.value() is not 0:
#            currParticles = []
#            tempIndex = self.spnbox_insertionindex.value() - 1
#            self.spnbox_insertion_fraction.setValue(
#                    self.insertionList[tempIndex][0][
#                            self.spnbox_psd.value()-1][1])
#            for var in self.insertionList[tempIndex][0]:
#                if var[0] is not '':
#                    currParticles.append(var[0])
#            for x in range(0, self.spnbox_geometry_contacttypes_totalgranulartypes.value()):
#                for y in range(x, self.totalTypes):
#                    tempStr = str(x+1)+'_'+str(y+1)
#                    # print self.insertionList
#                    if tempStr not in currParticles:
#                        self.combo_insertion_particleTypeList.addItem(tempStr)
#                    elif tempStr == self.insertionList[tempIndex][0][self.spnbox_psd.value()-1][0]:
#                        self.combo_insertion_particleTypeList.addItem(tempStr)
##                        self.spnbox_insertion_fraction.setValue(self.insertionList[tempIndex][0][self.spnbox_psd.value()-1][1])
#            self.combo_insertion_particleTypeList.setCurrentIndex(
#                self.combo_insertion_particleTypeList.findText(
#                        self.insertionList[tempIndex][0][
#                                self.spnbox_psd.value()-1][0]))
#            self.loading = False
#        elif len(self.insertionList[
#                self.spnbox_insertionindex.value()-1][0]) > 0:
#            self.spnbox_psd.setValue(1)

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

        self.cameraLookAt = [0.1,0.1,0.1,0.,0.,0.,0.,1.,0]

        self.scale = [.25, .25, .25]

        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
        self.trolltechBlack = QtGui.QColor.fromCmykF(1.0, 1.0, 1.0, 0.0)
        self.trolltechYellow = QtGui.QColor.fromCmykF(.00, .02, .20, .0)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        print angle
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        print angle
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
#        print angle
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.updateGL()

    def initializeGL(self):
#        self.qglClearColor(self.trolltechPurple.dark())
        self.qglClearColor(self.trolltechBlack)
        self.object = self.makeObject()
#        GL.glShadeModel(GL.GL_FLAT)
        GL.glEnable(GL.GL_DEPTH_TEST)
#        GL.glEnable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_CULL_FACE)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslated(0., 0., -10.0)
        print self.zRot
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
#        height = OpenGL.GLUT.glutGet(OpenGL.GLUT.GLUT_WINDOWS_HEIGHT)
#        GL.glBegin(GL.GL_QUADS);
#        GL.glColor3f( 1.0, 0.0, 0.0 );
#        GL.glVertex3f( 0.0, 0.0, 0.0 );
#        GL.glVertex3f( GL.ofGetWidth(), 0.0, 0.0 );
#        GL.glColor3f( 0.0, 0.0, 1.0 );
#        GL.glVertex3f( GL.ofGetWidth(), GL.ofGetHeight(), 0.0 );
#        GL.glVertex3f( 0.0, GL.ofGetHeight(), 0.0 );
#        GL.glEnd();

#        GL.glDisable(GL.GL_CLIP_PLANE0)
#        GL.glDisable(GL.GL_CLIP_PLANE1)
#        GL.glDisable(GL.GL_CLIP_PLANE2)
#        GL.glDisable(GL.GL_CLIP_PLANE3)
#        GL.glDisable(GL.GL_CLIP_PLANE4)
#        GL.glDisable(GL.GL_CLIP_PLANE5)
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
            # TODO: Add a condition for xRot and yRot
            print (self.xRot%2880)/2880.0
            print ((dx*((self.xRot%2880)/2880.0))*720)
#            factor = -5.
#            if self.xRot <= 2880:
#                if self.xRot%2880 <= 1440:
#                    self.setXRotation(self.xRot + 8.0 * dy + ((dx*((self.xRot%2880.0)/1440))*factor))   
#                else:
#                    self.setXRotation(self.xRot + 8.0 * dy + ((dx*((2880-(self.xRot%2880.0))/1440))*factor))
#            else:
#                if self.xRot%2880 <= 1440:
#                    self.setXRotation(self.xRot + 8.0 * dy - ((dx*((self.xRot%2880.0)/1440))*factor))   
#                else:
#                    self.setXRotation(self.xRot + 8.0 * dy - ((dx*((2880-(self.xRot%2880.0))/1440))*factor))
            self.setXRotation(self.xRot + 8.0 * dy)
            self.setYRotation(self.yRot + 8.0 * dx)
#            print str(self.xRot) + ' - xRot'
#            print str(self.yRot) + ' - yRot'
#            print str(dx) + ' - dx'
#            print str(dy) + ' - dy'
#            self.setZRotation()
#            self.setZRotation(self.zRot/(self.xRot+self.yRot))
#            self.cameraLookAt = [self.cameraLookAt[0] + dx/1000.0,  # ???
#                                 self.cameraLookAt[1] + dy/1000.0,  # ???
#                                 self.cameraLookAt[2],  # ???
#                                 self.cameraLookAt[3],  # move X
#                                 self.cameraLookAt[4],  # move Y
#                                 self.cameraLookAt[5],  # move Z (-(x/2 + y/2))
#                                 self.cameraLookAt[6],  # facing v[0] (x) DEF: 0
#                                 self.cameraLookAt[7],  # facing v[1] (y) DEF: 1
#                                 self.cameraLookAt[8]]  # facing v[2] (z) DEF: 0
#            self.updateGL()
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
#            self.cameraLookAt = [self.cameraLookAt[0] + dx/1000.0,  # ???
#                                 self.cameraLookAt[1] + dy/1000.0,  # ???
#                                 self.cameraLookAt[2],  # ???
#                                 self.cameraLookAt[3] + dx/1000.0,  # move X
#                                 self.cameraLookAt[4] + dy/1000.0,  # move Y
#                                 self.cameraLookAt[5],  # move Z (-(x/2 + y/2))
#                                 self.cameraLookAt[6],  # facing v[0] (x) DEF: 0
#                                 self.cameraLookAt[7],  # facing v[1] (y) DEF: 1
#                                 self.cameraLookAt[8]]  # facing v[2] (z) DEF: 0
            self.updateGL()
#            self.setXRotation(self.xRot + 8 * dy)
#            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeObject(self):

        global mesh_ref

        if len(mesh_ref) > 0:
            
            genList = GL.glGenLists(1)
            GL.glNewList(genList, GL.GL_COMPILE)

    #        GL.glMatrixMode(GL.GL_MODELVIEW)
    #        GL.glLoadIdentity()

    #        LightAmbient = [0.,0.,0.,1.5]
    #        LightAmbient = [0.,0.,0.,1.5]
            LightAmbient = [0.,0.,0.,.1]
            LightDiffuse = [5.,5.,5.,1.]
            LightPosition = [0.,1.,1.,0.]

            LightAmbient2 = [0.,0.,0.,.1]
            LightDiffuse2 = [2.,2.,2.,1.]
            LightPosition2 = [0.,-1.,-1.,0.]

    #        GL.glEnable(GL.GL_CULL_FACE)
            GL.glEnable(GL.GL_LIGHTING)
            GL.glEnable(GL.GL_LIGHT0)
            GL.glEnable(GL.GL_LIGHT1)

            GL.glLightfv( GL.GL_LIGHT0, GL.GL_AMBIENT, LightAmbient2)
            GL.glLightfv( GL.GL_LIGHT0, GL.GL_DIFFUSE, LightDiffuse2 )
            GL.glLightfv( GL.GL_LIGHT0, GL.GL_POSITION, LightPosition2 )

            GL.glLightfv( GL.GL_LIGHT1, GL.GL_AMBIENT, LightAmbient)
            GL.glLightfv( GL.GL_LIGHT1, GL.GL_DIFFUSE, LightDiffuse )
            GL.glLightfv( GL.GL_LIGHT1, GL.GL_POSITION, LightPosition )

#            GL.glEnable( GL.GL_LIGHTING )
            
            GL.glColorMaterial(GL.GL_FRONT, GL.GL_DIFFUSE)
            GL.glEnable(GL.GL_COLOR_MATERIAL)
            
    #        GL.glEnable(GL.GL_RESCALE_NORMAL)
    #        GL.glEnable(GL.GL_AUTO_NORMAL)

    #        GL.glLightModelf(GL.GL_LIGHT_MODEL_LOCAL_VIEWER, 0.5)
#            GL.glShadeModel(GL.GL_SMOOTH)
    #        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
    #        GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE)
    #        GL.glEnable(GL.GL_LIGHT_MODEL_AMBIENT)
    #        self.define_shader()
    #        test = GL.glCreateProgram()
    #        GL.glProgramParameteri
    #        GL.glUseProgram()
    #        GL.glEnable(GL.GL_DEPTH_TEST)
    #        GL.glEnable(shaders.vertex_shader)
    #        lightpos = (.5, 1., 1., 0.)
    #        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, lightpos)

    #        GL.glBegin(GL.GL_QUADS)
            GL.glBegin(GL.GL_TRIANGLES)

#            self.qglColor(self.trolltechGreen)
#            print mesh_ref
#            GL.glColor3f(.4, .0, 1.)
            for meshes in range(0, len(mesh_ref)):
                GL.glColor4f(mesh_ref[meshes][2][0],
                             mesh_ref[meshes][2][1],
                             mesh_ref[meshes][2][2],
                             mesh_ref[meshes][2][3])
                for index in range(0, len(mesh_ref[meshes][1])):
                    GL.glNormal3d(mesh_ref[meshes][1].normals[index][0],
                                  mesh_ref[meshes][1].normals[index][1],
                                  mesh_ref[meshes][1].normals[index][2])
                    GL.glVertex3d(mesh_ref[meshes][1].points[index][0],
                                  mesh_ref[meshes][1].points[index][1],
                                  mesh_ref[meshes][1].points[index][2])
                    GL.glVertex3d(mesh_ref[meshes][1].points[index][3],
                                  mesh_ref[meshes][1].points[index][4],
                                  mesh_ref[meshes][1].points[index][5])
                    GL.glVertex3d(mesh_ref[meshes][1].points[index][6],
                                  mesh_ref[meshes][1].points[index][7],
                                  mesh_ref[meshes][1].points[index][8])

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
#        self.cameraLookAt = [3.,3.,3.,0.,0.,0.,0.,1.,0]
        self.scale = [self.scale[0]*1.1,self.scale[1]*1.1,self.scale[2]*1.1]
        self.updateGL()
        #gluLookAt(3.,3.,3.,0.,0.,0.,0.,1.,0)

    def zoomout(self):
#        self.cameraLookAt = [self.cameraLookAt[0],  # ???
#                             self.cameraLookAt[1],  # ???
#                             self.cameraLookAt[2],  # ???
#                             self.cameraLookAt[3] - .2,  # move X
#                             self.cameraLookAt[4] - .2,  # move Y
#                             self.cameraLookAt[5] - .2,  # move Z (-(x/2 + y/2))
#                             self.cameraLookAt[6],  # facing v[0] (x) DEF: 0
#                             self.cameraLookAt[7],  # facing v[1] (y) DEF: 1
#                             self.cameraLookAt[8]]  # facing v[2] (z) DEF: 0
        self.scale = [self.scale[0]/1.1,self.scale[1]/1.1,self.scale[2]/1.1]
        self.updateGL()

#class GLWidget(QtOpenGL.QGLWidget):
#    xRotationChanged = QtCore.pyqtSignal(int)
#    yRotationChanged = QtCore.pyqtSignal(int)
#    zRotationChanged = QtCore.pyqtSignal(int)
#
#    def __init__(self, parent=None):
#        super(GLWidget, self).__init__(parent)
#
#        self.object = 0
#        self.xRot = 0
#        self.yRot = 0
#        self.zRot = 0
#
#        self.lastPos = QtCore.QPoint()
#
#        self.trolltechGreen = QtGui.QColor.fromCmykF(0.40, 0.0, 1.0, 0.0)
#        self.trolltechPurple = QtGui.QColor.fromCmykF(0.39, 0.39, 0.0, 0.0)
#
#    def minimumSizeHint(self):
#        return QtCore.QSize(50, 50)
#
#    def sizeHint(self):
#        return QtCore.QSize(400, 400)
#
#    def setXRotation(self, angle):
#        angle = self.normalizeAngle(angle)
#        print angle
#        if angle != self.xRot:
#            self.xRot = angle
#            self.xRotationChanged.emit(angle)
#            self.updateGL()
#
#    def setYRotation(self, angle):
#        angle = self.normalizeAngle(angle)
#        print angle
#        if angle != self.yRot:
#            self.yRot = angle
#            self.yRotationChanged.emit(angle)
#            self.updateGL()
#
#    def setZRotation(self, angle):
#        angle = self.normalizeAngle(angle)
#        print angle
#        if angle != self.zRot:
#            self.zRot = angle
#            self.zRotationChanged.emit(angle)
#            self.updateGL()
#
#    def initializeGL(self):
#        self.qglClearColor(self.trolltechPurple.dark())
#        self.object = self.makeObject()
#        GL.glShadeModel(GL.GL_FLAT)
#        GL.glEnable(GL.GL_DEPTH_TEST)
#        GL.glEnable(GL.GL_CULL_FACE)
#
#    def paintGL(self):
#        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
#        GL.glLoadIdentity()
#        GL.glTranslated(0.0, 0.0, -10.0)
#        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
#        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
#        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
#        GL.glCallList(self.object)
#
#    def resizeGL(self, width, height):
#        side = min(width, height)
#        if side < 0:
#            return
#
#        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
#
#        GL.glMatrixMode(GL.GL_PROJECTION)
#        GL.glLoadIdentity()
#        GL.glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#
#    def mousePressEvent(self, event):
#        self.lastPos = event.pos()
#
#    def mouseMoveEvent(self, event):
#        dx = event.x() - self.lastPos.x()
#        dy = 0 - (event.y() - self.lastPos.y())
#
#        if event.buttons() & QtCore.Qt.LeftButton:
#            self.setXRotation(self.xRot + 8 * dy)
#            self.setYRotation(self.yRot + 8 * dx)
#        elif event.buttons() & QtCore.Qt.RightButton:
#            self.setXRotation(self.xRot + 8 * dy)
#            self.setZRotation(self.zRot + 8 * dx)
#
#        self.lastPos = event.pos()
#
#    def makeObject(self):
#        genList = GL.glGenLists(1)
#        GL.glNewList(genList, GL.GL_COMPILE)
#
#        GL.glBegin(GL.GL_QUADS)
#
#
#        x1 = +0.06
#        y1 = -0.14
#        x2 = +0.14
#        y2 = -0.06
#        x3 = +0.08
#        y3 = +0.00
#        x4 = +0.30
#        y4 = +0.22
#
#        self.quad(x1, y1, x2, y2, y2, x2, y1, x1)
#        self.quad(x3, y3, x4, y4, y4, x4, y3, x3)
#
#        self.extrude(x1, y1, x2, y2)
#        self.extrude(x2, y2, y2, x2)
#        self.extrude(y2, x2, y1, x1)
#        self.extrude(y1, x1, x1, y1)
#        self.extrude(x3, y3, x4, y4)
#        self.extrude(x4, y4, y4, x4)
#        self.extrude(y4, x4, y3, x3)
#
#        NumSectors = 200
#
#        for i in range(NumSectors):
#            angle1 = (i * 2 * math.pi) / NumSectors
#            val1 = 0.3
#            val2 = 0.2
#            x5 = val1 * math.sin(angle1)
#            y5 = val1 * math.cos(angle1)
#            x6 = val2 * math.sin(angle1)
#            y6 = val2 * math.cos(angle1)
#
#            angle2 = ((i + 1) * 2 * math.pi) / NumSectors
#            x7 = val2 * math.sin(angle2)
#            y7 = val2 * math.cos(angle2)
#            x8 = val1 * math.sin(angle2)
#            y8 = val1 * math.cos(angle2)
#
#            self.quad(x5, y5, x6, y6, x7, y7, x8, y8)
#
#            self.extrude(x6, y6, x7, y7)
#            self.extrude(x8, y8, x5, y5)
#
#        GL.glEnd()
#        GL.glEndList()
#
#        return genList
#
#    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
#        self.qglColor(self.trolltechGreen)
#
#        GL.glVertex3d(x1, y1, -0.05)
#        GL.glVertex3d(x2, y2, -0.05)
#        GL.glVertex3d(x3, y3, -0.05)
#        GL.glVertex3d(x4, y4, -0.05)
#
#        GL.glVertex3d(x4, y4, +0.05)
#        GL.glVertex3d(x3, y3, +0.05)
#        GL.glVertex3d(x2, y2, +0.05)
#        GL.glVertex3d(x1, y1, +0.05)
#
#    def extrude(self, x1, y1, x2, y2):
#        self.qglColor(self.trolltechGreen.dark(250 + int(100 * x1)))
#
#        GL.glVertex3d(x1, y1, +0.05)
#        GL.glVertex3d(x2, y2, +0.05)
#        GL.glVertex3d(x2, y2, -0.05)
#        GL.glVertex3d(x1, y1, -0.05)
#
#    def normalizeAngle(self, angle):
#        while angle < 0:
#            angle += 360 * 16
#        while angle > 360 * 16:
#            angle -= 360 * 16
#        return angle

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = PyQtLink()
    window.show()
sys.exit(app.exec_())