import os
import time
import subprocess
from pathlib import Path
import logging
from pprint import pprint

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)



try:
    import hou
except ImportError as e:    
    LOG.error(f"Failed to import modules: {e}")         

class Logic:
    # for use with Qt interface
    def __init__(self):
        pass

    def expand_structure(self, full_structure, key):
        '''Recursively expand the prism structure'''
        print("key is", key)        
        pprint(full_structure)
        one_structure = full_structure.get(key)
        print("one_structure is", one_structure)
        value = one_structure.get("value")
        if one_structure.get("requires"): # if has requirements
            for subkey in one_structure.get("requires"):
                value.replace(f"@{subkey}@", self.expand_structure(full_structure, subkey))        
        return value        
    
    @staticmethod
    def get_entity_path(pcore, filepath=None, context=None) -> Path:
        '''
        Get the entity path from a file path or context
        filepath can be a scenefile or any existing file in the project
        so that we can derive a context from the filepath        
        '''
        # temp setup prism for IDE
        # import common
        # common.setup_imports() 
        # import PrismCore  
        # pcore = PrismCore.create(app="Standalone", prismArgs=["noUI"])
        #

        if not filepath and not context:
            raise ValueError("Either filepath or context must be provided")
        
        if filepath:
            file_context = pcore.getScenefileData(filepath)
            # file_context = file_context.copy()
            remove = ["scenefile", "comment", "extension", "locations",
                  "project_name", "version", "user", "username", "filename",
                  "department", "task",
                  ]
            for key in remove:
                if key in file_context:
                    del file_context[key]    
            context = file_context
            print("got context", context)
        
        if context:                
            # get the entity_path template
            structure = pcore.projects.getProjectStructure()
            if context.get("type") == "asset":
                key = "assets"
                # template = structure.get("assets")['value']
            elif context.get("type") == "shot":
                key = "shots"
                # template = structure.get("shots")['value']
            
            # combine template + context to get filepath
            # turns out all we need is structure key + context to get filepath            
            entity_path = pcore.projects.getResolvedProjectStructurePath(key, context=context)                       
            return Path(entity_path), context     

    @staticmethod
    def context_from_path(pcore, filepath):
        '''
        Get the context from a filepath
        Cleans up context for our playblasts
        '''      
        file_context = pcore.getScenefileData(filepath)
        
        # remove what we don't need, at least for playblasts
        # maybe this needs to be different if we use this function for other things
        remove = ["scenefile", "comment", "extension", "locations",
                "project_name", "version", "user", "username", "filename",
                "department", "task",
                ]
        for key in remove:
            if key in file_context:
                del file_context[key]    
        
        return file_context
        

    def get_prism_context(self, prismcore):
        '''Get the current context'''

        # temp setup prism
        import common
        common.setup_imports() 
        import PrismCore  
        pcore = PrismCore.create(app="Standalone", prismArgs=["noUI"])

        # hipPath = hou.hipFile.path()
        hipPath = r"e:\Projects\TOPHE\03_Production\Assets\Tophe\Scenefiles\rig\apex\apex_v0001.hiplc"
        hip_context = pcore.getScenefileData(hipPath)
        pprint(hip_context)

        context = hip_context.copy()
        
        remove = ["scenefile", "comment", "extension", "locations",
                  "project_name", "version", "user", "username",
                  ]
        # del context["scenefile"]
        # shot_scenefiles = structure.get("shotScenefiles")
        structure = pcore.projects.getProjectStructure()
        pprint(structure.keys())

        playblast_template = pcore.projects.getTemplatePath("playblasts")
        playblast_versions_template = pcore.projects.getTemplatePath("playblastVersions")
        if hip_context.get("type") == "asset":
            playblast_files_template = pcore.projects.getTemplatePath("playblastFilesAssets")
        else:
            playblast_files_template = pcore.projects.getTemplatePath("playblastFilesShots")

        # playblast_files_template = playblast_files_template.replace(
        #     "@playblastversion_path@", playblast_versions_template
        # )
        # playblast_files_template = playblast_files_template.replace(
        #     "@playblast_path@", playblast_template
        # )

        print(playblast_files_template)
        # return

        # playblast_template = structure.get("assetPlayblastFiles") # same as what we do
        # asset_scenefiles = structure.get("assetScenefiles").get('value')
        # playblast_template = pcore.projects.getTemplatePath(
        #     "playblastFilesShots"
        # )
        # print(playblast_template)                             
        # return
        pb_file = r"E:\Projects\TOPHE\03_Production\Assets\Tophe\Playblasts\apex\v0001\apex_v0001.0001.jpg"

        # template = "@task_path@/@task@_@version@@extension@"
        context = pcore.projects.extractKeysFromPath(pb_file,playblast_files_template)  
        print(context)             
              
        key = "playblastFilesShots"
        pcore.projects.getResolvedProjectStructurePath(key, context=context)
        pass
        

    @staticmethod
    def construct_outputpath(pcore, identifier, version, format, context):
        """
        identifier is name of the flipbook
        version is the version number

        location is equivalent to "Playblasts" structure
        @entity_path@/Playblasts/@identifier@ (remove the identifier part?)
        maybe location should just be @entity_path@

        example:
        S:\job\R318\03_Production\Shots\SQ100\sh_030\Playblasts\Effects\v0019\SQ100-sh_030_Effects_v0019.1001.jpg
        E:\Projects\TOPHE\03_Production\Assets\Tophe\Playblasts\apex\v0005\apex_v0005.0001.exr
        """        

        # check the required context keys exist
        required_keys = ["type", "project_path"]
        for key in required_keys:
            if key not in context:
                raise ValueError(f"Context is missing key: {key}")
        # location, context = Logic.get_entity_path(pcore, filepath=scenefile, context=None)
        
        identifier = identifier.replace(" ", "_")
        context['identifier'] = identifier
        context['version'] = version
        context['extension'] = format

        if context.get("type") == "asset":
            key = "playblastFilesAssets"
        elif context.get("type") == "shot":
            key = "playblastFilesShots"
        
        playblast_path = pcore.projects.getResolvedProjectStructurePath(
            key, context=context
        )   
        
        # replace @frame expression with houdini
        playblast_path = playblast_path.replace("@.(frame)@", ".$F4")
        
        output = Path(playblast_path).as_posix() # ensure forward slashes        
        # output = output.replace("$F4", "\$F4") # stop hscript from expanding
        return output

    @staticmethod
    def command_from_job(job):
        '''Construct a command from a job'''
        if job.type == "hscript":
            args = ""            
            if not job.frames: # no frames provided
                args += "-a" # do all frames
            else:
                args += "-f {} {}".format(job.frames[0], job.frames[1]) # do range of frames

            outputpath = job.outputpath #Logic.construct_outputpath(job.location, job.identifier, job.version, job.format)
            # must backslash $F to avoid hscript expansion
            outputpath = outputpath.replace(".$F4", ".\$F4") 
            return f"imgsave {args} {outputpath}"
        
        elif job.type == "ffmpeg":
            inputpath = str(job.inputpath)
            inputpath = inputpath.replace(".$F4", ".%04d") # replace $F4 with %04d
            # video options            
            framerate = job.framerate
            #int(hou.text.expandString("$FPS"))
            codec = "libaom-av1"
            constant_rate_factor = 30

            outputpath = job.outputpath            
            # -crf sets the constant rate factor, lower is better quality, range is 0-63 for AV1
            # -b:v 0 sets the bitrate to a variable rate, to achieve a constant quality
            # result string
            result = (
                f'ffmpeg -framerate {framerate} -i "{inputpath}" '
                f'-c:v {codec} -crf {constant_rate_factor} -b:v 0 "{outputpath}"'
                f"-progress pipe:1"
            )
            return result
        elif job.type == "del":
            if os.path.exists(job.inputpath):
                if os.path.isdir(job.inputpath):
                    subprocess.run(f"rm -r {job.inputpath}", shell=True)
                else:
                    os.remove(job.inputpath)
            return f"rm -r {job.inputpath}"


class Job:
    '''Contains all the information necessary to create a filesequence or video'''
    def __init__(self, inputpath="", outputpath="", frames=[], format="", framerate=24, type=""):        
        self.inputpath = inputpath
        self.outputpath = outputpath
        self.frames = frames
        self.format = format
        self.framerate = framerate
        self.type = type # must be ffmpeg, hscript, del

        # ensure format is valid, either video or image
        if type == "ffmpeg":
            pass 
            # check inputpath & outputpath is specified
        


class Exporter:
    '''
    Handles exporting image sequences from MPlay
    '''
    def __init__(self, settings: dict, logic: Logic, dryrun=False):
        self.settings = settings
        self.queue = []
        self.logic = logic
        self.dryrun = dryrun
    

    def execute(self):
        '''Run through the command queue'''
        for job in self.queue:
            command = self.logic.command_from_job(job)
            result = None
             
            LOG.debug(f"Command created from job: \n{command}")
            if self.dryrun:
                print("Dryrun: ", command)
            else:
                if job.type == "hscript":                    
                    result = hou.hscript(command)                
                else:
                    result = subprocess.run(command, shell=True)    # ffmpeg
                
            if not result:# if result unsuccessful
                LOG.error(f"Failed to execute command: {command}")
                return result
            

    def add_current_sequence(self, convert_video=False, keep_images=True):
        """Save the currently selected sequence to disk."""
        # When doing "Current", there is no way to query MPlay for seq name
        # we need a location to save the file, this should be from settings       
        #  
        output_sequence = self.logic.construct_outputpath(
            self.settings.get("identifier"),
            self.settings.get("version"),
            self.settings.get("image_format"),
        )

        write_seq_job = Job(outputpath=output_sequence, type="hscript")         
        self.queue.append(write_seq_job)   

        if convert_video:
            output_video = self.logic.construct_outputpath(
                self.settings.get("identifier"),
                self.settings.get("version"),
                self.settings.get("video_format"),
            )   
            job_video = Job(inputpath=output_sequence, outputpath=output_video, type="ffmpeg")            
            self.queue.append(job_video)     

            if not keep_images:
                del_images_job = Job(inputpath=output_sequence, type="del")
                self.queue.append(del_images_job)
              
    

if __name__ == "__main__":
    settings = {
        "location": "$HIP/flip/",
        "identifier": "identifier",
        "version": 1,
        "format": ".jpg"
    }


    # temp setup prism
    import common
    common.setup_imports() 
    import PrismCore  
    pcore = PrismCore.create(app="Standalone", prismArgs=["noUI"])
    ## 

    # logic = Logic()
    # logic.get_prism_context(None)
    
    
    # location = logic.get_entity_path(pcore, filepath=tmp_hip)

    # exporter = Exporter(settings, logic, dryrun=True)
    # # exporter.add_current_sequence(convert_video=False)
    
    # hipPath = hou.hipFile.path()
    tmp_hip =r"e:\Projects\TOPHE\03_Production\Assets\Tophe\Scenefiles\rig\apex\apex_v0001.hiplc"

    context = Logic.context_from_path(pcore, tmp_hip)

    output_sequence = Logic.construct_outputpath(
        pcore=pcore,
        identifier="my bacon",
        version="v0001",
        format=".jpg",      
        context=context,  
    )
    print(output_sequence)







