import os
import time
import subprocess
from pathlib import Path
import logging

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

try:
    import hou
except ImportError as e:    
    print(f"Failed to import modules: {e}")         

class Logic:
    # for use with Qt interface
    def __init__(self):
        pass

    def get_prism_context(self):
        '''Get the current context'''
        return hou.text.expandString("$HIP")

    @staticmethod
    def construct_outputpath(location, identifier, version, format):
        """
        location is the base path GET THIS FROM PRISM?
        identifier is name of the flipbook
        version is the version number

        example:
        S:\job\R318\03_Production\Shots\SQ100\sh_030\Playblasts\Effects\v0019\SQ100-sh_030_Effects_v0019.1001.jpg
        """

        # REPLACE WITH PRISM METHOD

        identifier = identifier.replace(" ", "_")
        output = Path(location) / f"{identifier}/v{version:04d}/{identifier}_v{version:04d}.$F4{format}"
        output = output.as_posix()
        # output = output.replace("$F4", "\$F4") # stop hscript from expanding
        return output

    @staticmethod
    def command_from_job(job):
        '''Construct a command from a job'''
        if not job.do_video:
            args = ""
            # expand path for ffmpeg
            if not job.frames: # no frames provided
                args += "-a" # do all frames
            else:
                args += "-f {} {}".format(job.frames[0], job.frames[1]) # do range of frames

            outputpath = Logic.construct_outputpath(job.location, job.identifier, job.version, job.format)
            # must backslash $F to avoid hscript expansion
            outputpath = outputpath.replace(".$F4", ".\$F4") 
            return f"imgsave {args} {outputpath}"
        else:
            inputpath = Logic.construct_outputpath(
                job.location, job.identifier, job.version, job.format
            )
            # video options            
            framerate = int(hou.text.expandString("$FPS"))
            codec = "libaom-av1"
            constant_rate_factor = 30

            outputpath = Logic.construct_outputpath(
                job.location, job.identifier, job.version, ".webm"
            )            
            
            # -crf sets the constant rate factor, lower is better quality, range is 0-63 for AV1
            # -b:v 0 sets the bitrate to a variable rate, to achieve a constant quality
            # result string
            result = (
                f"ffmpeg -framerate {framerate} -i {inputpath} "
                f"-c:v {codec} -crf {constant_rate_factor} -b:v 0 {outputpath}"
            )
            return result


    
    

class Job:
    '''Contains all the information necessary to create a filesequence or video'''
    def __init__(self, location, identifier, version, frames=[], format=".jpg", do_video=False):
        self.location = location
        self.identifier = identifier
        self.version = version
        self.frames = frames
        self.format = format
        self.do_video = do_video
        self.type = "ffmpeg" if do_video else "hscript"


        
    

class Exporter:
    '''
    Handles exporting image sequences from MPlay
    '''
    def __init__(self, settings: dict, logic: Logic, dryrun=False):
        self.settings = settings
        self.queue = []
        self.logic = logic
        self.dryrun = dryrun

    def job_from_settings(self, settings):
        '''Create a job from settings'''
        return Job(
            settings.get("location"),
            settings.get("identifier"),
            settings.get("format")
        )

    def execute(self):
        '''Run through the command queue'''
        for job in self.queue:
            command = self.logic.command_from_job(job)
            LOG.debug(f"Command created from job: \n{command}")
            if self.dryrun:
                print("Dryrun: ", command)
            else:
                if job.type == "hscript":                    
                    result = hou.hscript(command)                
                else:
                    result = subprocess.run(command, shell=True)    # ffmpeg
                return result
            

    def add_current_sequence(self, convert_video=False):
        """Save the currently selected sequence to disk."""
        # When doing "Current", there is no way to query MPlay for seq name
        # we need a location to save the file, this should be from settings        
        job = Job(location=self.settings.get("location"),
                    identifier=self.settings.get("identifier"),
                    version=self.settings.get("version"),
                    format=self.settings.get("format"),
                    frames=self.settings.get("frames"),
                    do_video=False
        )                                
        self.queue.append(job)   
        if convert_video:
            job_video = Job(self.settings.get("location"),
                        self.settings.get("identifier"),
                        self.settings.get("version"),
                        self.settings.get("video_format"),
                        do_video=True
            )                 
            self.queue.append(job_video)       
    

if __name__ == "__main__":
    settings = {
        "location": "$HIP/flip/test.$F4.jpg",
        "identifier": "identifier",
        "version": 1,
        "format": ".jpg"
    }

    logic = Logic()
    exporter = Exporter(settings, logic, dryrun=True)
    # exporter.add_current_sequence(convert_video=False)
    test_job = Job(
        location="$HIP/flipbook/",
        identifier="my_identifier",
        frames=[],
        version=1,
        format=".jpg"
    )
    exporter.queue.append(test_job)
    exporter.execute()




    