import time
import os
import json

import google.generativeai as genai
import streamlit as st
from tenacity import retry, stop_after_attempt, wait_random_exponential


def main():
    # Set page configuration
    st.set_page_config(
        page_title="ALwrity - AI Blog Outline Generator",
        layout="wide",
    )
    # Custom CSS for theme
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
    # Hide top header line
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    # Hide footer
    st.markdown('<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>', unsafe_allow_html=True)

    # Tool title and description at the top
    st.markdown('<h1 style="display:flex;align-items:center;font-size:2.5rem;gap:0.5rem;">🧕 ALwrity Blog Outline Generator</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:#1976D2;font-size:1.2rem;margin-bottom:1.5rem;">Generate a high-quality, structured outline for your blog, article, or essay in seconds.</div>', unsafe_allow_html=True)

    # API Key Input Section
    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown('''If the default Gemini API key is unavailable or exceeds its limits, you can provide your own API key below.<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a>
        ''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini API Key", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")
        st.session_state["user_gemini_api_key"] = user_gemini_api_key

    input_section()

    # Help & Support Section
    with st.expander('❓ Help & Troubleshooting', expanded=False):
        st.markdown('''
        - **Not getting results?** Make sure you entered a title or keywords.
        - **API key issues?** Ensure your Gemini API key is set in your environment.
        - **Still stuck?** [See our support & documentation](https://github.com/AJaySi/AI-Writer)
        ''')

    st.markdown('<div class="footer">Made with ❤️ by ALwrity | <a href="https://github.com/AJaySi/AI-Writer" style="color:#1976D2;">Support</a></div>', unsafe_allow_html=True)


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
                    content_outline = generate_outline(outline_title, content_type, num_headings, num_subheadings, st.session_state.get("user_gemini_api_key"))
                    if content_outline:
                        st.subheader('**📋 Your Content Outline:**')
                        st.markdown(content_outline)
                        st.write("\n\n\n")
                    else:
                        st.error("💥 **Failed to generate outline. Please try again!**")
            else:
                st.error("🚫 **Input Title/Topic of content to outline is required!**")


def generate_outline(outline_title, content_type, num_headings, num_subheadings, user_gemini_api_key=None):
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

    return gemini_text_response(prompt, user_gemini_api_key)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def gemini_text_response(prompt, user_gemini_api_key=None):
    """ Common functiont to get response from gemini pro Text. """
    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in the sidebar or set it in the environment.")
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
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", generation_config=generation_config)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as err:
        st.error(f"Failed to get response from Gemini: {err}. Retrying.")


if __name__ == "__main__":
    main()

