import unittest
from vapi_telecmi_server import TestAudioConversation

class VapiTelecmiServerTest(unittest.TestCase):
    def test_basic_functionality(self):
        # Run the existing placeholder test
        test_instance = TestAudioConversation()
        test_instance.test_basic_functionality()

    def test_error_handling(self):
        # Run the existing error handling test
        test_instance = TestAudioConversation()
        test_instance.test_error_handling()

if __name__ == "__main__":
    unittest.main()
