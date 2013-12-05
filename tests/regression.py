import unittest
from test_utils import start_jenkins

class regression_tests(unittest.TestCase):
    
    __jenkins_process = None
    
    def setUp(self):
        self.__jenkins_process = start_jenkins()
         
    def tearDown(self):
        self.__jenkins_process.terminate()
        
    def test1(self):
        pass

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(regression_tests)
    unittest.TextTestRunner(verbosity=3).run(suite)    