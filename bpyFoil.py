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
from bpy.types import Operator, Panel
from bpy.props import StringProperty, IntProperty
from mathutils import Vector

bl_info =   {	
			'name':'Blender Airfoil Importer',
			'category':'Object',
			'author':'Louay Cheikh',
			'version':(0,1),
			'blender':(2,65,0),
			'location':'View 3D > Add > Surface'
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

class bpyAirfoil(Operator):
	""" Addon to import airfoil Dat files """
	bl_idname = "object.bpyairfoil"
	bl_label = "Airfoil DAT File Importer"
	bl_options = {'REGISTER','UNDO'}
	
	FileName = StringProperty(name="Filename", subtype="FILE_PATH", default="/tmp\\", description="Dat file location")
	LineNumber = IntProperty(name="Line One", default=3, min=0, description="First Line of the Data Points")

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

		# Extract the datapoints and trim the ends of the file
		FoilPoints = [p.strip().split(' ') for p in data[self.LineNumber:]]

		# Convert the string points to floats
		FoilCoords = [Vector([float(p[0]),0,float(p[-1])]) for p in FoilPoints if p[0] or p[-1] != '']
		
		MakePolyLine(FoilName,FoilName,FoilCoords)
		
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
