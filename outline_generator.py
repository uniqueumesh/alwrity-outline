import time
import os
import json

import google.generativeai as genai
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- Config Section ---
MODEL_NAME = "gemini-2.0-flash"
GENERATION_CONFIG = {
    "temperature": 0.6,
    "top_k": 1,
    "max_output_tokens": 1024
}


def main():
    set_page_config()
    custom_css()
    hide_elements()
    title_and_description()
    how_to_use_section()
    advanced_settings()
    input_section()
    help_faq_section()
    st.markdown('<div class="footer">Made with ❤️ by ALwrity | <a href="https://github.com/AJaySi/AI-Writer" style="color:#1976D2;">Support</a></div>', unsafe_allow_html=True)


def set_page_config():
    st.set_page_config(
        page_title="Alwrity - Content Outline Generator",
        layout="wide",
    )


def custom_css():
    st.markdown("""
        <style>
        html, body, [class*="css"]  {
            font-size: 16px;
        }
        @media (max-width: 600px) {
            html, body, [class*="css"]  {
                font-size: 14px !important;
            }
            .stButton > button, .stTextInput > div > input {
                font-size: 15px !important;
            }
        }
        .streamlit-expanderHeader {color: #fff !important; background: #111 !important; border-radius: 8px;}
        .streamlit-expanderContent {background: #111 !important;}
        div.stButton > button:first-child {
            background: #1565C0 !important;
            color: white !important;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        }
        .stAlert, .stError, .stWarning { color: #fff !important; background: #b71c1c !important; }
        </style>
    """, unsafe_allow_html=True)


def hide_elements():
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)


def title_and_description():
    st.title("🧕 Alwrity - AI Content Outline Generator")
    st.markdown("This app helps you create a comprehensive outline for your blog, article, essay, story, or any content type using AI technology. 🧠✨")


def how_to_use_section():
    with st.expander('How to Use', expanded=False):
        st.markdown('''<div style="background:#111;padding:1rem;border-radius:10px;margin-bottom:1.5rem;">
        <ol style="color:#fff;margin-left:1.2em;">
          <li>Enter your topic or main keywords below.<br>(Or click <b>Try Example</b> to see how it works!)</li>
          <li>Select your content type and number of headings/subheadings.</li>
          <li>Click <b>Generate Outline</b> to get your result.</li>
          <li>Copy and use your outline in your blog or article!</li>
        </ol>
        </div>''', unsafe_allow_html=True)


def advanced_settings():
    # Advanced Settings (API Key)
    with st.expander("Advanced Settings ⚙️", expanded=False):
        st.markdown('''If you have your own Gemini AI Key, you can enter it below. <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a>''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini AI Key (optional)", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")
        st.session_state["user_gemini_api_key"] = user_gemini_api_key


def input_section():
    with st.expander("**💡 PRO-TIP** - Better input yield, better results.", expanded=True):
        col1, space, col2 = st.columns([5, 0.1, 5])
        with col1:
            if 'example_clicked' not in st.session_state:
                st.session_state['example_clicked'] = False

            def fill_example():
                st.session_state['outline_title'] = "Free AI Writer"
                st.session_state['example_clicked'] = True

            st.text_input(
                '📝 Topic or Main Keywords',
                key='outline_title',
                help="Describe your content idea in a sentence or a few keywords. E.g., 'Free AI Writer'",
                placeholder="E.g., How to Boost Your Productivity with Simple Hacks",
                args=({'aria-label': 'Topic or Main Keywords'},)
            )
            st.button('✨ Try Example', on_click=fill_example, help="Click to auto-fill an example topic.")
            content_type = st.selectbox(
                "📄 Content Type",
                options=["Blog", "Article", "Essay", "Story", "Other"],
                help="Choose the type of content you want to outline."
            )
        with col2:
            num_headings = st.slider(
                "🔢 Number of Main Headings",
                min_value=1,
                max_value=10,
                value=5,
                help="How many main sections should your outline have?"
            )
            num_subheadings = st.slider(
                "🔸 Subheadings per Heading",
                min_value=1,
                max_value=5,
                value=3,
                help="How many subpoints under each main heading?"
            )
            outline_format = st.radio(
                "📝 Outline Format",
                options=["Numbered List", "Bulleted List"],
                index=0,
                help="Choose how you want your outline formatted.",
                horizontal=True
            )
        if st.button('🚀 Generate Outline', help="Click to generate your content outline."):
            outline_title = st.session_state.get('outline_title', '')
            if outline_title.strip():
                with st.spinner("Generating your outline..."):
                    content_outline = generate_outline(outline_title, content_type, num_headings, num_subheadings, st.session_state.get("user_gemini_api_key"), outline_format)
                    if content_outline:
                        st.success('Your outline is ready!')
                        st.subheader('📋 Your Content Outline:')
                        st.markdown(content_outline)
                        if st.download_button("📋 Copy Outline", content_outline, file_name="outline.txt", help="Download or copy your outline."):
                            st.toast("Outline copied to clipboard!", icon="✅")
                    else:
                        st.error("We couldn't generate your outline. Please try again or check your AI Key.")
            else:
                st.warning("Please enter a topic or keywords to get started.")


def help_faq_section():
    with st.expander('❓ Need Help?', expanded=False):
        st.markdown('''
        - <b>What is an AI Outline?</b> An AI-generated outline gives you a structured plan for your content, saving you time and boosting creativity.<br>
        - <b>Do I need an AI Key?</b> No, you can use the tool without one. Only add your key if you have issues or want to use your own quota.<br>
        - <b>Why do I see errors?</b> Make sure you entered a topic. If you see API errors, try adding your own Gemini AI Key.<br>
        - <b>Still stuck?</b> <a href="https://github.com/AJaySi/AI-Writer" target="_blank">See our support & documentation</a>
        ''', unsafe_allow_html=True)


def generate_outline(outline_title, content_type, num_headings, num_subheadings, user_gemini_api_key=None, outline_format="Numbered List"):
    """Generate a content outline using Gemini LLM."""
    format_instruction = "Use numbered lists for headings and subheadings." if outline_format == "Numbered List" else "Use bullet points for headings and subheadings."
    prompt = f"""
    As an expert and experienced content writer for various online platforms, I will provide you with my 'topic title'.
    You are tasked with outlining a {content_type} type of content. 
    Your goal is to provide a well-structured content outline, with {num_headings} headings and {num_subheadings} subheadings.

    Follow the guidelines below for writing the outline:

    1. Ensure the title is informative and engaging.
    2. Avoid using generic words or overused phrases.
    3. Provide {num_headings} main headings, each with {num_subheadings} subheadings.
    4. Consider key sections, subsections, and points to ensure a smooth flow of ideas.
    5. Use headings, subheadings, and bullet points for a clear and coherent outline.
    6. Proofread the outline to ensure it is well-written, error-free, and easy to follow.
    7. Do not explain what and why; just give the finest possible output.
    8. {format_instruction}

    Important: Please read the entire prompt before writing anything, and follow the instructions exactly as given.

    \n\nMy 'topic title' is: '{outline_title}'
    """
    return gemini_text_response(prompt, user_gemini_api_key)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    """Get response from Gemini LLM."""
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in Advanced Settings or set it in the environment.")
            return None
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
    model = genai.GenerativeModel(model_name=MODEL_NAME, generation_config=GENERATION_CONFIG)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as err:
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")


if __name__ == "__main__":
    main()

