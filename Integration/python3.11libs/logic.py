import os
import time
import subprocess

try:
    import hou
except ImportError as e:    
    print(f"Failed to import modules: {e}")         

class Logic:
    # for use with Qt interface
    def __init__(self):
        pass

    @staticmethod
    def command_from_job(job):
        '''Construct a command from a job'''
        if job.do_video:
            # expand path for ffmpeg
            return "ffmpeg -i {} -c:v libx264 -crf 23 -pix_fmt yuv420p -y {}".format(job.location, job.location + ".mp4")
        else:
            return "imgsave -a {}".format("$HIP/flip/test.$F4.jpg")        


    # def construct_outputpath(self, identifier, version, format):        
    #     return "$HIP/flip/test.$F4.jpg"
    

class ExportJob:
    '''Contains all the information necessary to create a filesequence or video'''
    def __init__(self, location, identifier, format=".jpg", do_video=False):
        self.location = location
        self.identifier = identifier
        self.format = format
        self.do_video = do_video
    

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
            if self.dryrun:
                print("Dryrun: ", command)
            else:
                subprocess.run(command, shell=True)    
            

    def add_current_sequence(self, convert_video=False):
        """Save the currently selected sequence to disk."""
        # When doing "Current", there is no way to query MPlay for seq name
        # we need a location to save the file, this should be from settings
        # job = ExportJob("imgsave -a {}".format(self.settings.get("output_path")), "$HIP/flip/test.$F4.jpg")
        job = ExportJob(self.settings.get("location"),
                        self.settings.get("identifier"),
                        self.settings.get("version"),
                        self.settings.get("format")
        )                                
        self.queue.append(job)   
        if convert_video:
            job_video = ExportJob(self.settings.get("location"),
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
    exporter.add_current_sequence(convert_video=False)
    exporter.execute()




    