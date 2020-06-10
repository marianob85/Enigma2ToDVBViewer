import unittest
import Kingofsat


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        pass

    def test_apid_extract(self):
        inputData = [
            ("80|81|qaa|82|83", [("80", ""), ("81", "qaa"), ("82", ""), ("83", "")]),
            ("4061|esp|4062|vo", [("4061","esp"),("4062","vo")]),
            ("116|esp|117|vo|118 tre|119|126|127", [("116","esp"),("117","vo"),("118","tre"),("119", ""),("126", ""),("127", "")]),
            ("80|esp|81|qaa|82|83",[("80","esp"),("81","qaa"),("82", ""),("83", "")])
        ]
        for data in inputData:
            self.assertEqual(data[1], Kingofsat.extract_audio_pids(data[0]))


if __name__ == '__main__':
    unittest.main()
