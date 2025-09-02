# The purpose of this addon is to allow the user to display the Render Engine
# pulldown menu on the TopBar and other convenient places. In the spirit of
# progress and training muscle memory, I personally recommend choosing the
# Properties Panel Header.
#
# This addon includes snippets of Blender source code. The original Python
# source code is included in the Blender application install. Here is a link to
# the installer:
# https://download.blender.org/release/Blender2.93/
#
# VERSION HISTORY:
# RevH aka 2.93.1
# Added a fix to the preferences init function so that the addon would successfully load in Blender v4.4 and v4.5. However, be advised that the addon has not been fully updated. Technically, it's only fully compatible with v2.93.
# RevG aka 2.93
# This iteration adds Render Engine to the Outliner. Albeit, in a limited
# fashion. More than anything, this was a test to see if this location felt
# useful. After some evaluation, it felt unnecessary and it will probably be
# removed in a future version.
#
# RevF
# This iteration moves the open and close routines out of addon_prefs and into 
# addon_utils. It also moves the "update" functions for the checkboxes in the
# Addon Preferences panel. They've also moved to addon_utils.
#
# RevE
# The distinct things about this version are: addon_prefs function has "open"
# and "close" routines that are called in the register and unregister routines.
# Also, the draw routines override the originals as opposed to appending and
# prepending them. "append" and "prepend" were too limiting and they did not
# adequately facilitate the desired features.

import bpy
from bpy.types import Header, Menu, Panel, AddonPreferences


bl_info = {
    "name": "Bdog's Render Engine Selector",
    "author": "Bdog",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "TopBar, Properties Panel Header",
    "description": "Places Render Engine selector in places",
    "warning": "",
    "doc_url": "",
    #"support": 'OFFICIAL',
    "category": "Render",
}

#Globals
old_draw_right = None       #Old TopBar draw_right function
old_props_draw = None       #Old Properties header draw function
old_outliner_draw = None    #Old Outliner header draw function

#Initialization
old_draw_right = bpy.types.TOPBAR_HT_upper_bar.draw_right
old_props_draw = bpy.types.PROPERTIES_HT_header.draw
old_outliner_draw = bpy.types.OUTLINER_HT_header.draw
#-------------------------------------------------------------------------------


def new_draw_right(self, context):
    # If statusbar is hidden, still show messages at the top
    if not context.screen.show_statusbar:
        self.layout.template_reports_banner()
        self.layout.template_running_jobs()
    
    #Show Render Engine selector left of Scene and ViewLayer
    #++++++++++++++++++++
    lbl_render_engine = ""
    if bpy.context.preferences.addons[__name__].preferences.cbx_show_topbar_re_label == True:
        lbl_render_engine = "Render Engine"
    self.layout.prop(context.scene.render, "engine", text=lbl_render_engine)
    #++++++++++++++++++++

    # Active workspace view-layer is retrieved through window, not through workspace.
    self.layout.template_ID(context.window, "scene", new="scene.new",
                       unlink="scene.delete")

    row = self.layout.row(align=True)
    row.template_search(
        context.window, "view_layer",
        context.window.scene, "view_layers",
        new="scene.view_layer_add",
        unlink="scene.view_layer_remove")
#-------------------------------------------------------------------------------


def new_props_draw(self, context):
    ui_scale = context.preferences.system.ui_scale
    self.layout.template_header()
    self.layout.separator_spacer()

    # The following is an ugly attempt to make the search button center-align better visually.
    # A dummy icon is inserted that has to be scaled as the available width changes.
    content_size_est = 160 * ui_scale
    layout_scale = min(1, max(0, (context.region.width / content_size_est) - 1))
    if layout_scale > 0:
        row = self.layout.row()
        row.scale_x = layout_scale
        row.label(icon='BLANK1')

    #Show Render Engine selector instead of Search box
    #++++++++++++++++++++
    lbl_render_engine = ""
    if bpy.context.preferences.addons[__name__].preferences.cbx_show_properties_re_label == True:
        lbl_render_engine = "Render Engine"
    self.layout.prop(context.scene.render, "engine", text=lbl_render_engine)
    #++++++++++++++++++++

    self.layout.separator_spacer()
    self.layout.prop(context.space_data, "search_filter", icon='VIEWZOOM', text="")
    self.layout.separator_spacer()
    self.layout.popover(panel="PROPERTIES_PT_options", text="")
#-------------------------------------------------------------------------------


def new_outliner_draw(self, context):
    layout = self.layout

    space = context.space_data
    display_mode = space.display_mode
    scene = context.scene
    ks = context.scene.keying_sets.active

    layout.template_header()

    layout.prop(space, "display_mode", icon_only=True)

    if display_mode == 'DATA_API':
        OUTLINER_MT_editor_menus.draw_collapsible(context, layout)
    if display_mode == 'LIBRARY_OVERRIDES':
        layout.prop(space, "lib_override_view_mode", text="")

    layout.separator_spacer()
    #Show Render Engine selector instead of Search box
    #++++++++++++++++++++
    if display_mode == 'VIEW_LAYER':
        lbl_render_engine = ""
        if bpy.context.preferences.addons[__name__].preferences.cbx_show_outliner_re_label == True:
            lbl_render_engine = "Render Engine"
        self.layout.prop(context.scene.render, "engine", text=lbl_render_engine)
    else:
    #++++++++++++++++++++
        row = layout.row(align=True)
        row.prop(space, "filter_text", icon='VIEWZOOM', text="")
    
        layout.separator_spacer()

    if display_mode == 'SEQUENCE':
        row = layout.row(align=True)
        row.prop(space, "use_sync_select", icon='UV_SYNC_SELECT', text="")

    row = layout.row(align=True)
    if display_mode in {'SCENES', 'VIEW_LAYER', 'LIBRARY_OVERRIDES'}:
        row.popover(
            panel="OUTLINER_PT_filter",
            text="",
            icon='FILTER',
        )
    if display_mode == 'LIBRARY_OVERRIDES' and space.lib_override_view_mode == 'HIERARCHIES':
        # Don't add ID type filter for library overrides hierarchies mode. Point of it is to see a hierarchy that is
        # usually constructed out of different ID types.
        pass
    elif display_mode in {'LIBRARIES', 'LIBRARY_OVERRIDES', 'ORPHAN_DATA'}:
        row.prop(space, "use_filter_id_type", text="", icon='FILTER')
        sub = row.row(align=True)
        sub.active = space.use_filter_id_type
        sub.prop(space, "filter_id_type", text="", icon_only=True)

    if display_mode == 'VIEW_LAYER':
        layout.operator("outliner.collection_new", text="", icon='COLLECTION_NEW').nested = True

    elif display_mode == 'ORPHAN_DATA':
        layout.operator("outliner.orphans_purge", text="Purge")

    elif space.display_mode == 'DATA_API':
        layout.separator()

        row = layout.row(align=True)
        row.operator("outliner.keyingset_add_selected", icon='ADD', text="")
        row.operator("outliner.keyingset_remove_selected", icon='REMOVE', text="")

        if ks:
            row = layout.row()
            row.prop_search(scene.keying_sets, "active", scene, "keying_sets", text="")

            row = layout.row(align=True)
            row.operator("anim.keyframe_insert", text="", icon='KEY_HLT')
            row.operator("anim.keyframe_delete", text="", icon='KEY_DEHLT')
        else:
            row = layout.row()
            row.label(text="No Keying Set Active")

    #++++++++++++++++++++
    if display_mode == 'VIEW_LAYER':
        layout.separator_spacer()
        row = layout.row(align=True)
        row.prop(space, "filter_text", icon='VIEWZOOM', text="")
    #++++++++++++++++++++


#-------------------------------------------------------------------------------


class addon_utils():
    #Run this after addon_preferences is registered with Blender
    #This checks Blender UI preferences and updates UI accordingly
    def open():
        if bpy.context.preferences.addons[__name__].preferences.cbx_topbar_selector == True:
            bpy.types.TOPBAR_HT_upper_bar.draw_right = new_draw_right
        if bpy.context.preferences.addons[__name__].preferences.cbx_properties_selector == True:
            bpy.types.PROPERTIES_HT_header.draw = new_props_draw
        if bpy.context.preferences.addons[__name__].preferences.cbx_outliner_selector == True:
            bpy.types.OUTLINER_HT_header.draw = new_outliner_draw

    #Run this before addon_preferences is unregistered with Blender
    #This restores Blender UI to default state
    def close():
        if bpy.context.preferences.addons[__name__].preferences.cbx_topbar_selector == True:
            bpy.types.TOPBAR_HT_upper_bar.draw_right = old_draw_right
        if bpy.context.preferences.addons[__name__].preferences.cbx_properties_selector == True:
            bpy.types.PROPERTIES_HT_header.draw = old_props_draw
        if bpy.context.preferences.addons[__name__].preferences.cbx_outliner_selector == True:
            bpy.types.OUTLINER_HT_header.draw = old_outliner_draw
    
    def update_topbar(self, context):
        if bpy.context.preferences.addons[__name__].preferences.cbx_topbar_selector == True:
            bpy.types.TOPBAR_HT_upper_bar.draw_right = new_draw_right
        else:
            bpy.types.TOPBAR_HT_upper_bar.draw_right = old_draw_right
        
    def update_prop_header(self, context):
        if bpy.context.preferences.addons[__name__].preferences.cbx_properties_selector == True:
            bpy.types.PROPERTIES_HT_header.draw = new_props_draw
        else:
            bpy.types.PROPERTIES_HT_header.draw = old_props_draw
        
    def update_outliner_header(self, context):
        if bpy.context.preferences.addons[__name__].preferences.cbx_outliner_selector == True:
            bpy.types.OUTLINER_HT_header.draw = new_outliner_draw
        else:
            bpy.types.OUTLINER_HT_header.draw = old_outliner_draw
#-------------------------------------------------------------------------------


class addon_prefs(AddonPreferences):
    bl_idname = __name__
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('init')

    #Preferences Panel functions
    def draw(self, context):
        #Place the screen elements on the panel
        self.layout.label(text="Where do you want the Render Engine selector?")
        row = self.layout.row()
        row.prop(self, "cbx_topbar_selector")
        col = row.column()
        col.enabled = bpy.context.preferences.addons[__name__].preferences.cbx_topbar_selector
        col.prop(self, "cbx_show_topbar_re_label")
        row = self.layout.row()
        row.prop(self, "cbx_properties_selector")
        col = row.column()
        col.enabled = bpy.context.preferences.addons[__name__].preferences.cbx_properties_selector
        col.prop(self, "cbx_show_properties_re_label")
        row = self.layout.row()
        row.prop(self, "cbx_outliner_selector")
        col = row.column()
        col.enabled = bpy.context.preferences.addons[__name__].preferences.cbx_outliner_selector
        col.prop(self, "cbx_show_outliner_re_label")
        #Add a Toggle Console button for debugging
        row = self.layout.row()
        row.operator("wm.console_toggle", icon='CONSOLE')

    #Preferences Panel objects
    cbx_topbar_selector: bpy.props.BoolProperty(
        name="TopBar",
        default=True,
        description="Enable Render Engine selector on TopBar",
        #update=update_topbar
        update=addon_utils.update_topbar
    )
    
    cbx_properties_selector: bpy.props.BoolProperty(
        name="Properties Panel Header",
        default=False,
        description="Enable Render Engine selector on Properties Panel Header",
        update=addon_utils.update_prop_header
    )
    
    cbx_outliner_selector: bpy.props.BoolProperty(
        name="Outliner Panel Header",
        default=False,
        description="Enable Render Engine selector on Outliner Panel Header",
        update=addon_utils.update_outliner_header
    )
    
    cbx_show_topbar_re_label: bpy.props.BoolProperty(
        name="Show TopBar Label",
        default=True,
        description="Show TopBar Render Engine menu label",
    )
    
    cbx_show_properties_re_label: bpy.props.BoolProperty(
        name="Show Properties Label",
        default=True,
        description="Show Properties Render Engine menu label",
    )
    
    cbx_show_outliner_re_label: bpy.props.BoolProperty(
        name="Show Outliner Label",
        default=True,
        description="Show Outliner Render Engine menu label",
    )


def register():
    bpy.utils.register_class(addon_prefs)
    addon_utils.open()


def unregister():
    addon_utils.close()
    bpy.utils.unregister_class(addon_prefs)


if __name__ == "__main__":
    register()