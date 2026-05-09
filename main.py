# import the necessary modules and libraries
import json
import unittest
import datetime
from pathlib import Path


def load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Required JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


# convert json data from format 1 to the expected format
def convert_from_format1(json_object):
    location_parts = json_object["location"].split("/")
    if len(location_parts) != 5:
        raise ValueError(
            "Format 1 location must be Country/City/Area/Factory/Section"
        )

    return {
        "deviceID": json_object["deviceID"],
        "deviceType": json_object["deviceType"],
        "timestamp": json_object["timestamp"],
        "location": {
            "country": location_parts[0],
            "city": location_parts[1],
            "area": location_parts[2],
            "factory": location_parts[3],
            "section": location_parts[4],
        },
        "data": {
            "status": json_object["operationStatus"],
            "temperature": json_object["temp"],
        },
    }


# convert json data from format 2 to the expected format
def convert_from_format2(json_object):
    dt = datetime.datetime.strptime(
        json_object["timestamp"],
        "%Y-%m-%dT%H:%M:%S.%fZ",
    )
    timestamp = int((dt - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

    return {
        "deviceID": json_object["device"]["id"],
        "deviceType": json_object["device"]["type"],
        "timestamp": timestamp,
        "location": {
            "country": json_object["country"],
            "city": json_object["city"],
            "area": json_object["area"],
            "factory": json_object["factory"],
            "section": json_object["section"],
        },
        "data": {
            "status": json_object["data"]["status"],
            "temperature": json_object["data"]["temperature"],
        },
    }


def main(json_object):
    if json_object.get("device") is None:
        return convert_from_format1(json_object)
    return convert_from_format2(json_object)


class TestSolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_dir = Path(__file__).resolve().parent
        cls.jsonData1 = load_json_file(data_dir / "data-1.json")
        cls.jsonData2 = load_json_file(data_dir / "data-2.json")
        cls.jsonExpectedResult = load_json_file(data_dir / "data-result.json")

    def test_sanity(self):
        result = json.loads(json.dumps(self.jsonExpectedResult))
        self.assertEqual(result, self.jsonExpectedResult)

    def test_dataType1(self):
        result = main(self.jsonData1)
        self.assertEqual(
            result,
            self.jsonExpectedResult,
            "Converting from Type 1 failed",
        )

    def test_dataType2(self):
        result = main(self.jsonData2)
        self.assertEqual(
            result,
            self.jsonExpectedResult,
            "Converting from Type 2 failed",
        )


if __name__ == "__main__":
    unittest.main()
