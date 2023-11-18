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

        col = layout.column()
        
        # 输出目录文本框
        col.prop(scene, "batch_export_directory", text="Output Directory")
        
        # 检查输出目录是否为空
        if not scene.batch_export_directory:
            col.label(text="Please specify an output directory.", icon='ERROR')
        else:
            col.operator("export.batch_fbx", text="Batch Export Selected Objects")

def register():
    bpy.utils.register_class(BatchExportFBXOperator)
    bpy.utils.register_class(OBJECT_PT_BatchExportPanel)
    bpy.types.Scene.batch_export_directory = bpy.props.StringProperty(
        name="Output Directory",
        subtype='DIR_PATH'
    )

def unregister():
    bpy.utils.unregister_class(BatchExportFBXOperator)
    bpy.utils.unregister_class(OBJECT_PT_BatchExportPanel)
    del bpy.types.Scene.batch_export_directory

if __name__ == "__main__":
    register()
