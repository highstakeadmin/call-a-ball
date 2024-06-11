import argparse


def main():
    """
    Main function for running the script from the console
    Input arguments:
    1. <image_file> - format = .png or .jpeg
    2. <json_file_format>
    """

    # Parsing data from console
    parser = argparse.ArgumentParser(description="Detected balls")
    parser.add_argument("image_file", type=str,
                        help="Input image file for scan: \
                        *.jpeg | *.png")

    args = parser.parse_args()

    print(args.image_file)


if __name__ == "__main__":
    main()
