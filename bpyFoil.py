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
from bpy.props import StringProperty, IntProperty
from mathutils import Vector

bl_info = 	{	
			'name':'Blender Airfoil Importer',
			'category':'Object',
			'author':'Louay Cheikh',
			'version':(0,1),
			'blender':(2,65,0),
			'location':'Search Menu'
			}

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

def MakeSurface(objname,curvename,cList):
	pass

class bpyAirfoil(Operator):
	""" Addon to import airfoil Dat files """
	bl_idname = "object.bpyairfoil"
	bl_label = "Airfoil DAT File Importer"
	bl_options = {'REGISTER','UNDO'}
	
	FileName = StringProperty(name="Filename", subtype="FILE_PATH", default="/tmp\\", description="Dat file location")

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
		
		MakePolyLine(FoilName,FoilName,FoilPoints)
		
		return {'FINISHED'}

class bpyAirfoil_Panel(Panel):
	""" Addon Panel """
	bl_label = "Import Panel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOL_PROPS"
	
	def draw(self,context):
		self.layout.operator("object.bpyairfoil",text="Import")

def register():
	""" Register all Classes """
	bpy.utils.register_class(bpyAirfoil)
	bpy.utils.register_class(bpyAirfoil_Panel)

def unregister():
	""" Unregister all Classes """
	bpy.utils.unregister_class(bpyAirfoil)
	bpy.utils.unregister_class(bpyAirfoil_Panel)

if __name__ == "__main__":
	register()
