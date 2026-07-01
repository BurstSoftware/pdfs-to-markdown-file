import streamlit as st
import tempfile
import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

st.set_page_config(page_title="PDF → Markdown", layout="wide")
st.title("📄 PDF to Markdown Converter")
st.caption("Powered by Marker")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        pdf_path = tmp.name

    with st.spinner("Converting with Marker... (first run downloads models)"):
        try:
            converter = PdfConverter(artifact_dict=create_model_dict())
            rendered = converter(pdf_path)
            markdown_text, _, images = text_from_rendered(rendered)

            st.success("Conversion successful!")

            # === Preview ===
            with st.expander("Markdown Preview", expanded=True):
                st.markdown(markdown_text, unsafe_allow_html=True)

            # === Editable version (streamlit-ace) ===
            st.subheader("✏️ Edit Markdown")
            try:
                from streamlit_ace import st_ace
                edited_markdown = st_ace(
                    value=markdown_text,
                    language="markdown",
                    theme="monokai",
                    height=500,
                    key="editor"
                )
            except ImportError:
                edited_markdown = st.text_area(
                    "Markdown", value=markdown_text, height=500
                )

            # === Download ===
            st.download_button(
                label="⬇️ Download .md file",
                data=edited_markdown,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",
                mime="text/markdown",
                use_container_width=True
            )

            # === Show extracted images (if any) ===
            if images:
                st.subheader("🖼️ Extracted Images")
                cols = st.columns(3)
                for i, (name, img_bytes) in enumerate(images.items()):
                    with cols[i % 3]:
                        st.image(img_bytes, caption=name)

        except Exception as e:
            st.error(f"Conversion failed: {e}")
        finally:
            os.unlink(pdf_path)
