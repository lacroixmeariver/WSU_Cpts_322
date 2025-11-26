"""cleans data from the incoming csv."""

from __future__ import annotations

import csv
import os
import re
from datetime import datetime


def clean_csv(input_csv, output_csv=None):
    """Clean the raw csv data into a structured format."""
    # create cleaned version of the csv
    if output_csv is None:
        input_dir = os.path.dirname(input_csv)
        input_filename = os.path.basename(input_csv)
        output_filename = f"cleaned_{input_filename}"
        output_csv = os.path.join(input_dir, output_filename)

    cleaned_data = []

    with open(input_csv, "r", encoding="utf-8") as infile:
        reader = csv.reader(infile)

        for row in reader:
            if not row:
                continue
            row_text = " ".join(str(cell) for cell in row)

            # only look at rows with patron data
            if "Number of Patron" in row_text:
                room_data = get_row_data(row)
                if room_data:
                    cleaned_data.append(room_data)

    # write to a new csv that's properly formatted
    with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)

        # header
        writer.writerow(
            [
                "Building",
                "Room Number",
                "TimesAccessed",
                "AccessSucceed",
                "AccessFail",
                "DateEntered",
            ]
        )

        # rows
        for data in cleaned_data:
            writer.writerow(data)

    print(f"Cleaned data saved to {output_csv}")
    print(f"Processed {len(cleaned_data)} entries")

    result = []
    for data in cleaned_data:
        result.append(data)

    return result


def get_row_data(row):
    """Extract relevant data from a csv row."""
    row_string = " ".join(str(cell) for cell in row)
    num_patrons = row_string.find("Number of Patron")
    if num_patrons == -1:
        return None

    # location is before "Number of Patron"
    location = row_string[:num_patrons].strip()

    # Parse building and room number using regex
    building, room_num = parse_building_room(location)
    if not building or not room_num:
        return None

    # get use statistics
    passed = get_number(row_string, "Total Number Passed")
    failed = get_number(row_string, "Total Number Failed")
    total = get_number(row_string, "Total Number of Transaction")

    # calc  total as backup
    if total:
        times_accessed = total
    else:
        times_accessed = passed + failed

    date = get_date(row_string)

    return [building, room_num, times_accessed, passed, failed, date]


def parse_building_room(row_string):
    """Parse building and room number from row."""
    # same buildings different names
    building_aliases = {
        "Dana": ["Dana Hall", "Dana"],
        "EEME": ["EEME"],
        "Sloan": ["Sloan Hall", "Sloan"],
    }

    # look for building names and variants
    building = None
    alias = None
    for bldg, patterns in building_aliases.items():
        for pattern in patterns:
            if pattern in row_string:
                building = bldg
                alias = pattern
                break
        if building:
            break

    if not building:
        return None, None

    # Find room number after building name
    building_index = row_string.find(alias)
    if building_index != -1:
        after_building = row_string[building_index + len(alias) :].strip()

        # base case
        room_match = re.search(r"Room\s+(\d+[A-Za-z]?\b)", after_building, re.IGNORECASE)  # noqa
        if room_match:
            return building, room_match.group(1)

        # more general if 1st doesn't work
        room_match = re.search(r"(\b\d{2,4}[A-Za-z]?\b)", after_building)
        if room_match:
            return building, room_match.group(1)

    return building, None


def get_number(text, keyword):
    """Extract number following a keyword in text."""
    # look for keyword in text
    index = text.find(keyword)
    if index == -1:
        return 0

    # return number after keyword
    remaining = text[index + len(keyword) :]
    num_match = re.search(r"(\d+)", remaining)
    if num_match:
        return int(num_match.group(1))
    return 0


def get_date(text):
    """Extract date from text."""
    # parse date in mm/dd/yyyy format
    date = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", text)
    if date:
        return date.group(1)

    # use current date if none found
    return datetime.now().strftime("%m/%d/%Y")


def main():
    """Demonstrates cleaning."""
    input_csv = "docs/downloaded_csvs/VCEA Clubs Access Summary by Location.CSV"

    clean_csv(input_csv)

    input_dir = os.path.dirname(input_csv)
    input_filename = os.path.basename(input_csv)
    output_csv = os.path.join(input_dir, f"cleaned_{input_filename}")

    print("\nSample of cleaned data:")
    with open(output_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"{' | '.join(headers)}")
        print("-" * 50)
        for row in enumerate(reader):
            print(f"{' | '.join(str(cell) for cell in row)}")


if __name__ == "__main__":
    main()
