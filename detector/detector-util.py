import argparse
import sys
import cv2 as cv


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

    # Read image file (OpenCV)
    # [image].png -> img: open_cv
    img = cv.imread(cv.samples.findFile(args.image_file))

    # Checking the image for read
    if img is None:
        sys.exit("Could not read the image.")

    print(type(img))


if __name__ == "__main__":
    main()
