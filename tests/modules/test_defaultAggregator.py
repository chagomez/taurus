import logging
import time

from tests import BZTestCase, r, rc, err

from bzt.modules.aggregator import ResultsReader, DataPoint, KPISet
from tests.mocks import MockReader


class TestDefaultAggregator(BZTestCase):
    def setUp(self):
        super(TestDefaultAggregator, self).setUp()
        self.obj = ResultsReader()
        self.obj.track_percentiles = [25, 50, 75, 80, 90, 95, 99, 99.9, 100]
        self.obj.buffer_scale_idx = str(float(self.obj.track_percentiles[-1]))
        self.obj.buffer_len = 1

    def test_1(self):
        obj = self.obj

        mock = MockReader()
        mock.buffer_scale_idx = '100.0'
        mock.data.append((1, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((2, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((2, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((3, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((3, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((4, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((4, "", 1, r(), r(), r(), 200, None, '', 0))

        obj.add_listener(mock)

        for point in mock.datapoints():
            self.assertNotEquals(0, point[DataPoint.CUMULATIVE][''][KPISet.CONCURRENCY])

        mock.data.append((2, "", 1, r(), r(), r(), 200, None, '', 0))
        mock.data.append((2, "", 1, r(), r(), r(), 200, None, '', 0))

        for point in mock.datapoints():
            pass

        for point in mock.datapoints(True):
            pass

        for point in mock.results:
            overall = point[DataPoint.CURRENT]['']
            self.assertTrue(len(overall[KPISet.PERCENTILES]) > 0)

    def test_speed(self):
        obj = self.obj

        mock = MockReader()
        mock.buffer_scale_idx = '100.0'
        obj.add_listener(mock)

        res = {}
        # current measurements shows ~25K samples/sec
        for cnt in (10, 100, 1000, 10000, 25000, 40000, 50000):
            for a in range(0, cnt):
                sample = (cnt, "", 1, r(1000), r(1000), r(1000), rc(), err(), '', 0)
                mock.data.append(sample)
            before = time.time()
            for point in mock.datapoints():
                pass
            after = time.time()
            res[cnt] = after - before
            logging.info("Times: %s", res)

            while mock.results:
                point = mock.results.pop(0)
                overall = point[DataPoint.CURRENT]['']
                self.assertTrue(len(overall[KPISet.PERCENTILES]) > 0)

        for point in mock.datapoints(True):
            pass

    def test_0buffer_scaling(self):
        obj = self.obj

        mock = MockReader()
        obj.add_listener(mock)

        # t_stamp, label, conc, r_time, con_time, latency, r_code, error, trname
        mock.min_buffer_len = 1
        mock.buffer_len = 1
        mock.buffer_multiplier = 1
        mock.buffer_scale_idx = '50.0'

        buffer_len = mock.buffer_len
        for i in range(5):
            mock.data.append((100 + i, "", 1, 2, 2, 2, 200, None, '', 0))
        points = list(mock.datapoints())
        points = list(mock.datapoints())
        self.assertTrue(mock.buffer_len > buffer_len)
        buffer_len = mock.buffer_len

        for i in range(10):
            mock.data.append((200 + i, "", 1, 3, 3, 3, 200, None, '', 0))
        points = list(mock.datapoints())
        points = list(mock.datapoints())
        self.assertTrue(mock.buffer_len > buffer_len)
        buffer_len = mock.buffer_len

        for i in range(20):
            mock.data.append((300 + i, "", 1, 4, 4, 4, 200, None, '', 0))
        points = list(mock.datapoints())
        points = list(mock.datapoints())
        self.assertTrue(mock.buffer_len > buffer_len)
        buffer_len = mock.buffer_len

        for i in range(15):
            mock.data.append((400 + i, "", 1, 1, 1, 1, 200, None, '', 0))
        points = list(mock.datapoints())
        points = list(mock.datapoints())
        self.assertTrue(mock.buffer_len < buffer_len)
        buffer_len = mock.buffer_len

        for i in range(30):
            mock.data.append((500 + i, "", 1, 1, 1, 1, 200, None, '', 0))
        points = list(mock.datapoints())
        points = list(mock.datapoints())
        self.assertTrue(mock.buffer_len < buffer_len)
