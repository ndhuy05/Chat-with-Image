import streamlit as st
from transformers import BlipProcessor, BlipForQuestionAnswering
import torch
from PIL import Image
import io
import tempfile
from pathlib import Path

# 🎨 STREAMLIT PAGE CONFIG
st.set_page_config(
    page_title="🤖 Chat with Image - BLIP",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'image_loaded' not in st.session_state:
    st.session_state.image_loaded = False
if 'current_image' not in st.session_state:
    st.session_state.current_image = None

class ImageChatbot:
    def __init__(self, model_name, use_gpu=True):
        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForQuestionAnswering.from_pretrained(model_name)
        
        # Move to GPU if available and requested
        if torch.cuda.is_available() and use_gpu:
            self.model = self.model.cuda()
            self.device = "cuda"
        else:
            self.device = "cpu"
    
    def answer_question(self, image, question, max_tokens=50):
        """Answer question about the image"""
        try:
            # Process inputs
            inputs = self.processor(images=image, text=question, return_tensors="pt")
            
            # Move inputs to same device as model
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate answer
            with torch.no_grad():
                out = self.model.generate(**inputs, max_length=max_tokens)
            
            # Decode answer
            answer = self.processor.decode(out[0], skip_special_tokens=True)
            return answer
            
        except Exception as e:
            return f"Error: {e}"

def main():
    st.title("🤖 Chat with Image - BLIP")
    st.markdown("---")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        model = "Salesforce/blip-vqa-base"
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            max_tokens = st.slider("Max Tokens", 10, 100, 50)
            use_gpu = st.checkbox("Use GPU (if available)", value=True)
        
        # Initialize chatbot
        if st.session_state.chatbot is None:
            try:
                with st.spinner("🔄 Loading model..."):
                    st.session_state.chatbot = ImageChatbot(model, use_gpu)
                st.success(f"✅ Model loaded on {st.session_state.chatbot.device.upper()}!")
            except Exception as e:
                st.error(f"❌ Error initializing chatbot: {e}")
                return
        
        st.markdown("---")
        
        st.header("📸 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            help="Upload an image to chat about"
        )
        
        if uploaded_file:
            if st.button("🖼️ Load Image"):
                try:
                    st.session_state.current_image = Image.open(uploaded_file).convert("RGB")
                    st.session_state.image_loaded = True
                    st.success(f"✅ Image loaded: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"❌ Error loading image: {e}")
        
        st.markdown("---")
        st.header("📊 Status")
        if st.session_state.image_loaded:
            st.success("✅ Image loaded - Ready to chat!")
            if st.session_state.current_image:
                st.image(st.session_state.current_image, width=200, caption="Current Image")
        else:
            st.warning("⚠️ No image loaded - Please upload an image")
        
        # System info
        with st.expander("🖥️ System Info"):
            st.write(f"CUDA Available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                st.write(f"GPU: {torch.cuda.get_device_name(0)}")
        
        if st.button("�️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat")
        
        # Chat messages container
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if st.session_state.image_loaded:
            if prompt := st.chat_input("Ask me about the image..."):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate response
                with st.chat_message("assistant"):
                    with st.spinner("🤔 Analyzing image..."):
                        response = st.session_state.chatbot.answer_question(
                            st.session_state.current_image, 
                            prompt, 
                            max_tokens
                        )
                    st.markdown(response)
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            st.info("👆 Please upload and load an image first to start chatting!")
    
    with col2:
        st.header("📋 Instructions")
        
        with st.expander("🚀 How to use", expanded=True):
            st.markdown("""
            1. **Choose a BLIP model** in the sidebar
            2. **Upload an image** (PNG, JPG, JPEG, GIF, BMP)
            3. **Click 'Load Image'** to process it
            4. **Start asking questions** about your image!
            5. **View the conversation** in real-time
            """)
        
        with st.expander("💡 Tips for better results"):
            st.markdown("""
            - Upload clear, well-lit images
            - Ask specific questions about objects, colors, actions
            - Try different question types:
                - "What is in this image?"
                - "What color is the [object]?"
                - "How many [objects] are there?"
                - "What is the [object] doing?"
            - Use descriptive language
            """)
        
        with st.expander("📁 Supported Image Formats"):
            st.markdown("""
            - **PNG** (.png) - Best for graphics with transparency
            - **JPEG** (.jpg, .jpeg) - Best for photos
            - **GIF** (.gif) - Animated images (first frame used)
            - **BMP** (.bmp) - Bitmap images
            
            **Recommendations:**
            - Use high-resolution images for better accuracy
            - Ensure good lighting and contrast
            - Avoid blurry or heavily compressed images
            """)
        
        with st.expander("🎯 Image Analysis Capabilities"):
            st.markdown("""
            **BLIP can help you with:**
            - 🔍 Object identification
            - 🎨 Color recognition  
            - 🔢 Counting objects
            - 🏃 Action recognition
            - 📍 Scene description
            - 🌍 Location/setting identification
            - 🕐 Time of day estimation
            - 🌤️ Weather condition description
            """)
        
        if st.session_state.image_loaded:
            with st.expander("❓ Sample Questions", expanded=True):
                sample_questions = [
                    "What is the main object in this image?",
                    "What colors do you see?",
                    "How many objects are there?", 
                    "What is happening in this scene?",
                    "Where was this photo taken?",
                    "What time of day is it?",
                    "Describe this image in detail",
                    "What's the weather like in this image?"
                ]
                
                for question in sample_questions:
                    if st.button(question, key=f"sample_{question}", use_container_width=True):
                        # Add question to chat
                        st.session_state.messages.append({"role": "user", "content": question})
                        
                        # Generate response
                        response = st.session_state.chatbot.answer_question(
                            st.session_state.current_image, 
                            question, 
                            max_tokens
                        )
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
        
        # Model info
        with st.expander("🤖 About BLIP"):
            st.markdown("""
            **BLIP (Bootstrapping Language-Image Pre-training)**
            
            BLIP is a powerful AI model that can:
            - Understand and analyze images
            - Answer questions about visual content
            - Generate descriptive captions
            - Perform visual reasoning tasks
            
            **Model Options:**
            - `blip-vqa-base`: Faster, good accuracy
            - `blip-vqa-capfilt-large`: Slower, higher accuracy
            
            [Learn more about BLIP](https://github.com/salesforce/BLIP)
            """)

if __name__ == "__main__":
    main()
