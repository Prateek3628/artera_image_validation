#!/usr/bin/env python3
"""
Test script to validate an image using the image_validation module.

This script demonstrates how to use the validation functions.
Place an image file (e.g., input.jpg, input.png) in the same directory
and run this script to validate it.
"""

import json
from image_validation import validate_image, detect_faces, is_blurry
import cv2


def main():
    # Path to the image file (you can change this)
    image_path = 'image.png'
    
    print("=" * 60)
    print("IMAGE VALIDATION TEST")
    print("=" * 60)
    print(f"\nValidating image: {image_path}\n")
    
    # Method 1: Use the comprehensive validation function
    print("Running comprehensive validation...")
    print("-" * 60)
    result = validate_image(
        image_path, 
        blur_threshold=200.0,
        min_width=256,
        min_height=256,
        require_single_face=False
    )
    
    # Display results in a formatted way
    print(f"\nValidation Result: {'✓ VALID' if result['valid'] else '✗ INVALID'}")
    print(f"Image dimensions: {result['width']}x{result['height']} pixels")
    print(f"Faces detected: {result['num_faces']}")
    print(f"Blur score: {result['blur_score']:.2f}")
    
    if not result['valid']:
        print("\nValidation failed for the following reasons:")
        for i, reason in enumerate(result['reasons'], 1):
            print(f"  {i}. {reason}")
    else:
        print("\n✓ Image passed all validation checks!")
    
    print("\n" + "=" * 60)
    print("DETAILED ANALYSIS")
    print("=" * 60)
    
    # Method 2: Use individual functions for more detailed analysis
    try:
        img = cv2.imread(image_path)
        if img is not None:
            print("\nFace Detection:")
            print("-" * 60)
            faces = detect_faces(img)
            if faces:
                print(f"Found {len(faces)} face(s):")
                for i, (x, y, w, h) in enumerate(faces, 1):
                    print(f"  Face {i}: position=({x}, {y}), size={w}x{h}")
            else:
                print("No faces detected.")
            
            print("\nBlur Analysis:")
            print("-" * 60)
            blurry, blur_score = is_blurry(img, threshold=200.0)
            print(f"Blur score: {blur_score:.2f}")
            print(f"Status: {'BLURRY ✗' if blurry else 'CLEAR ✓'}")
            print(f"(Threshold: 100.0 - lower scores indicate more blur)")
    except Exception as e:
        print(f"\nError during detailed analysis: {e}")
    
    # Print full JSON result
    print("\n" + "=" * 60)
    print("FULL JSON RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2))
    print()


if __name__ == '__main__':
    main()
