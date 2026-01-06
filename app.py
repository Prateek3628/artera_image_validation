"""
Streamlit web application for image validation.

This app allows users to upload images and validate them based on:
- Face detection (must contain at least one human face)
- Blur detection (image must be sufficiently clear)
- Resolution requirements
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import json

from image_validation import validate_image, detect_faces, is_blurry


def main():
    # Page configuration
    st.set_page_config(
        page_title="Image Validator",
        page_icon="🔍",
        layout="wide"
    )
    
    # Title and description
    st.title("🔍 Image Validation App")
    st.markdown("""
    Upload an image to validate it based on:
    - **Face Detection**: Image must contain at least one human face
    - **Blur Detection**: Image must be sufficiently clear (not blurry)
    - **Resolution**: Image must meet minimum size requirements
    """)
    
    # Sidebar for configuration
    st.sidebar.header("⚙️ Validation Settings")
    
    min_width = st.sidebar.number_input(
        "Minimum Width (pixels)",
        min_value=100,
        max_value=2000,
        value=256,
        step=10,
        help="Minimum required image width"
    )
    
    min_height = st.sidebar.number_input(
        "Minimum Height (pixels)",
        min_value=100,
        max_value=2000,
        value=256,
        step=10,
        help="Minimum required image height"
    )
    
    blur_threshold = st.sidebar.slider(
        "Blur Threshold",
        min_value=50.0,
        max_value=500.0,
        value=100.0,
        step=10.0,
        help="Lower values = stricter blur detection. Images with blur score below this are considered blurry."
    )
    
    require_single_face = st.sidebar.checkbox(
        "Require Single Face",
        value=False,
        help="If checked, validation fails unless exactly one face is detected"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 💡 Tips
    - **Blur Score**: Higher is better (>100 is typically clear)
    - **Face Detection**: Works best with frontal faces
    - Supported formats: JPG, PNG, JPEG
    """)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose an image file",
        type=["jpg", "jpeg", "png"],
        help="Upload a JPG, JPEG, or PNG image"
    )
    
    if uploaded_file is not None:
        # Create two columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Image")
            
            # Display the uploaded image
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
            
            # Convert PIL Image to OpenCV format
            img_array = np.array(image)
            # Convert RGB to BGR for OpenCV
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_array
        
        with col2:
            st.subheader("✅ Validation Results")
            
            # Save uploaded file temporarily for validation
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Run validation
            with st.spinner("Validating image..."):
                result = validate_image(
                    temp_path,
                    min_width=min_width,
                    min_height=min_height,
                    blur_threshold=blur_threshold,
                    require_single_face=require_single_face
                )
            
            # Display validation status
            if result['valid']:
                st.success("✅ Image Validation PASSED", icon="✅")
            else:
                st.error("❌ Image Validation FAILED", icon="❌")
            
            # Display metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric(
                    "Faces Detected",
                    result['num_faces'],
                    delta="✓" if result['num_faces'] > 0 else "✗"
                )
            
            with metric_col2:
                blur_status = "Clear" if result['blur_score'] >= blur_threshold else "Blurry"
                st.metric(
                    "Blur Score",
                    f"{result['blur_score']:.1f}",
                    delta=blur_status
                )
            
            with metric_col3:
                st.metric(
                    "Resolution",
                    f"{result['width']}×{result['height']}"
                )
            
            # Display validation reasons if failed
            if not result['valid']:
                st.markdown("### ⚠️ Validation Issues:")
                for i, reason in enumerate(result['reasons'], 1):
                    st.warning(f"{i}. {reason}")
            
            # Show detailed results in expandable section
            with st.expander("📊 Detailed Analysis"):
                # Face detection details
                st.markdown("#### Face Detection")
                faces = detect_faces(img_cv)
                if faces:
                    st.success(f"✓ Found {len(faces)} face(s)")
                    for i, (x, y, w, h) in enumerate(faces, 1):
                        st.text(f"  Face {i}: Position ({x}, {y}), Size {w}×{h}")
                    
                    # Draw rectangles on image
                    img_with_faces = img_array.copy()
                    for (x, y, w, h) in faces:
                        cv2.rectangle(img_with_faces, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    st.image(img_with_faces, caption="Detected Faces", use_container_width=True)
                else:
                    st.error("✗ No faces detected")
                
                st.markdown("---")
                
                # Blur detection details
                st.markdown("#### Blur Analysis")
                blurry, blur_score = is_blurry(img_cv, threshold=blur_threshold)
                if blurry:
                    st.error(f"✗ Image is BLURRY (score: {blur_score:.2f})")
                else:
                    st.success(f"✓ Image is CLEAR (score: {blur_score:.2f})")
                
                st.caption(f"Threshold: {blur_threshold} (lower scores indicate more blur)")
                
                st.markdown("---")
                
                # Full JSON result
                st.markdown("#### JSON Response")
                st.json(result)
            
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    else:
        # Show placeholder when no image is uploaded
        st.info("👆 Upload an image to begin validation")
        
        # Example images section
        st.markdown("---")
        st.markdown("### 📝 What makes a valid image?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### ✅ Face Detection")
            st.markdown("- At least one human face visible")
            st.markdown("- Face should be frontal or near-frontal")
            st.markdown("- Face should be reasonably sized")
        
        with col2:
            st.markdown("#### ✅ Image Clarity")
            st.markdown("- Image should be in focus")
            st.markdown("- No motion blur")
            st.markdown("- Good lighting conditions")
        
        with col3:
            st.markdown("#### ✅ Resolution")
            st.markdown("- Meets minimum size requirements")
            st.markdown("- Default: 256×256 pixels")
            st.markdown("- Adjustable in settings")


if __name__ == "__main__":
    main()
