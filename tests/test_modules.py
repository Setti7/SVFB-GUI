import os
import unittest

import cv2
import numpy as np

from utils.Globals import logging
from utils.SaveData import SaveData, fishing_region

CWD = os.getcwd()
MAIN_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(MAIN_DIR, "media")
MEDIA_TEST = os.path.join(CWD, "media-test")
LOG_FILE = os.path.join(CWD, "log.log")


class TestSaveData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.chdir(MAIN_DIR)

    @classmethod
    def tearDownClass(cls):
        logging.shutdown()
        os.remove(LOG_FILE)

    def setUp(self):
        self.instance = SaveData('c')

    def test_load_template(self):
        # Check if templates are being loaded correctly

        for i in range(-5, 6):
            fishing_region_file = os.path.join(MEDIA_ROOT, f'Images\\fr {i}g.png')
            region_template_zoom = cv2.imread(fishing_region_file, 0)

            region_template, *_ = self.instance.load_template(i)
            np.testing.assert_array_equal(region_template, region_template_zoom)

    def test_fishing_region(self):
        # Check if fishing region is found on all templates
        # TODO: take screenshot with all zoom levels

        fishing_file = os.path.join(MEDIA_TEST, f'fishing_zoom_level_-4.png')
        fishing_img_bgr = cv2.imread(fishing_file, 1)

        region_template_gray, w_template, h_template = self.instance.load_template(-4)

        self.assertTrue(fishing_region(fishing_img_bgr, region_template_gray, w_template, h_template)['Detected'])

    def test_find_zoom(self):
        # Check if zoom level is being found
        # TODO: take screenshot with all zoom levels

        fishing_file = os.path.join(MEDIA_TEST, 'fishing_zoom_level_-4.png')
        fishing_img_bgr = cv2.imread(fishing_file, 1)

        result = self.instance.find_zoom(fishing_img_bgr)

        self.assertTrue(result['Found'])
        self.assertEqual(result['Zoom'], -4)

    def test_validate(self):
        first_frame = os.path.join(MEDIA_TEST, 'fishing_first_frame.png')
        success_session = os.path.join(MEDIA_TEST, 'fishing_success.png')
        success_session_close = os.path.join(MEDIA_TEST, 'fishing_success_close.png')
        failure_session_above = os.path.join(MEDIA_TEST, 'fishing_failure_above.png')
        failure_session_below = os.path.join(MEDIA_TEST, 'fishing_failure_below.png')
        failure_session_above_close = os.path.join(MEDIA_TEST, 'fishing_failure_above_close.png')
        failure_session_below_close = os.path.join(MEDIA_TEST, 'fishing_failure_below_close.png')
        failure_session_chest = os.path.join(MEDIA_TEST, 'fishing_failure_chest.png')

        first_frame = cv2.imread(first_frame, 1)
        success_session = cv2.imread(success_session, 1)
        success_session_close = cv2.imread(success_session_close, 1)
        failure_session_above = cv2.imread(failure_session_above, 1)
        failure_session_below = cv2.imread(failure_session_below, 1)
        failure_session_above_close = cv2.imread(failure_session_above_close, 1)
        failure_session_below_close = cv2.imread(failure_session_below_close, 1)
        failure_session_chest = cv2.imread(failure_session_chest, 1)

        result_success = self.instance.validate(first_frame, success_session)
        result_success_close = self.instance.validate(first_frame, success_session_close)
        result_failure_above = self.instance.validate(first_frame, failure_session_above)
        result_failure_below = self.instance.validate(first_frame, failure_session_below)
        result_failure_above_close = self.instance.validate(first_frame, failure_session_above_close)
        result_failure_below_close = self.instance.validate(first_frame, failure_session_below_close)
        result_failure_chest = self.instance.validate(first_frame, failure_session_chest)

        self.assertTrue(result_success)
        self.assertTrue(result_success_close)
        self.assertFalse(result_failure_above)
        self.assertFalse(result_failure_below)
        self.assertFalse(result_failure_above_close)
        self.assertFalse(result_failure_below_close)
        self.assertFalse(result_failure_chest)
