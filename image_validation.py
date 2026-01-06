"""
Image validation module for checking face presence and image clarity.

This module provides functions to:
1. Detect human faces in images using OpenCV's Haar cascade classifier
2. Assess image blur using Laplacian variance
3. Validate images based on multiple criteria (resolution, face presence, clarity)
"""

import os
from typing import List, Tuple, Dict

import cv2
import numpy as np


def detect_faces(image: np.ndarray) -> List[Tuple[int, int, int, int]]:
    """
    Detect human faces in an image using Haar cascade classifier.
    
    Args:
        image: BGR image loaded with OpenCV (numpy array).
    
    Returns:
        List of bounding boxes for detected faces, where each box is 
        represented as a tuple (x, y, w, h):
        - x: left coordinate
        - y: top coordinate
        - w: width
        - h: height
        Returns an empty list if no faces are detected.
    
    Example:
        >>> img = cv2.imread('photo.jpg')
        >>> faces = detect_faces(img)
        >>> print(f"Found {len(faces)} face(s)")
    """
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load the Haar cascade classifier for frontal face detection
    # This uses OpenCV's built-in cascade file
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    # Detect faces in the image
    # Parameters tuned for good balance between detection and false positives
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,      # Image pyramid scale reduction
        minNeighbors=5,       # Minimum neighbors for a detection to be kept
        minSize=(30, 30),     # Minimum face size
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Convert numpy array to list of tuples
    return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]


def is_blurry(image: np.ndarray, threshold: float = 200.0) -> Tuple[bool, float]:
    """
    Determine if an image is blurry using the variance of the Laplacian method.
    
    This method applies the Laplacian operator to the grayscale image and 
    computes its variance. A lower variance indicates less edge content, 
    which typically means the image is blurry.
    
    Args:
        image: BGR image loaded with OpenCV (numpy array).
        threshold: Focus measure threshold. Values below this threshold 
                  indicate a blurry image. Default is 100.0.
    
    Returns:
        A tuple containing:
        - bool: True if the image is blurry (focus measure < threshold), 
                False otherwise
        - float: The computed focus measure (variance of Laplacian)
    
    Example:
        >>> img = cv2.imread('photo.jpg')
        >>> blurry, score = is_blurry(img, threshold=100.0)
        >>> print(f"Blur score: {score:.2f}, Blurry: {blurry}")
    
    References:
        - Pech-Pacheco et al. "Diatom autofocusing in brightfield microscopy: 
          a comparative study." ICPR 2000.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Compute the Laplacian of the image and then the variance
    # The Laplacian highlights regions of rapid intensity change (edges)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    focus_measure = laplacian.var()
    
    # Return whether the image is blurry and the focus measure
    return (focus_measure < threshold, float(focus_measure))


def validate_image(
    path: str,
    min_width: int = 256,
    min_height: int = 256,
    blur_threshold: float = 200.0,
    require_single_face: bool = False
) -> Dict:
    """
    Validate an image based on multiple criteria.
    
    Performs comprehensive validation including:
    - File existence and readability
    - Minimum resolution requirements
    - Face detection (at least one face required)
    - Optional single face requirement
    - Blur detection
    
    Args:
        path: Path to the image file.
        min_width: Minimum required image width in pixels. Default is 256.
        min_height: Minimum required image height in pixels. Default is 256.
        blur_threshold: Threshold for blur detection. Images with focus 
                       measure below this are considered blurry. Default is 100.0.
        require_single_face: If True, validation fails unless exactly one 
                            face is detected. Default is False.
    
    Returns:
        A JSON-serializable dictionary containing:
        - valid (bool): True if all validation checks pass, False otherwise
        - reasons (List[str]): List of validation failure reasons (empty if valid)
        - num_faces (int): Number of faces detected (0 if image couldn't be loaded)
        - blur_score (float): Focus measure score (0.0 if image couldn't be loaded)
        - width (int): Image width in pixels (0 if image couldn't be loaded)
        - height (int): Image height in pixels (0 if image couldn't be loaded)
    
    Example:
        >>> result = validate_image('photo.jpg', blur_threshold=100.0)
        >>> if result['valid']:
        ...     print("Image is valid!")
        ... else:
        ...     print(f"Validation failed: {', '.join(result['reasons'])}")
        >>> print(f"Detected {result['num_faces']} face(s)")
        >>> print(f"Blur score: {result['blur_score']:.2f}")
    """
    # Initialize result dictionary with default values
    result: Dict = {
        'valid': False,
        'reasons': [],
        'num_faces': 0,
        'blur_score': 0.0,
        'width': 0,
        'height': 0
    }
    
    # Check if file exists
    if not os.path.exists(path):
        result['reasons'].append(f"File does not exist: {path}")
        return result
    
    # Try to load the image
    image = cv2.imread(path)
    if image is None:
        result['reasons'].append(f"Unable to read image file: {path}")
        return result
    
    # Get image dimensions
    height, width = image.shape[:2]
    result['width'] = width
    result['height'] = height
    
    # Check minimum resolution
    if width < min_width or height < min_height:
        result['reasons'].append(
            f"Image resolution ({width}x{height}) is below minimum "
            f"required ({min_width}x{min_height})"
        )
    
    # Detect faces
    faces = detect_faces(image)
    num_faces = len(faces)
    result['num_faces'] = num_faces
    
    # Check face requirements
    if num_faces == 0:
        result['reasons'].append("No human faces detected in the image")
    elif require_single_face and num_faces != 1:
        result['reasons'].append(
            f"Expected exactly 1 face, but found {num_faces} face(s)"
        )
    
    # Check for blur
    blurry, blur_score = is_blurry(image, threshold=blur_threshold)
    result['blur_score'] = blur_score
    
    if blurry:
        result['reasons'].append(
            f"Image is too blurry (blur score: {blur_score:.2f}, "
            f"threshold: {blur_threshold:.2f})"
        )
    
    # Image is valid only if there are no validation failures
    result['valid'] = len(result['reasons']) == 0
    
    return result
