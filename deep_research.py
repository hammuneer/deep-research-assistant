"""
Streamlit entrypoint for the Deep Research app.

This script sets up the Streamlit UI, collects a research query from
the user, runs the asynchronous research process, and displays
status updates and the final report.
"""

import asyncio
import streamlit as st
from dotenv import load_dotenv

from research_manager import ResearchManager


# Load environment variables from .env (local dev convenience)
load_dotenv(override=True)

# Configure Streamlit page
st.set_page_config(
    page_title="Deep Research",
    page_icon="🔎",
    layout="wide",
)


# Sidebar info
with st.sidebar:
    st.markdown("## ⚙️ About Deep Research")
    st.write(
        """
        This tool runs **multi-step deep research** using AI:
        1. Plans multiple web searches 📝  
        2. Gathers diverse perspectives 🌐  
        3. Writes a **long-form research report** 📄  
        4. (Optional) Emails the report directly to you 📧  
        """
    )
    st.info("ℹ️ Enter a research topic below and let the agent do the heavy lifting!")


# Main header
st.markdown(
    """
    <h1 style="text-align:center;">🔎 Deep Research Assistant</h1>
    <p style="text-align:center; font-size:18px; color:gray;">
    Your personal AI-powered researcher.  
    Ask a question, and get a comprehensive report — complete with optional email delivery.  
    </p>
    """,
    unsafe_allow_html=True,
)


# Input field for the research query
query: str = st.text_area(
    "💡 What topic would you like to research?",
    placeholder="e.g. 'Latest advancements in renewable energy technologies 2025, send to myemail@example.com'",
    height=100,
)


# Handle Run button
if st.button("🚀 Run Deep Research", type="primary"):
    if not query.strip():
        st.warning("⚠️ Please enter a research topic.")
    else:
        research_manager = ResearchManager()

        async def process() -> str:
            """
            Run the research pipeline asynchronously.

            Returns:
                str: Concatenated markdown output from the research process.
            """
            output_chunks: list[str] = []

            status_placeholder = st.empty()  # live status updates

            async for chunk in research_manager.run(query):
                if "..." in chunk:  # heuristic: status update
                    status_placeholder.info(f"⏳ {chunk}")
                output_chunks.append(chunk)

            status_placeholder.success("✅ Research complete!")

            return "\n\n".join(output_chunks)

        # Run the async process
        with st.spinner("🤖 Running deep research... this may take a while."):
            result: str = asyncio.run(process())

        # Render result
        st.markdown("## 📊 Research Report")
        st.markdown(result, unsafe_allow_html=True)
