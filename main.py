import customtkinter as ctk 
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
from proglog import ProgressBarLogger
import logging
import re
from datetime import datetime

# set up the log file
logging.basicConfig(filename='app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# metod to rest UI part for the check of downloads
def reset_UI():
    """
    Resets the user interface to its initial state.

    This function sets the text of 'progress_label' to "0%", the value of 'progress_bar' to 0, 
    and the text of 'status_label' to an empty string. It also sets the text color of 'status_label' 
    to black and its background color to transparent.

    Args:
        None

    Returns:
        None
    """
    progress_label.configure(text="0%")
    progress_bar.set(0)
    status_label.configure(text="",text_color="black",fg_color="transparent")


# metod to update the progress bat
def update_progress_bar(fase,value,label,bar):
    """
    Updates the progress bar and label on a user interface.

    This function sets the text of the given label to the current phase and the percentage value. 
    It also sets the value of the progress bar according to the given value. Both the label and 
    the progress bar are then updated to reflect these changes.

    Args:
        fase (str): The current phase of the process.
        value (float): The current progress value (0-100).
        label (tkinter.Label): The label to update with the current phase and progress value.
        bar (tkinter.Progressbar): The progress bar to update with the current progress value.

    Returns:
        None
    """
    label.configure(text=fase+" "+str(int(value))+"%")
    label.update()
    
    bar.set((value)/100)
    bar.update()


#modify the moviepy progress bar to use UI bar
class MyBarLogger(ProgressBarLogger):
    """
    A custom logger that extends the ProgressBarLogger class.

    Methods
    -------
    callback(**changes)
        Logs the changes in parameters.
        
    bars_callback(bar, attr, value, old_value=None)
        Updates the progress bar based on the value of the attribute.
    """
    def callback(self, **changes):
        """
        Logs the changes in parameters.

        Parameters
        ----------
        **changes : dict
            A dictionary where each key-value pair represents a parameter and its new value.
        """
        for (parameter, value) in changes.items():
            logging.info(f"Parameter {parameter} is now {value}")

    def bars_callback(self, bar, attr, value, old_value=None):
        """
        Updates the progress bar based on the value of the attribute.

        Parameters
        ----------
        bar : str
            The name of the progress bar to update.
        attr : str
            The attribute of the progress bar to update.
        value : int or float
            The new value of the attribute.
        old_value : int or float, optional
            The old value of the attribute.
        """
        percentage = (value / self.bars[bar]['total']) * 100
        update_progress_bar("Convert {}".format(bar),percentage,progress_label,progress_bar)
    
    

def convert_to_mp4(url,resolution):
    """
    Downloads a YouTube video and audio, merges them, and saves the result as an MP4 file.

    This function creates a YouTube object, filters the video and audio streams, downloads them,
    creates video and audio clips, merges them, and saves the result as an MP4 file. It also handles
    errors and updates a status label with the download status or any errors that occur.

    Parameters
    ----------
    url : str
        The URL of the YouTube video to download.
    resolution : str
        The resolution of the video to download.

    Raises
    ------
    Exception
        If any error occurs during the download or file operations.
    """
    try:
        #create the Youtube object with funtion on_progress 
        yt= YouTube(url,on_progress_callback=on_progress)

        #filter the Video and the audio trace
        video_stream=yt.streams.filter(res=resolution,mime_type="video/mp4").first()
        audio_stream= yt.streams.filter(mime_type="audio/mp4").first()
        
        
        #download the video and the audio trace
        video_filename=video_stream.download(output_path="downloads",filename="video")
        audio_filename=audio_stream.download(output_path="downloads",filename="audio")
        
        #create the objects for video and audio clip
        video = VideoFileClip(video_filename)
        audio = AudioFileClip(audio_filename)

        final_clip = video.set_audio(audio)
        
        #create the logger option
        logger = MyBarLogger()
        # set up the progress bar to 0
        progress_bar.set(0)
      
        #make the title of the video safe
        safe_title = re.sub(r'[^\w\s]', '', yt.title)

        #download the video into a specific directory
        final_clip.write_videofile(os.path.join("downloads", "{}.mp4".format(safe_title)), logger=logger)
        
        #close and remove the trace
        video.close()
        audio.close()
        os.remove(video_filename)
        os.remove(audio_filename)
        
        logging.info("Downloaded File:{} - {}".format(datetime.now(),safe_title))
        # update the status label
        status_label.configure(text="Downloaded MP4 : {}".format(safe_title),text_color="white",fg_color="green")

    except Exception as e:
        logging.info("Error:{} - {}".format(datetime.now(),str(e)))
        status_label.configure(text="Error {}".format(str(e)),text_color="white",fg_color="red")

def convert_to_mp3(url):
    """
    Downloads a YouTube video's audio and saves it as an MP3 file.

    This function creates a YouTube object, filters the audio stream, downloads it,
    creates an audio clip, and saves it as an MP3 file. It also handles errors and
    updates a status label with the download status or any errors that occur.

    Parameters
    ----------
    url : str
        The URL of the YouTube video to download.

    Raises
    ------
    Exception
        If any error occurs during the download or file operations.
    """
    try:
        #create the Youtube object with funtion on_progress 
        yt= YouTube(url,on_progress_callback=on_progress)
        
        #filter the Video to take the audio trace
        audio_stream= yt.streams.filter(mime_type="audio/mp4").first()
        
        #download the audio trace
        audio_filename=audio_stream.download(output_path="downloads",filename="audio")
        
        #create the object audio
        audio = AudioFileClip(audio_filename)
        
        #create the logger option
        logger = MyBarLogger()
        # set up the progress bar to 0
        progress_bar.set(0)
        
        #make the title of the video safe
        safe_title = re.sub(r'[^\w\s]', '', yt.title)

        #download the video into a specific directory
        audio.write_audiofile(os.path.join("downloads", "{}.mp3".format(safe_title)), logger=logger)
        
        #close and remove the trace
        audio.close()
        os.remove(audio_filename)

        logging.info("Downloaded File:{} - {}".format(datetime.now(),safe_title))
        # update the status label
        status_label.configure(text="Downloaded MP3 : {}".format(safe_title),text_color="white",fg_color="green")
    
    except Exception as e:
        logging.info("Error:{} - {}".format(datetime.now(),str(e)))
        status_label.configure(text="Error {}".format(str(e)),text_color="white",fg_color="red")


def download_video():
    """
    Downloads a YouTube video and converts it to the requested format.

    This function resets the UI, gets the URL and file type from the user,
    makes the progress label, progress bar, and status label visible, and
    then checks if the URL is not blank. If the URL is not blank, it checks
    if the requested file type is MP4. If it is, it gets the resolution for
    the video and converts it to MP4. If the requested file type is not MP4,
    it converts the video to MP3. If the URL is blank, it logs an error and
    updates the status label with the error message.
    """
    #reset UI for every click 
    reset_UI()
    # get Url from textbox
    url = entry_url.get()
    # get type file from combobox
    type_file_requested= format_var.get()
    
    #make progress_label / progress_bar / status_label visible
    progress_label.pack(pady=(1,5))
    progress_bar.pack(pady=(1,5))
    status_label.pack(pady=(1,5))
    
    # if the url is not blank
    if not url == "":
        # check if the type file is MP4
        if type_file_requested=="MP4":
            # get the resolution for the video
            resolution = resolution_var.get()
            # convert to mp4
            convert_to_mp4(url,resolution)
        else:
            # convert to mp3
            convert_to_mp3(url)
    else:
        logging.info("Error:{} - {}".format(datetime.now(),"Blank textbox"))
        status_label.configure(text="Error {}".format("Blank textbox"),text_color="white",fg_color="red")

    
    

# metod to check the download
def on_progress(stream,chunk,bytes_remaning):
    """
    Updates the progress bar based on the number of bytes remaining.

    This function calculates the total size of the file, the number of bytes downloaded,
    and the percentage completed, and then updates the progress bar with these values.

    Parameters
    ----------
    stream : Stream
        The stream that is being downloaded.
    chunk : bytes
        The chunk of the stream that has just been downloaded.
    bytes_remaning : int
        The number of bytes remaining to be downloaded.
    """
    total_size=stream.filesize
    bytes_download= total_size-bytes_remaning
    percentage_completed = bytes_download/total_size * 100
    
    update_progress_bar("Download",percentage_completed,progress_label,progress_bar)


# create a root window
root=ctk.CTk()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# title of the window
root.title("YT Python")

# set min and max width and the height
root.geometry("720x480")
root.minsize(720,480)
root.maxsize(1080,720)

# create a frame to hold the content
content_frame = ctk.CTkFrame(root)
content_frame.pack(fill=ctk.BOTH,expand=True,padx=10,pady=10)

# create a label and the entry widget for the video url
url_label = ctk.CTkLabel(content_frame,text="Enter the Youtube url here : ")
entry_url= ctk.CTkEntry(content_frame,width=400,height=40)
url_label.pack(pady=(10,5))
entry_url.pack(pady=(1,5))

# create a label and combobox for file format selection
format_label = ctk.CTkLabel(content_frame,text="Select file format : ")
format_label.pack(pady=(10,5))
formats=["MP3","MP4"]
format_var=ctk.StringVar()
format_combobox=ctk.CTkComboBox(content_frame,values=formats,variable=format_var)
format_combobox.pack(pady=(1,5))
format_combobox.set("MP3")

# create a label for the combo box
combo_label = ctk.CTkLabel(content_frame,text="Resolution:")
# create a resolution combo box
resolution=["1080p","720p","360p","240p"]
resolution_var=ctk.StringVar()
resolution_combobox=ctk.CTkComboBox(content_frame,values=resolution,variable=resolution_var)
resolution_combobox.set("240p")

def update_visibility(*args):
    if format_var.get() == "MP4":
        combo_label.pack(pady=(10,5))
        resolution_combobox.pack(pady=(1,5))
    else:
        combo_label.pack_forget()
        resolution_combobox.pack_forget()

format_var.trace_add('write', update_visibility)
update_visibility()  # Call this right after creating the widgets

# create a download button
download_button=ctk.CTkButton(content_frame,text="Download",command=download_video)
download_button.pack(pady=(1,5))

# create a label and the progress bar to display the download progress
progress_label=ctk.CTkLabel(content_frame,text="0%")
progress_bar=ctk.CTkProgressBar(content_frame,width=400)
progress_bar.set(0)

# create the status label
status_label=ctk.CTkLabel(content_frame,text="")

# to start the app
root.mainloop()



