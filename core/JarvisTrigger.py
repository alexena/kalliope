from stt.snowboy import snowboydecoder


class JarvisTrigger:
    """
    Class used to catch the trigger word before listening for an order to process
    """
    def __init__(self):
        # TODO update this to load the file from settings
        self.model = "stt/snowboy/resources/snowboy.umdl"
        # boolean used to stop the snowbow listening
        self.interrupted = False

    def interrupt_callback(self):
        """
        This function will be passed to snowboy to stop the main thread
        :return:
        """
        return self.interrupted

    def start(self):
        """
        Start the snowboy thread and wait for a Jarvis trigger word
        :return:
        """

        detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.5)

        # start snowboy loop
        # TODO change to callback, call a function that wait for an audio order
        detector.start(detected_callback=snowboydecoder.play_audio_file,
                       interrupt_check=self.interrupt_callback,
                       sleep_time=0.03)

        # we wait that a callback
        detector.terminate()

    def stop(self):
        """
        Stop the Snowboy main thread
        :return:
        """
        self.interrupted = True