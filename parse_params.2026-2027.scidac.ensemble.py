#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------
# Parse the OA4 physics manifest CSV and emit add_case(...) lines to paste into another script.
#
# Each data row becomes one line, e.g.:
#   add_case(**kwargs,EF=0.350, CF=10.00, HD=0.500, HM=2.500, PS=700.0, FT= 7.4925, FE=1.000, OB=0.002500, OE=0.375)

import csv
import sys
import argparse


# --------------------------------------------------------------------------------------------------
# Field formatting spec
# Order here sets the parameter order in each emitted line. Each entry pairs the CSV column with the
# format applied to its value. FT uses width 7 so single-digit values line up under the two-digit ones,
# which is where the leading space in "FT= 7.4925" comes from. Only FT is width-padded, matching your
# example. If you want CF (or others) aligned too, just widen its format, e.g. "{:6.2f}".

FIELD_FORMATS = [
    # ("EF", "{:.3f}"),
    # ("CF", "{:.2f}"),
    # ("HD", "{:.3f}"),
    # ("HM", "{:.3f}"),
    # ("PS", "{:.1f}"),
    # ("FT", "{:7.4f}"),
    # ("FE", "{:.3f}"),
    # ("OB", "{:.6f}"),
    # ("OE", "{:.3f}"),
    ("EF", "{:18.15f}"),
    ("CF", "{:18.15f}"),
    ("HD", "{:18.15f}"),
    ("HM", "{:18.15f}"),
    ("PS", "{:18.15f}"),
    ("FT", "{:18.15f}"),
    ("FE", "{:18.15f}"),
    ("OB", "{:18.15f}"),
    ("OE", "{:18.15f}"),
]

# ------------------------------------------------------------------------------
# Build one add_case line from a CSV row
# The comma right after **kwargs has no trailing space, matching your example, the rest use ", ".

def format_case(row,member_num):
    parts = [f"{name}={fmt.format(float(row[name]))}" for name, fmt in FIELD_FORMATS]
    return f"add_case(**kwargs,member='{member_num:03d}'," + ", ".join(parts) + ")"


# --------------------------------------------------------------------------------------------------
# Main
# Reads the manifest and writes one add_case line per row. Defaults to stdout so you can copy it
# straight into your other script, or use -o to dump it to a file.

def main():
    parser = argparse.ArgumentParser(
        description="Emit add_case lines from the OA4 physics manifest.")
    parser.add_argument("csv_path", nargs="?", default="oa4_physics_manifest.csv",
                        help="Path to the manifest CSV (default: oa4_physics_manifest.csv)")
    parser.add_argument("-o", "--output",
                        help="Write lines to this file instead of stdout")
    parser.add_argument("--skip-control", action="store_true",
                        help="Skip rows whose row_type is CONTROL")
    parser.add_argument("--comment-id", action="store_true",
                        help="Append the row_id as a trailing comment on each line")
    args = parser.parse_args()

    lines = []
    member_num = 0
    with open(args.csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if args.skip_control and row.get("row_type", "").upper() == "CONTROL":
                continue
            line = format_case(row,member_num)
            if args.comment_id:
                line += f"  # {row['row_id']}"
            lines.append(line)
            member_num +=1

    text = "\n".join(lines) + "\n"
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print(f"Wrote {len(lines)} lines to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()