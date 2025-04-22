#!/usr/bin/env python3
import argparse
import json
import os

from src.membrane_image_analysis import detect_colored_circles, track_circles_over_time

def write_markdown_table(records, output_path):
    header = "| image | circle_id |   x  |   y  | radius | color  |\n"
    sep    = "|:-----:|:---------:|:----:|:----:|:------:|:-------|\n"
    lines = [header, sep]
    for rec in records:
        lines.append(f"|  {rec['image']}    |     {rec['circle_id']}     |"
                     f"  {rec['x']} |  {rec['y']} |   {rec['radius']}   | {rec['color']}   |\n")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Tracking table written to {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Detect and/or track colored circles on a membrane."
    )
    parser.add_argument(
        "images", nargs="+",
        help="Path(s) to input image(s). For tracking, provide multiple frames."
    )
    parser.add_argument(
        "--track", action="store_true",
        help="Track circles over time across multiple images."
    )
    parser.add_argument(
        "--output-table", action="store_true",
        help="If tracking, also write the results to examples/tracking_table.md"
    )

    args = parser.parse_args()

    if args.track:
        result = track_circles_over_time(args.images)
        print(json.dumps(result["table"], indent=2))

        if args.output_table:
            write_markdown_table(result["table"], os.path.join("examples", "tracking_table.md"))
    else:
        for img_path in args.images:
            circles = detect_colored_circles(img_path)
            print(f"Results for {img_path}:")
            print(json.dumps(circles, indent=2))

if __name__ == "__main__":
    main()
