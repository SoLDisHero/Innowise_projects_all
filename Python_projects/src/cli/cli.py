import argparse

def cli_parser():
    parser = argparse.ArgumentParser(description="Managing student and rooms data")
    # add room argument
    parser.add_argument("--students", required=True, help="Path to student data file --> data/students.json")

    # add room argument
    parser.add_argument("--rooms", required=True, help="Path to room data file --> data/rooms.json")

    # add format
    parser.add_argument("--format", choices=['json', 'xml'], default='json', help="Formats: json or xml")

    return parser.parse_args()