bl_info = {
    "name": "Timecode",
    "author": "Ray Mairlot",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "Timeline Header or Space> Set timecode",
    "description": "Allows viewing and setting the current frame via a timecode (HH:MM:SS:FF)",
    "category": "Animation"
    }
    


import bpy
from bpy.app.handlers import persistent



def containsLetters(itemList):

    letters = [item for item in itemList if item.isdigit() == False]
    
    return len(letters) > 0



def calculateTimecode():
        
    fps = bpy.context.scene.render.fps
    timecode = bpy.context.scene.timecode
    totalFrames = bpy.context.scene.frame_current
            
    hours = int((totalFrames / fps) / 3600)
    
    if hours >= 1:
        
        timecode.hours = str(hours).zfill(2)   
        totalFrames = totalFrames - ((hours * fps) * 3600)
        
    else:
        
        timecode.hours = "00"  
        
    minutes = int((totalFrames / fps) / 60)
    
    if minutes >= 1:
        
        timecode.minutes = str(minutes).zfill(2)
        totalFrames = totalFrames - ((minutes * fps) * 60)        
        
    else:
        
        timecode.minutes = "00"  
            
    seconds = int(totalFrames / fps)
    
    if seconds >= 1:
        
        timecode.seconds = str(seconds).zfill(2)
        totalFrames = totalFrames - (seconds * fps)        
        
    else:
        
        timecode.seconds = "00"   
        
    frames = totalFrames
    
    if frames >= 1:          
        timecode.frames = str(frames).zfill(2)
        
    else:
        
        timecode.frames = "00"  
        


def formatTimecode():
    
    timecode = bpy.context.scene.timecode
    
    timecode.hours = timecode.hours.zfill(2)
    timecode.minutes = timecode.minutes.zfill(2)
    timecode.seconds = timecode.seconds.zfill(2)
    timecode.frames = timecode.frames.zfill(2)
    
    fps = bpy.context.scene.render.fps
    
    maximumEndFrame = bpy.types.Scene.bl_rna.properties['frame_end'].hard_max
    
    maximumHours = int((maximumEndFrame / fps) / 3600)
    
    if int(timecode.hours) > maximumHours:
        
        timecode.hours = str(maximumHours)
        
    if int(timecode.minutes) > 59:
        
        timecode.minutes = str(59)
        
    if int(timecode.seconds) > 59:
        
        timecode.seconds = str(59)
        
    if int(timecode.frames) > fps:
        
        timecode.frames = str(fps - 1)                  



def setFrame(self, context):
                
    timecode = context.scene.timecode
                
    #Don't trigger this function again when values are being updated by this function or if letters have been entered
    if not timecode.updating:
        
        stringInputs = [timecode.hours, timecode.minutes, timecode.seconds, timecode.frames]
        
        if not containsLetters(stringInputs):
            
            fps = context.scene.render.fps
            hours = int(timecode.hours)
            minutes = int(timecode.minutes)
            seconds = int(timecode.seconds)
            frames = int(timecode.frames)
                
            currentFrame = (hours * fps * 3600) + (minutes * fps * 60) + (seconds * fps) + frames
            
            #Prevent infite loop by not triggering frame_change_post when setting the new frame
            #Also prevents infite loop by not re-triggering this function when performing 'zfill' on properties
            timecode.updating = True
            formatTimecode()            
            bpy.context.scene.frame_set(currentFrame)
            timecode.updating = False
            
        else:
            
            timecode.updating = True
            
            calculateTimecode()
                    
            timecode.updating = False
        


class TimecodeProperties(bpy.types.PropertyGroup):
    
    hours = bpy.props.StringProperty(name="Hours", description="Hours", default="00", update=setFrame)

    minutes = bpy.props.StringProperty(name="Minutes", description="Minutes", default="00", update=setFrame)
    
    seconds = bpy.props.StringProperty(name="Seconds", description="Seconds", default="00", update=setFrame)    

    frames = bpy.props.StringProperty(name="Frames", description="Frames", default="00", update=setFrame)
    
    updating = bpy.props.BoolProperty(name="Updating", default=False)   
        


class SetTimecodeOperator(bpy.types.Operator):
    bl_idname = "scene.set_timecode"
    bl_label = "Set timecode"


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        return {'FINISHED'}


    def draw(self, context):
        
        layout = self.layout
        row = layout.row(align=False)
        row.label("Timecode:")
        
        row = layout.row(align=True)
        row.prop(context.scene.timecode, "hours", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "minutes", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "seconds", text="")
        row.label("   :")
        row.prop(context.scene.timecode, "frames", text="")



@persistent
def timecodeUpdate(scene):
            
    #Prevent infinite loop by not re-triggering when the current frame is being set by 'setFrame'
    if not scene.timecode.updating:
                    
        calculateTimecode()

                    

#Only needed when manually running from text editor
#bpy.app.handlers.frame_change_post.clear()
#bpy.app.handlers.frame_change_post.append(timecodeUpdate)



def TimecodeMenu(self, context):
                
    layout = self.layout
    row = layout.row(align=False)
    row.label("Timecode:")
    row.scale_x = 0.8
    
    labelScale = 0.6
    propertyScale = 0.3
    
    row = layout.row(align=True)
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "hours", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "minutes", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "seconds", text="")
    column.scale_x = propertyScale
    
    column = row.column(align=True)
    column.label(":")
    column.scale_x = labelScale
    
    column = row.column(align=True)    
    column.prop(context.scene.timecode, "frames", text="")
    column.scale_x = propertyScale
    


def register():
    
    bpy.app.handlers.frame_change_post.append(timecodeUpdate)
    bpy.utils.register_class(SetTimecodeOperator)
    bpy.utils.register_class(TimecodeProperties)
    bpy.types.Scene.timecode = bpy.props.PointerProperty(type=TimecodeProperties)
    bpy.types.TIME_HT_header.append(TimecodeMenu) 



def unregister():
    
    bpy.app.handlers.frame_change_post.remove(timecodeUpdate)
    bpy.utils.unregister_class(SetTimecodeOperator)
    bpy.utils.unregister_class(TimecodeProperties)
    bpy.types.TIME_HT_header.remove(TimecodeMenu) 



if __name__ == "__main__":
    register()
