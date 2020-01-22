import os
import errno
import shutil
import pickle
import random
from configparser import ConfigParser
from math import floor
from logaspect.groundtruth.split_xml_format import SplitXMLFormat
from logaspect.groundtruth.split_ilwaanet_format import SplitIlwaanetFormat


class Split(object):
    # split each file to three parts: train, dev, and test
    # compositition: train: 60, dev: 20, test: 20
    def __init__(self, dataset):
        self.dataset = dataset
        self.dataset_conf = {}
        self.files = {}
        self.random_seed = 101
        self.train_size = 0.8

    @staticmethod
    def __check_path(path):
        # check a path is exist or not. if not exist, then create it
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def __set_datapath(self):
        # set data path for output files
        self.__check_path(self.xml_path)
        self.train_file = os.path.join(self.xml_path, 'xml.train.txt')
        self.test_file = os.path.join(self.xml_path, 'xml.test.txt')

    def __get_dataset(self):
        # get dataset configuration
        current_path = os.path.dirname(os.path.realpath(__file__))
        dataset_config_path = os.path.join(current_path, 'datasets.conf')

        # read dataset path from .conf file
        parser = ConfigParser()
        parser.read(dataset_config_path)
        for section_name in parser.sections():
            options = {}
            for name, value in parser.items(section_name):
                options[name] = value
            self.dataset_conf[section_name] = options

        # set output path
        self.xml_path = self.dataset_conf['main']['xml_path']

        # get dataset and groundtruth path
        dataset_path = os.path.join(self.dataset_conf['main']['dataset_path'], self.dataset,
                                    self.dataset_conf['main']['logs_dir'])
        groundtruth_pickle = os.path.join(self.dataset_conf['main']['dataset_path'], self.dataset,
                                          self.dataset_conf['main']['xml_pickle_dir'])
        filenames = os.listdir(dataset_path)

        # get full path of each filename
        for filename in filenames:
            self.files[filename] = {
                'xml_pickle_file': os.path.join(groundtruth_pickle, filename)
            }

    def split(self):
        # set conll output files and create conll-format instance
        self.__get_dataset()
        self.__set_datapath()

        train_data = []
        test_data = []

        for filename, properties in self.files.items():
            print('pickle file     :', self.dataset, filename)

            # parsed_list is list of dictionaries containing parsed log entries
            with open(properties['xml_pickle_file'], 'rb') as f_pickle:
                parsed_list = pickle.load(f_pickle)

            # note: test_length = dev_length
            lines_length = len(parsed_list)
            train_length = floor(0.8 * lines_length)

            # get training, dev, and test data
            for data in parsed_list[:train_length]:
                train_data.append(data)

            for data in parsed_list[train_length:]:
                test_data.append(data)

        return train_data, test_data

    def split_random(self):
        self.__get_dataset()
        self.__set_datapath()

        train_data = []
        test_data = []

        for filename, properties in self.files.items():
            print('pickle file     :', self.dataset, filename)

            # parsed_list is list of dictionaries containing parsed log entries
            with open(properties['xml_pickle_file'], 'rb') as f_pickle:
                parsed_list = pickle.load(f_pickle)

            # check positive and negative
            positives = []
            negatives = []
            for index, element in enumerate(parsed_list):
                if element['sentiment'] == 'positive':
                    positives.append(index)
                elif element['sentiment'] == 'negative':
                    negatives.append(index)

            # random sequence for positive
            list_len = len(positives)
            random.Random(self.random_seed).shuffle(positives)

            train_length = floor(self.train_size * list_len)
            for index in positives[:train_length]:
                train_data.append(parsed_list[index])

            for index in positives[train_length:]:
                test_data.append(parsed_list[index])

            # random sequence for negative
            negative_len = len(negatives)
            if negative_len > 0:
                random.Random(self.random_seed).shuffle(negatives)

                train_length = floor(self.train_size * negative_len)
                for index in negatives[:train_length]:
                    train_data.append(parsed_list[index])

                for index in negatives[train_length:]:
                    test_data.append(parsed_list[index])

        return train_data, test_data


def split_all(train_data, test_data, train_file, test_file):
    split = SplitXMLFormat(train_data, train_file)
    split.convert()

    split = SplitXMLFormat(test_data, test_file)
    split.convert()


def split_all_ilwaanet(train_data, test_data, train_file, test_file):
    split = SplitIlwaanetFormat(train_data, train_file)
    split.convert()

    split = SplitIlwaanetFormat(test_data, test_file)
    split.convert()


def remove_directories():
    # remove output directories
    punctuation_path = '/home/hudan/Git/pylogforensics/datasets/data-xml/'
    if os.path.isdir(punctuation_path):
        shutil.rmtree(punctuation_path)

if __name__ == '__main__':
    datasets = [
        # 'casper-rw',
        # 'dfrws-2009-jhuisi',
        # 'dfrws-2009-nssal',
        'honeynet-challenge7'
    ]

    remove_directories()
    train_all, test_all = [], []
    train_filename, test_filename = '', ''
    for dataset_name in datasets:
        split_dataset = Split(dataset_name)
        # train, test = split_dataset.split()
        train, test = split_dataset.split_random()
        train_all.extend(train)
        test_all.extend(test)
        train_filename = split_dataset.train_file
        test_filename = split_dataset.test_file

    # split
    split_all(train_all, test_all, train_filename, test_filename)
    # split_all_ilwaanet(train_all, test_all, train_filename, test_filename)
