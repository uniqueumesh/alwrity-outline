import time
import os
import json

import google.generativeai as genai
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential


def main():
    set_page_config()
    custom_css()
    hide_elements()
    title_and_description()
    advanced_settings()
    input_section()


def set_page_config():
    st.set_page_config(
        page_title="Alwrity - Content Outline Generator",
        layout="wide",
    )


def custom_css():
    st.markdown("""
        <style>
                ::-webkit-scrollbar-track {
        background: #e1ebf9;
        }

        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9;
            border-radius: 10px;
            border: 3px solid #e1ebf9;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #64B5F6;
        }

        ::-webkit-scrollbar {
            width: 16px;
        }
        div.stButton > button:first-child {
            background: #1565C0;
            color: white;
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
            outline_title = st.text_input(
                '**Enter Title of your content or main keywords:**',
                help="🔍 Describe the idea of the whole content in a single sentence. Keep it between 1-3 sentences.",
                placeholder="E.g., How to Boost Your Productivity with Simple Hacks"
            )

            content_type = st.selectbox(
                "**Select the type of content:**",
                options=["Blog", "Article", "Essay", "Story", "Other"],
                help="📝 Choose the type of content you want to create an outline for."
            )
        with col2:
            num_headings = st.slider(
                "**Number of main headings:**",
                min_value=1,
                max_value=10,
                value=5,
                help="📌 Choose the number of main headings for the outline."
            )

            num_subheadings = st.slider(
                "**Number of subheadings per heading:**",
                min_value=1,
                max_value=5,
                value=3,
                help="📋 Choose the number of subheadings under each main heading."
            )

        if st.button('**✍️ Get AI Outline**'):
            if outline_title.strip():
                with st.spinner("⏳ Hang On, Generating Outline..."):
                    content_outline = generate_outline(outline_title, content_type, num_headings, num_subheadings)
                    if content_outline:
                        st.subheader('**📋 Your Content Outline:**')
                        st.markdown(content_outline)
                        st.write("\n\n\n")
                    else:
                        st.error("💥 **Failed to generate outline. Please try again!**")
            else:
                st.error("🚫 **Input Title/Topic of content to outline is required!**")


def generate_outline(outline_title, content_type, num_headings, num_subheadings):
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

    Important: Please read the entire prompt before writing anything, and follow the instructions exactly as given.

    \n\nMy 'topic title' is: '{outline_title}'
    """

    return gemini_text_response(prompt, st.session_state.get("user_gemini_api_key"))


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    """ Common functiont to get response from gemini pro Text. """
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in Advanced Settings or set it in the environment.")
            return None
        genai.configure(api_key=api_key)
    except Exception as err:
        st.error(f"Failed to configure Gemini: {err}")
    # Set up the model
    generation_config = {
        "temperature": 0.6,
        "top_k": 1,
        "max_output_tokens": 1024
    }
    # FIXME: Expose model_name in main_config
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as err:
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")


if __name__ == "__main__":
    main()

