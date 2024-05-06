import numpy as np
import SimpleITK as sitk
import pygalmesh

output_QCT_R_HR_trab = '/home/gianthk/Data/TacoSound/QCT/QCTFEMUR_1955L_new/QCTFEMUR_1955L/masks/QCTFEMUR_1955L_R_HR_trab.mhd'


# load binary image
data_3D_BW_trab = sitk.ReadImage(output_QCT_R_HR_trab, imageIO="MetaImageIO")

# min_facet_angle=20,  lloyd=True,
size_f = 2 # size factor
# mesh_trab = pygalmesh.generate_from_array(np.transpose(sitk.GetArrayFromImage(data_3D_BW_trab), [2, 1, 0]),
#                                           voxel_size=data_3D_BW_trab.GetSpacing(),
#                                           max_facet_distance=size_f*min(data_3D_BW_trab.GetSpacing()),
#                                           max_cell_circumradius=3*size_f*min(data_3D_BW_trab.GetSpacing())
#                                          )

mesh_trab = pygalmesh.generate_from_array(np.transpose(sitk.GetArrayFromImage(data_3D_BW_trab), [2, 1, 0]),
                                          voxel_size=data_3D_BW_trab.GetSpacing(),
                                          max_facet_distance=3.0,
                                          max_cell_circumradius=6.0
                                         )


# remove triangles
mesh_trab.remove_lower_dimensional_cells()

print(mesh_trab)

# add origin
mesh_trab.points = np.array(data_3D_BW_trab.GetOrigin()) + mesh_trab.points

# write output mesh
output_QCT_R_HR_mesh_trab = ('/home/gianthk/Data/TacoSound/QCT/QCTFEMUR_1955L_new/QCTFEMUR_1955L/masks/QCTFEMUR_1955L_R_HR_trab_mesh_max_facet3mm_max_cell_circ6mm.vtk')
mesh_trab.write(output_QCT_R_HR_mesh_trab)