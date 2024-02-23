import bpy
import os

bl_info = {
    "name": "Batch Export FBX",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Sidebar > Batch Export FBX",
    "description": "Batch export selected objects as FBX with object names",
    "category": "Import-Export"
}

class BatchExportFBXOperator(bpy.types.Operator):
    bl_idname = "export.batch_fbx"
    bl_label = "Batch Export FBX"
    bl_description = "Batch export selected objects as FBX with object names"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        selected_objects = bpy.context.selected_objects
        
        # 保存原始位置和原始父对象
        original_locations = {obj: obj.location.copy() for obj in selected_objects}
        original_parents = {obj: obj.parent for obj in selected_objects}
        
        for obj in selected_objects:
            # 将物体移动到世界原点
            bpy.context.view_layer.objects.active = obj
            obj.location = (0, 0, 0)
            
            # 取消其他物体的选择状态
            for other_obj in selected_objects:
                other_obj.select_set(False)
            
            # 选择当前物体并导出
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            fbx_path = os.path.join(scene.batch_export_directory, obj.name + ".fbx")
            bpy.ops.export_scene.fbx(filepath=fbx_path, use_selection=True, axis_forward='-Z', axis_up='Y')
            
            # 恢复原始位置和父对象
            obj.location = original_locations[obj]
            obj.parent = original_parents[obj]

        # 恢复所有物体的选择状态
        for obj in selected_objects:
            obj.select_set(True)

        # Add the current export directory to the previous directories list if it's not already there
        if scene.batch_export_directory not in scene.previous_export_directories:
            scene.previous_export_directories.add().name = scene.batch_export_directory

        self.report({'INFO'}, "Batch export complete")
        return {'FINISHED'}

class OBJECT_PT_BatchExportPanel(bpy.types.Panel):
    bl_label = "Batch Export"
    bl_idname = "OBJECT_PT_batch_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        row = layout.row(align=True)
 
        # 输出目录文本框
        row.prop(scene, "batch_export_directory", text="")
        
        # 下拉菜单用于选择以前的导出地址
        row.prop_menu_enum(scene, "previous_export_directory", text="", icon='DOWNARROW_HLT')
        
        # 打开文件夹的按钮
        row.operator("file.select_directory", text="", icon='FILE_FOLDER')
        
        # 检查输出目录是否为空
        if not scene.batch_export_directory:
            layout.label(text="Please specify an output directory.", icon='ERROR')
        else:
            layout.operator("export.batch_fbx", text="Batch Export Selected Objects")

 
def register():
    bpy.utils.register_class(BatchExportFBXOperator)
    bpy.utils.register_class(OBJECT_PT_BatchExportPanel)

    bpy.types.Scene.batch_export_directory = bpy.props.StringProperty(
        name="Output Directory",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.DirPathItem = bpy.props.StringProperty(
        name="Directory Path",
        description="A directory path",
        default="",
        maxlen=1024,
        subtype='DIR_PATH',
    )

    bpy.types.Scene.previous_export_directories = bpy.props.CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    bpy.types.Scene.previous_export_directory = bpy.props.EnumProperty(
        name="Previous Export Directory",
        items=lambda self, context: [(i.name, i.name, i.name) for i in context.scene.previous_export_directories],
        update=lambda self, context: setattr(context.scene, "batch_export_directory", self.previous_export_directory)
    )

def unregister():
    bpy.utils.unregister_class(BatchExportFBXOperator)
    bpy.utils.unregister_class(OBJECT_PT_BatchExportPanel)
    del bpy.types.Scene.batch_export_directory
    del bpy.types.Scene.DirPathItem
    del bpy.types.Scene.previous_export_directories
    del bpy.types.Scene.previous_export_directory

if __name__ == "__main__":
    register()
