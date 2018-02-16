'''
Extracting Apple Watch Health Data
'''
import time
from datetime import datetime
from xml.dom import minidom
import numpy as np
import pandas as pd

class AppleWatchData(object):
    '''
    Object to contain all relevant data access calls for Apple Watch health data.
    '''
    # TODO: make parsing of xml file a helper function
    def __init__(self, xml_data_file_path, source_name, tag_name='Record'):
        """
        Class can be generalized to retrieve data from sources other than Apple Watch.

        :param xml_data_file_path: local path to xml file exported by Health App on iPhone
        :param source_name: source of health data (i.e. Apple Watch)
        :param tag_name: xml tag to parse data from
        """
        self.file_path = xml_data_file_path
        self.source_name = source_name
        self.tag_name = tag_name
        self.xmldoc = minidom.parse(xml_data_file_path)
        self.records = self.xmldoc.getElementsByTagName(self.tag_name)

    def parse_tag(self, attribute):
        """
        Filter for records in Health Data matching attribute name.

        :param attribute: attribute name of xml Record tag
        :return: a list of all records matching class's source name and attribute name
        """
        record_list = []
        for s in self.records:
            found1 = s.attributes['type'].value == attribute
            if self.source_name == 'Apple Watch':
                found2 = u'Apple\xa0Watch' in s.attributes['sourceName'].value
            else:
                found2 = self.source_name in s.attributes['sourceName'].value
            # parse the record
            if found1 and found2:
                record_list.append(s)
        return record_list

    def parse_record(self, record):
        """
        For a given record pull and start timestamp, end timestamp, and health data value.

        :param record: xml object with tag name of Record
        :return: Record's start timestamp, end timestamp, and biometric data
        """
        # Extract start time stamp
        start_timestamp_string = record.attributes['startDate'].value
        start_time = datetime.strptime(start_timestamp_string, '%Y-%m-%d %H:%M:%S -0500')
        # Extract end time stamp
        end_timestamp_string = record.attributes['endDate'].value
        end_time = datetime.strptime(end_timestamp_string, '%Y-%m-%d %H:%M:%S -0500')

        # Extract biometric
        try:
            # convert to float for numerical values
            biometric = float(record.attributes['value'].value)
        except:
            biometric = record.attributes['value'].value

        return start_time, end_time, biometric

    def parse_record_list(self, record_list):
        """
        Generate array of timestamps and data values returned by multiple records.

        :param record_list: list of xml objects with tag name Record
        :return: array of timestamps and data values returned by parse_record()
        """
        # vectorize extraction record values
        apple_data = map(lambda record: self.parse_record(record), record_list)
        apple_array = np.array(apple_data)

        return apple_array

    def load_heart_rate_data(self):
        """

        :return: data frame of instantaneous beats per minute and respective time stamps
        """
        # count data
        attribute = 'HKQuantityTypeIdentifierHeartRate'
        record_list = self.parse_tag(attribute)
        hr_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        hr_data_df['start_timestamp'] = apple_array[:, 0]
        hr_data_df['end_timestamp'] = apple_array[:, 1]
        hr_data_df['heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        # sort by start time
        hr_data_df.sort_values('start_timestamp', inplace=True)

        return hr_data_df

    def load_heart_rate_variability_data(self):
        """

        :return: data frame of average standard deviation of NN (beat-to-beat) intervals and
                 instantaneous heart rate measures (BPM) used to derive this estimate
        """
        # units of milliseconds
        attribute = 'HKQuantityTypeIdentifierHeartRateVariabilitySDNN'
        record_list = self.parse_tag(attribute)
        hrv_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        # parse metadata list
        instantaneous_bpm = []
        for s in record_list:
            meta_data = {'bpm': [], 'time': []}
            nodes = s.childNodes[1].getElementsByTagName('InstantaneousBeatsPerMinute')
            for node in nodes:
                meta_data['bpm'].append(node.attributes['bpm'].value)
                meta_data['time'].append(node.attributes['time'].value)

            instantaneous_bpm.append(meta_data)

        hrv_data_df['start_timestamp'] = apple_array[:, 0]
        hrv_data_df['end_timestamp'] = apple_array[:, 1]
        hrv_data_df['heart_rate_variability'] = pd.to_numeric(apple_array[:, 2], errors='ignore')
        hrv_data_df['instantaneous_bpm'] = instantaneous_bpm

        return hrv_data_df

    def load_resting_heart_rate_data(self):
        """

        :return: data frame of average resting heart rate (BPM) per diem
        """
        # units of BPM
        attribute = 'HKQuantityTypeIdentifierRestingHeartRate'
        record_list = self.parse_tag(attribute)
        resting_hr_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        resting_hr_data_df['start_timestamp'] = apple_array[:, 0]
        resting_hr_data_df['end_timestamp'] = apple_array[:, 1]
        resting_hr_data_df['resting_heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        # sort by start time
        resting_hr_data_df.sort_values('start_timestamp', inplace=True)

        return resting_hr_data_df

    def load_walking_heart_rate_data(self):
        """

        :return: data frame of average walking heart rate (BPM) per diem
        """
        # units of BPM
        attribute = 'HKQuantityTypeIdentifierWalkingHeartRateAverage'
        record_list = self.parse_tag(attribute)
        walking_hr_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        walking_hr_data_df['start_timestamp'] = apple_array[:, 0]
        walking_hr_data_df['end_timestamp'] = apple_array[:, 1]
        walking_hr_data_df['walking_heart_rate'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        # sort by start time
        walking_hr_data_df.sort_values('start_timestamp', inplace=True)

        return walking_hr_data_df

    def load_distance_data(self):
        """

        :return: data frame of miles walked/ran and respective timestamps
        """
        # units of miles
        attribute = 'HKQuantityTypeIdentifierDistanceWalkingRunning'
        record_list = self.parse_tag(attribute)
        distance_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        distance_data_df['start_timestamp'] = apple_array[:, 0]
        distance_data_df['end_timestamp'] = apple_array[:, 1]
        distance_data_df['distance_walk_run'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return distance_data_df

    def load_basal_energy_data(self):
        """

        :return: data frame of basal kilocalories burned and respective timestamps
        """
        # units of kilocalories
        attribute = 'HKQuantityTypeIdentifierBasalEnergyBurned'
        record_list = self.parse_tag(attribute)
        energy_burned_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        energy_burned_data_df['start_timestamp'] = apple_array[:, 0]
        energy_burned_data_df['end_timestamp'] = apple_array[:, 1]
        energy_burned_data_df['energy_burned'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return energy_burned_data_df

    def load_stand_hour_data(self):
        """

        :return: data frame of stand hour labels (i.e. stood vs idle) per hour
        """
        # Two stand labels are 'Stood' and 'Idle'
        attribute = 'HKCategoryTypeIdentifierAppleStandHour'
        record_list = self.parse_tag(attribute)
        stand_hour_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        stand_hour_df['start_timestamp'] = apple_array[:, 0]
        stand_hour_df['end_timestamp'] = apple_array[:, 1]
        stand_hour_df['stand_hour'] = apple_array[:, 2]

        # rename stand hour labels
        new_labels = {'HKCategoryValueAppleStandHourIdle': 'Idle',
                       'HKCategoryValueAppleStandHourStood': 'Stood'}
        stand_hour_df['stand_hour'] = stand_hour_df['stand_hour']\
            .replace(new_labels)

        return stand_hour_df

    def load_step_data(self):
        """

        :return: data frame of step data and respective timestamps
        """
        # step count data
        attribute = 'HKQuantityTypeIdentifierStepCount'
        record_list = self.parse_tag(attribute)
        step_data_df = pd.DataFrame()

        # parse records
        apple_array = self.parse_record_list(record_list)
        step_data_df['start_timestamp'] = apple_array[:, 0]
        step_data_df['end_timestamp'] = apple_array[:, 1]
        step_data_df['steps'] = pd.to_numeric(apple_array[:, 2], errors='ignore')

        return step_data_df