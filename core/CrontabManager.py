from crontab import CronTab
from crontab import CronSlices

from core import Utils
from core.ConfigurationManager.BrainLoader import BrainLoader
from core.Models import Event
import logging

logging.basicConfig()
logger = logging.getLogger("kalliope")


class InvalidCrontabPeriod(Exception):
    pass

CRONTAB_COMMENT = "KALLIOPE"
KALLIOPE_ENTRY_POINT_SCRIPT = "kalliope.py"


class CrontabManager:

    def __init__(self, brain_file=None):
        self.my_user_cron = CronTab(user=True)
        self.brain = BrainLoader.get_brain(file_path=brain_file)
        self.base_command = self._get_base_command()

    def load_events_in_crontab(self):
        """
        Remove all line in crontab with the CRONTAB_COMMENT
        Then add back line from event in the brain.yml
        :return:
        """
        # clean the current crontab from all Kalliope event
        self._remove_all_job()
        # load the brain file
        for synapse in self.brain.synapses:
            for signal in synapse.signals:
                # print signal
                # if the signal is an event we add it to the crontab
                if type(signal) == Event:
                    # for all synapse with an event, we add the task id to the crontab
                    self._add_event(period_string=signal.period, event_id=synapse.name)

    def _add_event(self, period_string, event_id):
        my_user_cron = CronTab(user=True)
        job = my_user_cron.new(command=self.base_command+" "+str("\"" + event_id + "\""), comment=CRONTAB_COMMENT)
        if CronSlices.is_valid(period_string):
            job.setall(period_string)
            job.enable()
        else:
            raise InvalidCrontabPeriod("The crontab period %s is not valid" % period_string)
        # write the file
        my_user_cron.write()
        Utils.print_info("Synapse \"%s\" added to the crontab" % event_id)

    def get_jobs(self):
        return self.my_user_cron.find_comment(CRONTAB_COMMENT)

    def _remove_all_job(self):
        """
        Remove all line in crontab that are attached to Kalliope
        :return:
        """
        iter = self.my_user_cron.find_comment(CRONTAB_COMMENT)
        for job in iter:
            logger.debug("remove job %s from crontab" % job)
            self.my_user_cron.remove(job)
        # write the file
        self.my_user_cron.write()

        # this is a fix for the CronTab lib
        # see https://github.com/peak6/python-crontab/issues/1
        new_iter = self.my_user_cron.find_comment(CRONTAB_COMMENT)
        sum_job = sum(1 for _ in new_iter)
        while sum_job > 0:
            self._remove_all_job()

    def _get_base_command(self):
        """
        Return the path of the entry point of Kalliope
        Example: /home/user/kalliope/kalliope.py
        :return: The path of the entry point script kalliope.py
        """
        import inspect
        import os
        # get current script directory path. We are in /an/unknown/path/kalliope/core
        cur_script_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # get parent dir. Now we are in /an/unknown/path/kalliope
        parent_dir = os.path.normpath(cur_script_directory + os.sep + os.pardir)
        # we add the kalliope.py file name
        real_entry_point_path = parent_dir + os.sep + KALLIOPE_ENTRY_POINT_SCRIPT
        # We test that the file exist before return it
        logger.debug("Real Kalliope.py path: %s" % real_entry_point_path)
        if os.path.isfile(real_entry_point_path):
            crontab_cmd = "python %s start --brain-file %s --run-synapse " % (real_entry_point_path,
                                                                              self.brain.brain_file)
            return crontab_cmd
        raise IOError("kalliope.py file not found")
