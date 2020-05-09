#!/bin/env python3
import numpy as np
import pandas as pd
from collections import defaultdict, Counter

import vtk
# each color to specific square
from vtk.util.colors import red, orange, yellow
from vtk.util.colors import purple, blue, green
from vtk.util.colors import white, magenta, green_dark
from vtk.util.colors import grey, light_grey, pink

df = pd.read_csv("../data/fingerprinting.csv", index_col="Unnamed: 0")
f = df.Square.apply(lambda x: int(x[1:]))

func = defaultdict(list)
for i, val in zip(df[["Server-RSSI-1", "Server-RSSI-2", "Server-RSSI-3"]].to_numpy(), f):
    func[tuple(i)].append(val)

unique_func = dict()
for i, val in func.items():
    unique_func[i] = max(Counter(val).items(), key=lambda x: x[1])[0]

# create bins for space
# [-95; -20] - range, that RSSI can be measured
nx = ny = nz = 75
numPoints = nx * ny * nz

mn_x = df["Server-RSSI-1"].min()
mx_x = df["Server-RSSI-1"].max()
xs = np.linspace(-20, -95, nx)

mn_y = df["Server-RSSI-2"].min()
mx_y = df["Server-RSSI-2"].max()
ys = np.linspace(-20, -95, nx)

mn_z = df["Server-RSSI-3"].min()
mx_z = df["Server-RSSI-3"].max()
zs = np.linspace(-20, -95, nz)
zz, yy, xx = np.meshgrid(zs, ys, xs, indexing='ij')
xyz = np.zeros((numPoints, 3), np.float64)
xyz[:, 0] = xx.flat
xyz[:, 1] = yy.flat
xyz[:, 2] = zz.flat

# create the pipeline
coords = vtk.vtkDoubleArray()
pts = vtk.vtkPoints()
grid = vtk.vtkStructuredGrid()
items = vtk.vtkAppendPolyData()
mapper = vtk.vtkPolyDataMapper()
actor = vtk.vtkActor()
domainMapper = vtk.vtkDataSetMapper()
domainActor = vtk.vtkActor()


# colors
def get_color(r, g, b):
    clrs = vtk.vtkUnsignedCharArray()
    clrs.SetNumberOfComponents(3)
    clrs.SetName("Colors")
    clrs.SetNumberOfTuples(0)
    for i in range(1024):
        clrs.InsertNextTypedTuple((r, g, b))
    return clrs


colors = [[int(gr * 255) for gr in c] for c in
          [red, orange, yellow, purple, blue, green, white, magenta, green_dark, grey, light_grey, pink]]

# make each point a sphere with small radius
for i, val in unique_func.items():
    dotSource = vtk.vtkSphereSource()
    dotSource.SetThetaResolution(5)
    dotSource.SetPhiResolution(5)
    dotSource.SetRadius(0.3)
    dotSource.SetCenter(*i)

    sp = dotSource.GetOutput()
    dotSource.Update()
    sp.GetCellData().SetScalars(get_color(*colors[val]))

    items.AddInputConnection(dotSource.GetOutputPort())

# settings
domainMapper.SetScalarVisibility(0)
domainActor.GetProperty().SetOpacity(0.3)

# construct the grid
grid.SetDimensions(nx, ny, nz)
coords.SetNumberOfComponents(3)
coords.SetNumberOfTuples(numPoints)
coords.SetVoidArray(xyz, 3 * numPoints, 1)

# connect
pts.SetNumberOfPoints(numPoints)
pts.SetData(coords)
grid.SetPoints(pts)
mapper.SetInputConnection(items.GetOutputPort())
mapper.SetColorModeToDirectScalars()
actor.SetMapper(mapper)
domainMapper.SetInputData(grid)
domainActor.SetMapper(domainMapper)

# show
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.AddActor(domainActor)
ren.SetBackground(0.0, 0.0, 0.0)
ren.SetUseDepthPeeling(1)
ren.SetOcclusionRatio(0.1)
ren.SetMaximumNumberOfPeels(100)
renWin.SetSize(400, 300)
renWin.SetMultiSamples(0)
renWin.SetAlphaBitPlanes(1)
iren.Initialize()
renWin.Render()
iren.Start()
