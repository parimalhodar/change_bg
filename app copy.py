import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import io
import os
from streamlit_extras.add_vertical_space import add_vertical_space
import numpy as np

# Set page config with mobile-friendly layout
st.set_page_config(
    page_title="Background Remover & Replacer",
    page_icon="✂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🖼️ Remove & Replace Background")
st.markdown("Upload images to remove backgrounds and add new ones! Works best on PC and mobile.(by Parimal Hodar)")
st.divider()

# Background options
st.markdown("### Background Options")
bg_option = st.radio(
    "Choose background type:",
    ["Remove Only (Default)", "Solid Color", "Preset Backgrounds", "Custom Background"],
    horizontal=True,
    help="Select what type of background you want for your processed images"
)

# Background selection based on option
selected_background = None
background_color = None

if bg_option == "Solid Color":
    st.markdown("#### Select Color")
    color_option = st.selectbox(
        "Choose a color:",
        ["White", "Black", "Red", "Blue", "Green", "Yellow", "Purple", "Pink", "Custom"]
    )
    
    color_map = {
        "White": (255, 255, 255),
        "Black": (0, 0, 0),
        "Red": (255, 0, 0),
        "Blue": (0, 0, 255),
        "Green": (0, 255, 0),
        "Yellow": (255, 255, 0),
        "Purple": (128, 0, 128),
        "Pink": (255, 192, 203)
    }
    
    if color_option == "Custom":
        background_color = st.color_picker("Pick a custom color", "#FFFFFF")
        # Convert hex to RGB
        background_color = tuple(int(background_color[i:i+2], 16) for i in (1, 3, 5))
    else:
        background_color = color_map[color_option]

elif bg_option == "Preset Backgrounds":
    st.markdown("#### Select Preset Background")
    
    # Check if backgrounds folder exists
    bg_folder = "backgrounds"
    if os.path.exists(bg_folder):
        bg_files = [f for f in os.listdir(bg_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        if bg_files:
            # Display background options with thumbnails
            selected_bg_file = st.selectbox("Choose a background:", bg_files)
            
            if selected_bg_file:
                selected_background = Image.open(os.path.join(bg_folder, selected_bg_file))
                # Show preview
                st.image(selected_background, caption="Selected Background", width=200)
        else:
            st.warning("No background images found in backgrounds folder.")
            st.info("Please add some background images (.png, .jpg, .jpeg, .webp) to the 'backgrounds' folder.")
    else:
        st.warning("Backgrounds folder not found.")
        st.info("Please create a 'backgrounds' folder and add some background images.")
        
        # Fallback: Use online backgrounds
        st.markdown("**Using Online Backgrounds:**")
        online_bg_option = st.selectbox(
            "Choose an online background:",
            ["Gradient Blue", "Gradient Purple", "Gradient Green", "Abstract Pattern"]
        )
        
        # Create gradient backgrounds
        if online_bg_option == "Gradient Blue":
            selected_background = create_gradient_background((100, 150, 255), (200, 220, 255))
        elif online_bg_option == "Gradient Purple":
            selected_background = create_gradient_background((150, 100, 255), (220, 200, 255))
        elif online_bg_option == "Gradient Green":
            selected_background = create_gradient_background((100, 255, 150), (200, 255, 220))
        else:  # Abstract Pattern
            selected_background = create_pattern_background()

elif bg_option == "Custom Background":
    st.markdown("#### Upload Custom Background")
    custom_bg = st.file_uploader(
        "Choose a background image",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload your own background image"
    )
    
    if custom_bg:
        selected_background = Image.open(custom_bg)
        st.image(selected_background, caption="Custom Background", width=200)

# Function to create gradient background
def create_gradient_background(color1, color2, size=(800, 600)):
    img = Image.new('RGB', size, color1)
    draw = ImageDraw.Draw(img)
    
    for i in range(size[1]):
        ratio = i / size[1]
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, i), (size[0], i)], fill=(r, g, b))
    
    return img

# Function to create pattern background
def create_pattern_background(size=(800, 600)):
    img = Image.new('RGB', size, (240, 240, 250))
    draw = ImageDraw.Draw(img)
    
    # Create a simple pattern
    for x in range(0, size[0], 50):
        for y in range(0, size[1], 50):
            draw.ellipse([x, y, x+20, y+20], fill=(200, 200, 230))
    
    return img

# Function to replace background
def replace_background(original_img, background_removed_img, new_background=None, bg_color=None):
    if bg_color:
        # Create solid color background
        bg = Image.new('RGB', original_img.size, bg_color)
    elif new_background:
        # Resize background to match original image
        bg = new_background.resize(original_img.size, Image.Resampling.LANCZOS)
        if bg.mode != 'RGB':
            bg = bg.convert('RGB')
    else:
        # Return transparent background (original behavior)
        return background_removed_img
    
    # Convert background removed image to RGBA if not already
    if background_removed_img.mode != 'RGBA':
        background_removed_img = background_removed_img.convert('RGBA')
    
    # Composite the images
    result = Image.new('RGB', original_img.size, (255, 255, 255))
    result.paste(bg, (0, 0))
    result.paste(background_removed_img, (0, 0), background_removed_img)
    
    return result

st.divider()

# Move file uploader to main content
st.markdown("### Upload Images")
images = st.file_uploader(
    "Choose images",
    accept_multiple_files=True,
    type=['png', 'jpg', 'jpeg', 'webp'],
    help="Select one or more images to process."
)

# Add footer in sidebar
with st.sidebar:
    add_vertical_space(2)
    st.markdown("Made with ❤️ by [Parimal Hodar]")

if images:
    for idx, image in enumerate(images):
        try:
            with Image.open(image) as img:
                # Ensure image is in RGB mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                st.subheader(f"Image {idx + 1}")
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown("**Original**")
                    st.image(img, use_container_width=True)

                with st.spinner(f'Processing image {idx + 1}...'):
                    # Remove background
                    bg_removed = remove(img)
                
                # Handle output format
                if isinstance(bg_removed, Image.Image):
                    output_image = bg_removed
                else:
                    try:
                        output_image = Image.open(io.BytesIO(bg_removed))
                    except:
                        st.error(f"Failed to process image {idx + 1}")
                        continue
                
                # Apply background replacement if needed
                if bg_option != "Remove Only (Default)":
                    final_image = replace_background(img, output_image, selected_background, background_color)
                    output_format = "JPEG"
                    file_extension = "jpg"
                else:
                    final_image = output_image
                    output_format = "PNG"
                    file_extension = "png"
                
                with col2:
                    if bg_option == "Remove Only (Default)":
                        st.markdown("**Background Removed**")
                    else:
                        st.markdown("**With New Background**")
                    
                    st.image(final_image, use_container_width=True)
                    
                    # Create download button
                    output_stream = io.BytesIO()
                    if output_format == "PNG":
                        final_image.save(output_stream, format="PNG")
                        mime_type = "image/png"
                    else:
                        final_image.save(output_stream, format="JPEG", quality=95)
                        mime_type = "image/jpeg"
                    
                    output_stream.seek(0)
                    
                    # Generate filename based on background option
                    base_name = image.name.split('.')[0]
                    if bg_option == "Remove Only (Default)":
                        filename = f"no_bg_{base_name}.{file_extension}"
                    else:
                        bg_type = bg_option.lower().replace(" ", "_")
                        filename = f"{bg_type}_{base_name}.{file_extension}"
                    
                    st.download_button(
                        label=f"📥 Download Image {idx + 1}",
                        data=output_stream.getvalue(),
                        file_name=filename,
                        mime=mime_type,
                        key=f"download_{idx}"
                    )
                
        except Exception as e:
            st.error(f"Error processing image {idx + 1}: {str(e)}")
            st.error("Please try with a different image or contact support.")

else:
    st.info("👆 Upload some images to get started!")
