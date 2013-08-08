#  bpyFoil.py
#  
#  Copyright 2013 Louay Cheikh <brotherlu@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

"""
bpyFoil is intended to import airfoil DAT files into blender and create
a surface with the points
"""

import bpy
import re, random
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, IntProperty

bl_info =   {   
            'name':'Blender Airfoil Importer',
            'category':'Object',
            'author':'Louay Cheikh',
            'version':(0,5),
            'blender':(2,67,0),
            'location':'Search Menu'
            }

# Object select Name
def SelectObj(ObjName):
    bpy.ops.object.select_all(action='SELECT')
    Obj = bpy.data.objects.get(ObjName)
    Obj.select = True
    bpy.context.scene.objects.active = Obj

# Object select Newest
def SelectNewestObj():
    obj = bpy.context.scene.objects[0]
    obj.select = True
    bpy.context.scene.objects.active = obj

def MakePolyLine(objname, curvename, cList):
    """
    Polyline Generator function generator from 
    http://blenderscripting.blogspot.ca/2011/05/blender-25-python-bezier-from-list-of.html
    """

    w=1 # weight
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')  
    curvedata.dimensions = '3D'  

    objectdata = bpy.data.objects.new(objname, curvedata)  
    objectdata.location = (0,0,0) #object origin  
    bpy.context.scene.objects.link(objectdata)  

    polyline = curvedata.splines.new('POLY')  
    polyline.points.add(len(cList)-1)  
    for num in range(len(cList)):  
        x, z = cList[num]  #unpack the each Num
        polyline.points[num].co = (x, 0, z, w)  #modify the coordinates of the points

# Airfoil Class

class AirFoil:
    def __init__(self,FoilName,Resolution=250):
        
        FF = open(FoilName,'r')
        data = FF.readlines()
        
        # Create the regexp for finding the data 
        r = re.compile('[.\S]*\.[0-9]*')
        # Get FoilName from the file
        self.FoilName = data[0].strip()
        # Create the coordintes from the regler exp
        FoilCoords = [r.findall(x) for x in data[1:]]
        # Convert the strings to Floats
        self.__RawPoints = [(float(x[0]),float(x[1])) for x in FoilCoords if len(x)==2 ]
        # Ensure the First point is not the Point Count that some DAT files include 
        if self.__RawPoints[0][0]>1: self.__RawPoints.remove(self.__RawPoints[0])
        
        self.__ProcPoints = []
        self.__upper = []
        self.__lower = []
        self.__procPointsCount = Resolution
    
    def __str__(self):
        return "Airfoil Process Object, Last Processed: %s" % (self.FoilName)

    def processFoil(self):
        """Process Airfoils to Generate Points for Multisection solids"""
        
        # Split airfoil in upper and lower portions
        self.__airfoilSplit()
        
        # Interpolate
        self.__hinterpolate()
        
    def __airfoilSplit(self):
        """Process to divide the foildata to upper and lower sections"""
        # Find the chord coordiantes
        trailing = min(self.__RawPoints,key=lambda x:x[0])
        leading = max(self.__RawPoints,key=lambda x:x[0])
        
        # Find chord coordinates index
        trailingloc = self.__RawPoints.index(trailing)
        leadingloc = self.__RawPoints.index(leading)
        splitloc = leadingloc if 0 < leadingloc < len(self.__RawPoints)-3 else trailingloc
        
        # Split the airfoil along chord
        self.__upper = self.__RawPoints[:splitloc+1]
        self.__lower = self.__RawPoints[splitloc+1:]
        
        # Ensure each section starts at (0,0)->(1,0)
        if self.__upper[0][0] > self.__upper[-1][0]:
            self.__upper.reverse()
        if self.__lower[0][0] > self.__lower[-1][0]:
            self.__lower.reverse()
        
        # Ensure that the foils are not reversed
        testpoint = random.randint(0,min([len(self.__upper),len(self.__lower)])-1)
        if self.__upper[testpoint][1] < self.__lower[testpoint][1]:
            self.__upper , self.__lower = self.__lower , self.__upper
        
    def __hinterpolate(self):
        """Process of interpolation using piecewise hermite curve interpolation"""
        
        # Temp. Data holders
        upperint = []
        lowerint = []
        
        # Leading edge interpolation to be order of magnitude higher
        leadfine = 10
        
        # Create points
        xpoints = list(map(lambda x:x/float(self.__procPointsCount),range(0,self.__procPointsCount+1)))
                
        # Calculate secants
        uppersec = [(self.__upper[i+1][1]-self.__upper[i][1])/(self.__upper[i+1][0]-self.__upper[i][0]) for i in range(len(self.__upper)-1)]
        lowersec = [(self.__lower[i+1][1]-self.__lower[i][1])/(self.__lower[i+1][0]-self.__lower[i][0]) for i in range(len(self.__lower)-1)]
        
        # Calculate tangents
        uppertan = [(uppersec[k-1]+uppersec[k])/2 for k in range(1,len(uppersec))]
        uppertan.insert(0,uppersec[0])
        uppertan.append(uppersec[-1])

        lowertan = [(lowersec[k-1]+lowersec[k])/2 for k in range(1,len(lowersec))]
        lowertan.insert(0,lowersec[0])
        lowertan.append(lowersec[-1])
        
        # Hermite blending functions
        p0 = lambda t: 2*t**3 - 3*t**2 + 1
        m0 = lambda t: t**3 - 2*t**2 + t
        p1 = lambda t: -2*t**3 + 3*t**2
        m1 = lambda t: t**3 - t**2
        
        for xp in xpoints:
            for i in range(len(self.__upper)):
                if self.__upper[i][0] == xp:
                    upperint.append(self.__upper[i])
            
            for i in range(len(self.__upper)-1):
                if self.__upper[i][0] < xp < self.__upper[i+1][0]:
                    h = self.__upper[i+1][0]-self.__upper[i][0]
                    t = (xp - self.__upper[i][0]) / h
                    solution = ( p0(t)*self.__upper[i][1] + h*m0(t)*uppertan[i] + p1(t)*self.__upper[i+1][1] + h*m1(t)*uppertan[i+1] )
                    upperint.append((xp,solution))

            for i in range(len(self.__lower)):
                if self.__lower[i][0] == xp:
                    lowerint.append(self.__lower[i])
            
            for i in range(len(self.__lower)-1):
                if self.__lower[i][0] < xp < self.__lower[i+1][0]:
                    h = self.__lower[i+1][0]-self.__lower[i][0]
                    t = (xp - self.__lower[i][0]) / h
                    solution = ( p0(t)*self.__lower[i][1] + h*m0(t)*lowertan[i] + p1(t)*self.__lower[i+1][1] + h*m1(t)*lowertan[i+1] )
                    lowerint.append((xp,solution))
        
        upperint.reverse()
        upperint.append((0,0))
        self.__ProcPoints = upperint + lowerint
                    
    def getRawPoints(self):
        """Return Raw Points"""
        return self.__RawPoints
    
    def getProcPoints(self):
        """Return Generated Points"""
        if self.__ProcPoints == []:
            print("Points were not Generated. Call method 'processFoil'.")
            return
        return self.__ProcPoints

# Operator Class

class bpyAirfoil(Operator):
    """ Addon to import airfoil Dat files """
    bl_idname = "object.bpyairfoil"
    bl_label = "Airfoil DAT File Importer"
    bl_options = {'REGISTER','UNDO'}

    FileName = StringProperty(name="Filename", subtype="FILE_PATH", default="/tmp\\", description="Dat file location")
    Interp = BoolProperty(name="Interpolate")
    InterResolution = IntProperty(name="Interpolation Resolution",default=100,min=10)
    Surface_choice = BoolProperty(name="Import as Surface")

    def execute(self, context):
        """ Import """
        try:
            f = AirFoil(self.FileName,self.InterResolution)
        except:
            return {'FINISHED'}

        if self.Interp:
            #Generate from Interpolated Data
            f.processFoil()
            MakePolyLine(f.FoilName,f.FoilName,f.getProcPoints())
        else:
            # Generate the Polyline from RawData
            MakePolyLine(f.FoilName,f.FoilName,f.getRawPoints())

        # Select Object
        SelectNewestObj()

        if self.Surface_choice:
            bpy.ops.object.convert(target='MESH',keep_original=False)
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action="SELECT")
            bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)
            bpy.ops.mesh.fill(use_beauty=True)
            bpy.ops.object.editmode_toggle()

        return {'FINISHED'}

def register():
    """ Register all Classes """
    bpy.utils.register_class(bpyAirfoil)

def unregister():
    """ Unregister all Classes """
    bpy.utils.unregister_class(bpyAirfoil)

if __name__ == "__main__":
    register()
