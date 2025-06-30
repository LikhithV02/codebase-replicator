import streamlit as st
import os
import base64
import io
from PIL import Image, ImageGrab
import time
from groq import Groq
from typing import List, Optional
import json

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    api_key = "your_groq_api_key"  # Replace with your actual Groq API key
    if not api_key:
        st.error("Please set GROQ_API_KEY environment variable")
        return None
    return Groq(api_key=api_key)

def encode_image_from_pil(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

def encode_image_from_file(image_path: str) -> str:
    """Encode image file to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def take_screenshot() -> Image.Image:
    """Take a screenshot of the entire screen"""
    screenshot = ImageGrab.grab()
    return screenshot

def analyze_screenshots_with_groq(client: Groq, screenshots: List[str], filename: str) -> str:
    """Send screenshots to Groq for code analysis"""
    
    # Prepare the content for the API call
    content = [
        {
            "type": "text",
            "text": f"""Please analyze these screenshots of code and reproduce the complete code as accurately as possible. 

File: {filename}

Instructions:
1. Look at all the screenshots carefully
2. Reconstruct the complete code from these images
3. Maintain proper indentation and formatting
4. Include all imports, functions, classes, and comments
5. If there are any parts that are unclear, make reasonable assumptions based on context
6. Return only the code without any additional explanations

The screenshots show different parts of the same file, so piece them together logically."""
        }
    ]
    
    # Add all screenshot images
    for screenshot_b64 in screenshots:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{screenshot_b64}"
            }
        })
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.1,  # Lower temperature for more consistent code reproduction
            max_completion_tokens=4096,  # Increased for longer code files
            top_p=0.9,
            stream=False,
            stop=None,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error calling Groq API: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Code Screenshot Replicator",
        page_icon="📸",
        layout="wide"
    )
    
    st.title("📸 Code Screenshot Replicator")
    st.markdown("Take screenshots of your code and use Groq AI to replicate it accurately")
    
    # Check if Groq client is available
    client = get_groq_client()
    if not client:
        st.stop()
    
    # Sidebar for configuration
    st.sidebar.header("Configuration")
    
    # Session state initialization
    if 'screenshots' not in st.session_state:
        st.session_state.screenshots = []
    if 'current_filename' not in st.session_state:
        st.session_state.current_filename = ""
    if 'generated_code' not in st.session_state:
        st.session_state.generated_code = {}
    
    # Add file upload option
    st.sidebar.subheader("Upload Screenshots")
    uploaded_files = st.sidebar.file_uploader(
        "Upload screenshot files", 
        type=['png', 'jpg', 'jpeg'], 
        accept_multiple_files=True,
        help="You can also upload existing screenshot files instead of taking new ones"
    )
    
    if uploaded_files and filename:
        if st.sidebar.button("Add Uploaded Images"):
            for uploaded_file in uploaded_files:
                if len(st.session_state.screenshots) < 5:
                    # Convert uploaded file to base64
                    image = Image.open(uploaded_file)
                    screenshot_b64 = encode_image_from_pil(image)
                    st.session_state.screenshots.append(screenshot_b64)
                else:
                    st.sidebar.warning("Maximum 5 screenshots allowed per batch")
                    break
            st.sidebar.success(f"Added {len(uploaded_files)} images")
            st.rerun()
    filename = st.sidebar.text_input("Current File Name", 
                                   value=st.session_state.current_filename,
                                   placeholder="e.g., main.py")
    
    if filename != st.session_state.current_filename:
        st.session_state.current_filename = filename
        st.session_state.screenshots = []  # Clear screenshots when changing files
    
    # Screenshot section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📷 Screenshot Capture")
        
        if st.button("Take Screenshot", type="primary", use_container_width=True):
            if not filename:
                st.error("Please enter a filename first")
            else:
                with st.spinner("Taking screenshot..."):
                    time.sleep(2)  # Give user time to switch windows
                    screenshot = take_screenshot()
                    screenshot_b64 = encode_image_from_pil(screenshot)
                    st.session_state.screenshots.append(screenshot_b64)
                    st.success(f"Screenshot {len(st.session_state.screenshots)} captured!")
        
        # Display current screenshots count
        st.info(f"Screenshots captured: {len(st.session_state.screenshots)}/5")
        
        # Show screenshots
        if st.session_state.screenshots:
            st.subheader("Captured Screenshots")
            for i, screenshot_b64 in enumerate(st.session_state.screenshots):
                with st.expander(f"Screenshot {i+1}"):
                    st.image(f"data:image/png;base64,{screenshot_b64}", caption=f"Screenshot {i+1}")
                    if st.button(f"Remove Screenshot {i+1}", key=f"remove_{i}"):
                        st.session_state.screenshots.pop(i)
                        st.rerun()
        
        # Clear all screenshots
        if st.session_state.screenshots:
            if st.button("Clear All Screenshots", type="secondary"):
                st.session_state.screenshots = []
                st.rerun()
    
    with col2:
        st.header("🤖 Code Generation")
        
        # Generate code button
        if st.button("Generate Code from Screenshots", 
                    type="primary", 
                    use_container_width=True,
                    disabled=len(st.session_state.screenshots) == 0 or not filename):
            
            if not st.session_state.screenshots:
                st.error("Please take at least one screenshot first")
            elif not filename:
                st.error("Please enter a filename")
            else:
                with st.spinner("Analyzing screenshots and generating code..."):
                    generated_code = analyze_screenshots_with_groq(
                        client, 
                        st.session_state.screenshots, 
                        filename
                    )
                    
                    if generated_code:
                        st.session_state.generated_code[filename] = generated_code
                        st.success("Code generated successfully!")
                    else:
                        st.error("Failed to generate code")
        
        # Display generated code
        if filename in st.session_state.generated_code:
            st.subheader(f"Generated Code for {filename}")
            code = st.session_state.generated_code[filename]
            
            # Code display with copy functionality
            st.code(code, language='python')
            
            # Download button
            st.download_button(
                label=f"Download {filename}",
                data=code,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
            
            # Edit code
            if st.checkbox("Edit Generated Code"):
                edited_code = st.text_area(
                    "Edit the code:",
                    value=code,
                    height=400,
                    key=f"edit_{filename}"
                )
                if st.button("Save Edited Code"):
                    st.session_state.generated_code[filename] = edited_code
                    st.success("Code updated!")
                    st.rerun()
    
    # Project overview
    st.header("📁 Project Overview")
    
    if st.session_state.generated_code:
        st.subheader("Generated Files")
        for file, code in st.session_state.generated_code.items():
            with st.expander(f"📄 {file}"):
                st.code(code, language='python')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label=f"Download {file}",
                        data=code,
                        file_name=file,
                        mime="text/plain",
                        key=f"download_{file}"
                    )
                with col2:
                    if st.button(f"Remove {file}", key=f"remove_file_{file}"):
                        del st.session_state.generated_code[file]
                        st.rerun()
        
        # Download all files as zip
        if len(st.session_state.generated_code) > 1:
            import zipfile
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for filename, code in st.session_state.generated_code.items():
                    zip_file.writestr(filename, code)
            
            st.download_button(
                label="📦 Download All Files as ZIP",
                data=zip_buffer.getvalue(),
                file_name="generated_code.zip",
                mime="application/zip",
                use_container_width=True
            )
    else:
        st.info("No files generated yet. Take screenshots and generate code to see them here.")
    
    # Instructions
    with st.expander("📋 Instructions"):
        st.markdown("""
        ### How to use this app:
        
        1. **Set up your environment:**
           - Make sure you have set the `GROQ_API_KEY` environment variable
           - Open the code file you want to replicate in your IDE/editor
        
        2. **For each file:**
           - Enter the filename (e.g., `main.py`, `utils.py`)
           - Position your code editor window so the code is visible
           - Click "Take Screenshot" - you have 2 seconds to switch to your code window
           - Scroll down in your code and take additional screenshots as needed
           - You can take up to 5 screenshots per batch (Groq's limit)
        
        3. **Generate code:**
           - Click "Generate Code from Screenshots"
           - The AI will analyze all screenshots and reconstruct the complete code
           - Review and edit the generated code if needed
           - Download the file
        
        4. **For large files:**
           - If your file is longer than 5 screenshots, generate code for the first batch
           - Clear screenshots and continue with the next part
           - Manually combine the generated code sections
        
        ### Tips:
        - Use a consistent font size in your editor for better OCR
        - Ensure good contrast between text and background
        - Include proper overlap between screenshots to avoid missing lines
        - The AI works best with Python code but can handle other languages too
        """)

if __name__ == "__main__":
    main()