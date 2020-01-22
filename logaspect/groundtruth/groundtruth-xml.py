import errno
import os
import pickle
from configparser import ConfigParser
from nerlogparser.nerlogparser import Nerlogparser


class GroundTruth(object):
    def __init__(self, datasets_config_file=''):
        self.dataset = ''
        self.datasets_config_file = datasets_config_file
        self.configurations = {}

        self.parser = Nerlogparser()

    @staticmethod
    def __check_path(path):
        # check a path is exist or not. if not exist, then create it
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def __read_configuration(self):
        # get configuration path
        if self.datasets_config_file:
            config_path = self.datasets_config_file
        else:
            current_path = os.path.dirname(os.path.realpath(__file__))
            config_path = os.path.join(current_path, 'datasets.conf')

        # parse config file
        parser = ConfigParser()
        parser.read(config_path)

        # get all configurations
        for section_name in parser.sections():
            options = {}
            for name, value in parser.items(section_name):
                if '\n' in value:
                    value = value.split('\n')
                options[name] = value

            self.configurations[section_name] = options

    @staticmethod
    def __read_wordlist(log_type, term_type):
        # read word list of particular log type for initial abstraction
        current_path = os.path.dirname(os.path.realpath(__file__))
        current_path = os.path.join(current_path, term_type)

        # open word list files in the specified directory
        wordlist_path = os.path.join(current_path, log_type + '.txt')
        with open(wordlist_path, 'r') as f:
            wordlist_temp = f.readlines()

        # get word list
        wordlist = []
        for wl in wordlist_temp:
            wordlist.append(wl.strip())

        return wordlist

    def __get_preprocessed_logs(self, log_file):
        # parse log files
        parsed_logs = self.parser.parse_logs(log_file)

        return parsed_logs

    @staticmethod
    def __extract_term(log_message, master_terms, mode):
        extracted_terms = []
        titlecase_terms = []
        uppercase_terms = []
        sentiment = 1
        log_message_split = log_message.split()

        # check for lower case terms
        for word in log_message_split:
            for master_term in master_terms:
                if master_term == word:
                    if mode == 'aspect':
                        start_index = log_message.index(master_term)
                        end_index = start_index + len(master_term)
                        extracted_terms.append((master_term, start_index, end_index))

                    elif mode == 'sentiment':
                        sentiment = 0
                else:
                    titlecase_terms.append(master_term)

        # check for Title case terms
        for word in log_message_split:
            for master_term in titlecase_terms:
                master_term_split = master_term.split()
                first_word_title_case = master_term_split[0].title()
                master_term = ' '.join([first_word_title_case] + master_term_split[1:])
                if master_term == word:
                    if mode == 'aspect':
                        start_index = log_message.index(master_term)
                        end_index = start_index + len(master_term)
                        extracted_terms.append((master_term, start_index, end_index))

                    elif mode == 'sentiment':
                        sentiment = 0
                else:
                    uppercase_terms.append(master_term)

        # check for UPPER case terms
        for word in log_message_split:
            for master_term in uppercase_terms:
                master_term_split = master_term.split()
                first_word_upper_case = master_term_split[0].upper()
                master_term = ' '.join([first_word_upper_case] + master_term_split[1:])
                if master_term == word:
                    if mode == 'aspect':
                        start_index = log_message.index(master_term)
                        end_index = start_index + len(master_term)
                        extracted_terms.append((master_term, start_index, end_index))

                    elif mode == 'sentiment':
                        sentiment = 0

        if mode == 'aspect':
            return extracted_terms

        elif mode == 'sentiment':
            return sentiment

    def __set_tag(self, log_file, sentiment_terms, aspect_terms):
        # preprocessing of logs
        parsed_logs = self.__get_preprocessed_logs(log_file)

        # set tag
        word_tags = []
        for line_id, parsed_log in parsed_logs.items():
            log_message = parsed_log['message']

            if log_message != '':
                # extract sentiment and aspect terms
                aspect_data = self.__extract_term(log_message, aspect_terms, 'aspect')
                sentiment_data = self.__extract_term(log_message, sentiment_terms, 'sentiment')
                sentiment = 'positive' if sentiment_data == 1 else 'negative'

                # save a log line to three lines of data format
                aspect_dict = None
                if len(aspect_data) >= 1:
                    # noinspection PyUnresolvedReferences
                    aspect_dict = {
                        'sentence': log_message,
                        'term': aspect_data,
                        'sentiment': sentiment
                    }

                elif len(aspect_data) == 0:
                    aspect_dict = {
                        'sentence': log_message,
                        'term': None,
                        'sentiment': sentiment
                    }

                word_tags.append(aspect_dict)

        return word_tags, parsed_logs

    def __save_groundtruth(self, word_tags, filename):
        # save sentiment dataset to xml format
        groundtruth_dir = os.path.join(self.configurations['main']['dataset_path'], self.dataset,
                                       self.configurations['main']['xml_pickle_dir'])
        self.__check_path(groundtruth_dir)

        # save parsed logs to a pickle file
        pickle_file = os.path.join(groundtruth_dir, filename)
        with open(pickle_file, 'wb') as f_pickle:
            pickle.dump(word_tags, f_pickle, protocol=pickle.HIGHEST_PROTOCOL)

    def set_ground_truth(self, dataset):
        self.dataset = dataset

        # read configuration file
        self.__read_configuration()
        logtypes = self.configurations[self.dataset + '-logtype']['logtype']

        # if logtypes is string, then convert it to list
        if isinstance(logtypes, str):
            logtypes = [logtypes]

        # get sentiment ground truth per log type
        for logtype in logtypes:
            # get list of log types
            if isinstance(self.configurations[self.dataset][logtype], str):
                file_list = [self.configurations[self.dataset][logtype]]
            else:
                file_list = self.configurations[self.dataset][logtype]

            sentiment_terms = self.__read_wordlist(logtype, 'sentiment-terms')
            aspect_terms = self.__read_wordlist(logtype, 'aspect-terms')
            for filename in file_list:
                print('Processing', filename, '...')

                # set tag for sentiment and aspect terms
                log_file = os.path.join(self.configurations['main']['dataset_path'], self.dataset,
                                        self.configurations['main']['logs_dir'], filename)
                word_tags, parsed_logs = self.__set_tag(log_file, sentiment_terms, aspect_terms)

                # save ground truth to a pickle file
                self.__save_groundtruth(word_tags, filename)


if __name__ == '__main__':
    datasets = [
        'casper-rw',
        'dfrws-2009-jhuisi',
        'dfrws-2009-nssal',
        'honeynet-challenge7'
    ]

    gt = GroundTruth()
    for dataset_name in datasets:
        print('\nProcessing', dataset_name, '...')
        gt.set_ground_truth(dataset_name)
