# -*- coding: utf-8 -*-
import logging

from gmail import Gmail
from email.header import decode_header
from core.NeuronModule import NeuronModule, MissingParameterException

logging.basicConfig()
logger = logging.getLogger("kalliope")


class Gmail_checker(NeuronModule):
    def __init__(self, **kwargs):
        super(Gmail_checker, self).__init__(**kwargs)

        # check if parameters have been provided
        username = kwargs.get('username', None)
        password = kwargs.get('password', None)

        if username is None:
            raise MissingParameterException("Username parameter required")

        if password is None:
            raise MissingParameterException("Password parameter required")

        # prepare a returned dict
        returned_dict = dict()

        g = Gmail()
        g.login(username, password)

        # check if login succeed
        logging.debug("Gmail loggin ok: %s" % g.logged_in)  # Should be True, AuthenticationError if login fails

        # get unread mail
        unread = g.inbox().mail(unread=True)

        returned_dict["unread"] = len(unread)

        if len(unread) > 0:
            # add a list of subject
            subject_list = list()
            for email in unread:
                email.fetch()
                encoded_subject = email.subject
                subject = self._parse_subject(encoded_subject)
                subject_list.append(subject)

            returned_dict["subjects"] = subject_list

        logger.debug("gmail neuron returned dict: %s" % str(returned_dict))
        # logout of gmail
        g.logout()
        self.say(returned_dict)

    def _parse_subject(self, encoded_subject):
        dh = decode_header(encoded_subject)

        return ''.join([self.try_parse(t[0], t[1]) for t in dh])

    @staticmethod
    def try_parse(header, encoding):

        if encoding is None:
            encoding = 'ASCII'
        try:
            return unicode(header, encoding)
        except UnicodeDecodeError:
            try:
                return unicode(header, 'ISO-8859-1')
            except UnicodeDecodeError:
                return unicode(header, 'UTF-8')
