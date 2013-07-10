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
import re
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty
from mathutils import Vector

bl_info = 	{	
			'name':'Blender Airfoil Importer',
			'category':'Object',
			'author':'Louay Cheikh',
			'version':(0,4),
			'blender':(2,67,0),
			'location':'Search Menu'
			}

def SelectObj(ObjName):
	bpy.ops.object.select_all(action='SELECT')
	Obj = bpy.data.objects.get(ObjName)
	Obj.select = True
	bpy.context.scene.objects.active = Obj

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
		x, y, z = cList[num]  
		polyline.points[num].co = (x, y, z, w)

class bpyAirfoil(Operator):
	""" Addon to import airfoil Dat files """
	bl_idname = "object.bpyairfoil"
	bl_label = "Airfoil DAT File Importer"
	bl_options = {'REGISTER','UNDO'}

	FileName = StringProperty(name="Filename", subtype="FILE_PATH", default="/tmp\\", description="Dat file location")
	Mesh_choice = BoolProperty(name="Import as Mesh")
	Surface_choice = BoolProperty(name="Import as Surface")

	def execute(self, context):
		""" Import """
		try:
			f = open(self.FileName,'r')
		except:
			return {'FINISHED'}
		# Read the raw file
		data = f.readlines()
		# Extract the Airfoil Name
		FoilName = data[0]
		# Create the regexp for finding the data
		r = re.compile('[.\S]*\.[0-9]*')
		# Create the coordintes from the regler exp
		FoilCoords = [r.findall(x) for x in data[1:]]
		# Convert the strings to Floats
		FoilPoints = [(float(x[0]),0,float(x[1])) for x in FoilCoords if len(x)==2 ]
		# Ensure the First point is not the Point Count that some DAT files include 
		if FoilPoints[0][0]>1: FoilPoints.remove(FoilPoints[0])
		# Generate the Polyline
		MakePolyLine(FoilName,FoilName,FoilPoints)
		# Select Object
		SelectNewestObj()

		if self.Mesh_choice or self.Surface_choice:
			bpy.ops.object.convert(target='MESH',keep_original=False)

		if self.Surface_choice:
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
