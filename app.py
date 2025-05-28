import os
import tempfile
import streamlit as st
from PIL import Image # If used directly, otherwise remove
import streamlit.components.v1 as components # If used directly, otherwise remove
from datetime import datetime # For timestamp in filenames
import json # For CSS if loaded from JSON, or for debugging

# Import from your new modules
from utils import load_config, export_to_word, export_to_pdf, remove_problematic_chars
from document_processing import process_rfp
from knowledge_base import ProposalKnowledgeBase #, HierarchicalEmbeddingModel (if instantiated directly here)
from generation_engine import EnhancedProposalGenerator, SpecialistRAGDrafter

# Potentially other UI specific imports like pandas, matplotlib, plotly if visualizations are generated directly in app.py
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter


# Main Streamlit UI
def main():
    st.set_page_config(page_title="AI Proposal & RFP Generator", layout="wide", page_icon="📄")

    # Apply custom CSS
    st.markdown("""
    <style>
    .st-emotion-cache-1cngmya {
  font-family: sans-serif;
}
.st-ca {
  background-color: transparent;
}
.custom-header {
  margin: 0 0 10px;
  text-align: center;
}
.custom-header h5 {
  color: #636363;
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 30px;
  background-color: transparent;
  padding: 0;
}

.custom-header h5 strong {
  color: #111;
}

.st-emotion-cache-zy6yx3 {
  background-color: #fff !important;
}
.st-be {
  background: transparent;
  padding: 5px 10px;
  border-radius: 25px;
  color: #111 !important;
}
.st-ar button {
  color: #111;
  padding: 5px 10px;
  border-radius: 25px;
}
.st-ar button p {
  font-size: 16px !important;
  font-weight: 500;
}
.stHorizontalBlock {
  flex-flow: column;
  justify-content: center;
  align-items: center;
}

.st-bn:hover,
.st-bd {
  color: #111;
  background-color: #fff !important;
}
.st-bn:hover {
  color: #111;
}
.st-emotion-cache-1weic72 {
  flex-direction: row;
  -webkit-box-align: center;
  align-items: center;
  justify-content: center;
  color: #111;
}
.st-emotion-cache-c8ta4l {
  color: #111;
  margin: 0 0 10px;
}
.st-emotion-cache-1erivf3 {
  flex-flow: column;
  align-items: center;
  padding: 0;
  background-color: transparent;
  border-radius: 0;
  color: #111;
  justify-content: center;
  align-items: center;
}
.st-emotion-cache-u8hs99 {
  align-items: center;
  display: flex;
  justify-content: center;
  margin: 0;
  flex-wrap: wrap;
  flex-flow: column;
  text-align: center;
}

.stFileUploader {
  display: flex;
  flex-flow: column;
  min-width: 455px;
  max-width: 100%;
  height: auto;
  justify-content: center;
  align-items: center;
  text-align: center;
  border-radius: 20px;
  padding: 2rem;
  border: 1px dashed #b1b1b1 !important;
  background: linear-gradient(
      180deg,
      rgba(147, 84, 255, 0) 0%,
      rgba(147, 84, 255, 0.15) 100%
    ),
    #fff !important;
  box-shadow: -44px 139px 41px 0px rgba(0, 0, 0, 0),
    -28px 89px 37px 0px rgba(0, 0, 0, 0),
    -16px 50px 31px 0px rgba(0, 0, 0, 0.02),
    -7px 22px 23px 0px rgba(0, 0, 0, 0.03),
    -2px 6px 13px 0px rgba(0, 0, 0, 0.03) !important;
}
.stButton > button,
.st-emotion-cache-ktz07o {
  color: #fff;
  border-radius: 12px;
  background: #9354ff;
  border: 1px solid #9354ff;
  box-shadow: 0px 4px 7.3px 0px rgba(0, 0, 0, 0.15),
    0px -3.2px 12.1px 0px rgba(0, 0, 0, 0.15) inset,
    0px 5.2px 13px 0px rgba(255, 255, 255, 0.39) inset;
}
.st-emotion-cache-ktz07o:active,
.st-emotion-cache-ktz07o:focus:not(:active),
.st-emotion-cache-ktz07o:hover {
  background: transparent;
  color: #9354ff;
  border: 1px solid #9354ff;
}
.st-emotion-cache-8atqhb {
  display: flex;
  justify-content: center;
}
.st-emotion-cache-1l4firl {
  color: #111;
}
/* .stAlert .stAlertContainer {
  border-radius: 20px;
  border: 1px solid #e2e2e2;
  background: #fff;
  box-shadow: -32px 30px 12px 0px rgba(0, 0, 0, 0),
    -21px 19px 11px 0px rgba(0, 0, 0, 0),
    -12px 11px 10px 0px rgba(0, 0, 0, 0.02),
    -5px 5px 7px 0px rgba(0, 0, 0, 0.03), -1px 1px 4px 0px rgba(0, 0, 0, 0.03);
  color: #111;
} */
.stTextArea st-de {
  border: 0;
  color: #111;
  border-radius: 8px;
  background: #f7f7f7;
}
.st-emotion-cache-qoz3f2.erovr380 {
  color: #000;
  font-size: 16px;
  font-weight: 500;
  line-height: normal;
}
.st-emotion-cache-x2by6s {
  width: calc(60% - 1rem);
  flex: 1 1 calc(60% - 1rem);
}
.st-emotion-cache-seewz2,
.st-emotion-cache-seewz2 li {
  color: #111 !important;
}
.stButton.st-emotion-cache-8atqhb.e1mlolmg0 {
  background-color: transparent;
  padding: 0;
  box-shadow: none;
  margin: 0;
}
body,
.stApp {
  background: #fff;
}
.st-dz,
.st-emotion-cache-pro1il,
.st-emotion-cache-vewp9z,
.st-emotion-cache-vewp9z h1, .st-emotion-cache-vewp9z h2, .st-emotion-cache-vewp9z h3, .st-emotion-cache-vewp9z h4, .st-emotion-cache-vewp9z h5, .st-emotion-cache-vewp9z h6,
.st-emotion-cache-vewp9z p,
p,
body,
.stApp {
  font-family: sans-serif!important;
}

.st-emotion-cache-vewp9z.erovr380 ol {
  display: inline-block;
  font-family: sans-serif;
}
.st-dv {
  background: #F7F7F7;
}

.stApp header {
  background-color: #fff;
}
.stApp header,
.stApp h1,
.stApp h2,
.stApp h3 {
  font-weight: 700;
  color: #18181b;
}

/* Component styles */
.st-emotion-cache-8atqhb {
  margin: 0;
  padding: 0;
  background: transparent;
  box-shadow: none;
}

.st-ae > div {
  text-align: center;
}

.stMarkdown[data-testid="stMarkdown"] {
  background-color: #fff;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  margin-bottom: 0;
}

.st-ar {
  justify-content: center;
  color: #111;
  border-radius: 140px;
  background: #f1f1f1;
  display: inline-flex;
  padding: 5px;
  align-items: center;
  margin: 0 auto;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.st-ar .st-c2 {
  display: none !important;
}

.st-bd {
  color: #111 !important;
}

.stHeading {
  text-align: center;
}

/* Input component styles */
.stFileUploader,
.stButton,
.stTextInput,
.stMarkdown,
.stDataFrame,
.stSelectbox,
.stTextArea {
  border-radius: 18px !important;
  box-shadow: 0 2px 16px 0 rgba(0, 0, 0, 0.04);
  background: #fff;
  padding: 1.5rem 1.5rem;
  margin-bottom: 1.5rem;
}


.stButton > button ,
button.st-emotion-cache-ag3azy.eacrzsi2 {
  border-radius: 12px;
  background: #9354FF;
  box-shadow: 0px 4px 7.3px 0px rgba(0, 0, 0, 0.15), 0px -3.2px 12.1px 0px rgba(0, 0, 0, 0.15) inset, 0px 5.2px 13px 0px rgba(255, 255, 255, 0.39) inset;
  color: #fff;
}
.stButton > button:hover,
button.st-emotion-cache-ag3azy.eacrzsi2:hover {
  background: transparent;
  color: #9354FF;
  border: 1px solid #9354FF;
}

.custom-header {
  margin: 0 0 10px;
  text-align: center;
}

.custom-header h5 {
  color: #636363;
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 30px;
  background-color: transparent;
  padding: 0;
}

.custom-header h5 strong {
  color: #111;
}

.info-box {
  background-color: #fff;
  padding: 0;
  border-radius: 0;
  margin-bottom: 0;
  box-shadow: none;
}
.st-emotion-cache-seewz2 li {
  color: #111 !important;
}

.section-card {
  background-color: white;
  padding: 20px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}


.sidebar-content {
  background-color: white;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 15px;
}
.st-emotion-cache-bvonac {
  padding: 0;
  background-color: transparent;
  border-radius: 0.5rem;
  color: rgb(24, 24, 27);
  flex-flow: column;
}
.st-emotion-cache-2ti0tp {
  margin: 0 0 1rem;
}
.st-emotion-cache-fis6aj {
  white-space: normal;
  word-wrap: break-word;
  overflow-wrap: break-word;
  width: 100%;
}
.st-emotion-cache-1nb7gun {
  justify-content: center;
  margin: 0 0 1rem;
}
.st-emotion-cache-j78z8c {
  justify-content: center;
}
.st-emotion-cache-x2by6s .st-emotion-cache-13o7eu2.e1lln2w84[data-testid="stVerticalBlockBorderWrapper"] .stVerticalBlock.st-emotion-cache-vlxhtx.e1lln2w83[data-testid="stVerticalBlock"] {
  border-radius: 20px;
  border: 1px solid #E2E2E2;
  background: #FFF;
  box-shadow: -32px 30px 12px 0px rgba(0, 0, 0, 0.00), -21px 19px 11px 0px rgba(0, 0, 0, 0.00), -12px 11px 10px 0px rgba(0, 0, 0, 0.02), -5px 5px 7px 0px rgba(0, 0, 0, 0.03), -1px 1px 4px 0px rgba(0, 0, 0, 0.03);
  text-align: left;
  padding: 1rem 2rem;
}
.st-emotion-cache-vewp9z h1 {
  font-size: 2rem;
}

.st-emotion-cache-vewp9z h2 {
  font-size: 1.6rem;
}
s
.t-emotion-cache-1mwoiw6 {
  width: calc(60% - 1rem);
  flex: 1 1 calc(60% - 1rem);
  border-radius: 20px;
  border: 1px solid #E2E2E2;
  background: #FFF;
  box-shadow: -32px 30px 12px 0px rgba(0, 0, 0, 0.00), -21px 19px 11px 0px rgba(0, 0, 0, 0.00), -12px 11px 10px 0px rgba(0, 0, 0, 0.02), -5px 5px 7px 0px rgba(0, 0, 0, 0.03), -1px 1px 4px 0px rgba(0, 0, 0, 0.03);
  text-align: left;
  padding: 1rem 2rem;
}
/* .st-emotion-cache-17lr0tt .stMarkdown[data-testid="stMarkdown"]{
  border-radius: 20px;
  border: 1px solid #E2E2E2;
  background: #FFF;
  box-shadow: -32px 30px 12px 0px rgba(0, 0, 0, 0.00), -21px 19px 11px 0px rgba(0, 0, 0, 0.00), -12px 11px 10px 0px rgba(0, 0, 0, 0.02), -5px 5px 7px 0px rgba(0, 0, 0, 0.03), -1px 1px 4px 0px rgba(0, 0, 0, 0.03);
  padding: 2rem;
  text-align: left;
} */
.st-cb[aria-labelledby="tabs-bui3-tab-9"] ,
div#tabs-bui3-tabpanel-9 {
  width: calc(60% - 1rem);
  flex: 1 1 calc(60% - 1rem);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: auto;
  text-align: left;
}
.st-cb[aria-labelledby="tabs-bui3-tab-0"] ,
div#tabs-bui3-tabpanel-0 {
  text-align: left;
}

div#tabs-bui2-tabpanel-5 .st-emotion-cache-13o7eu2.e1lln2w84,
div#tabs-bui2-tabpanel-4 .st-emotion-cache-vewp9z.erovr380,
div#tabs-bui2-tabpanel-2 .st-ae [data-baseweb="tab-panel"] .st-emotion-cache-13o7eu2.e1lln2w84 .stMarkdown[data-testid="stMarkdown"] .st-emotion-cache-vewp9z.erovr380 {
  width: calc(60% - 1rem);
  text-align: left;
  align-items: center;
  margin: auto;
}
.st-emotion-cache-1mwoiw6 {
  width: calc(33.3333% - 1rem);
  flex: 1 1 calc(33.3333% - 1rem);
  width: calc(40% - 1rem);
  flex: 1 1 calc(40% - 1rem);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: auto;
  text-align: left;
  border: 1px solid #E2E2E2;
  background: #FFF;
  box-shadow: -32px 30px 12px 0px rgba(0, 0, 0, 0.00), -21px 19px 11px 0px rgba(0, 0, 0, 0.00), -12px 11px 10px 0px rgba(0, 0, 0, 0.02), -5px 5px 7px 0px rgba(0, 0, 0, 0.03), -1px 1px 4px 0px rgba(0, 0, 0, 0.03);
  text-align: left;
  padding: 1rem 2rem;
  border-radius: 15px;
}
div#tabs-bui2-tabpanel-2 .st-ar {
  padding: 15px 1rem;
  max-width: 75%;
}
@media (max-width: 768px) {
  .st-emotion-cache-1mwoiw6 ,
  div#tabs-bui2-tabpanel-5 .st-emotion-cache-13o7eu2.e1lln2w84,
  div#tabs-bui2-tabpanel-4 .st-emotion-cache-vewp9z.erovr380,
  div#tabs-bui2-tabpanel-2 .st-ae [data-baseweb="tab-panel"] .st-emotion-cache-13o7eu2.e1lln2w84 .stMarkdown[data-testid="stMarkdown"] .st-emotion-cache-vewp9z.erovr380 ,
  .st-cb[aria-labelledby="tabs-bui3-tab-9"] , s
  .st-cb[aria-labelledby="tabs-bui3-tab-0"] 
  .st-emotion-cache-x2by6s ,
  .st-emotion-cache-1mwoiw6,
  div#tabs-bui3-tabpanel-9  {
    width: 100%;
  flex: 1 1 100%;
  }
  .st-emotion-cache-vewp9z h1 {
    font-size: 1.5rem
}
.st-ar {border-radius: 10px;}
.st-emotion-cache-vewp9z h2 {
  font-size: 1.2rem
}
div#tabs-bui2-tabpanel-2 .st-ar,
.stFileUploader {
  min-width: 100%;
  max-width: 100%;
}
.st-emotion-cache-nvtlpw .e16xj5sw0 {
  align-items: center;
}
.st-ar {width: 100%;}

}

/* Fix for invisible text and black input fields */

/* Ensure all text has good contrast */
body, p, h1, h2, h3, h4, h5, h6, span, div, input, textarea, button, select, label {
  color: #333 !important;
}

/* Fix input fields that appear black */
input, textarea, select, .st-dv {
  background-color: #FFFFFF !important;
  border: 1px solid #E2E2E2 !important;
  color: #333 !important;
}

/* Fix black button text */
.stButton > button,
button.st-emotion-cache-ag3azy.eacrzsi2,
.st-emotion-cache-ktz07o {
  color: #FFFFFF !important;
  background: #9354FF !important;
}

/* Button hover states */
.stButton > button:hover,
button.st-emotion-cache-ag3azy.eacrzsi2:hover,
.st-emotion-cache-ktz07o:hover {
  color: #9354FF !important;
  background: #FFFFFF !important;
}

/* Fix black text in drag & drop areas */
.stFileUploader {
  color: #333 !important;
}

/* Fix any inverted text elements */
.st-bd, .st-be, .st-bn {
  color: #333 !important;
}

/* Fix for any text that might be invisible due to white-on-white */
.st-emotion-cache-vewp9z, 
.st-emotion-cache-vewp9z h1,
.st-emotion-cache-vewp9z h2,
.st-emotion-cache-vewp9z h3,
.st-emotion-cache-vewp9z h4,
.st-emotion-cache-vewp9z h5,
.st-emotion-cache-vewp9z h6,
.st-emotion-cache-vewp9z p,
.st-emotion-cache-vewp9z ol li,
.st-emotion-cache-vewp9z ul li {
  color: #333 !important;
}

/* Ensure form fields are visible with proper contrast */
.st-dv input, 
.st-dv textarea, 
.st-dv select {
  background-color: #F7F7F7 !important;
  color: #333 !important;
  border: 1px solid #E2E2E2 !important;
}

/* Fix for checkboxes and their labels */
input[type="checkbox"],
input[type="radio"] {
  border: 1px solid #111 !important;
}

/* Fix for dropdown menus */
.st-ar button {
  color: #111 !important;
  background-color: #f1f1f1 !important;
}

/* Fix for alerts and notification boxes */
.stAlert .stAlertContainer {
  background-color: #FFF !important;
  color: #333 !important;
  border: 1px solid #E2E2E2 !important;
}

/* Fix for any black overlays */
.section-card,
.sidebar-content,
.st-emotion-cache-x2by6s .st-emotion-cache-13o7eu2.e1lln2w84[data-testid="stVerticalBlockBorderWrapper"] .stVerticalBlock {
  background-color: #FFFFFF !important;
  color: #333 !important;
}

/* Ensure any placeholder text is visible */
::placeholder {
  color: #999 !important;
  opacity: 1 !important;
}
* Fix input fields that appear black */
input, textarea, select, .st-dv {
  background-color: #FFFFFF !important;
  border: 1px solid #E2E2E2 !important;
  color: #333 !important;
}

/* Fix black button text */
.stButton > button,
button.st-emotion-cache-ag3azy.eacrzsi2,
.st-emotion-cache-ktz07o,
button.css-fblp2m,
.stFileUploader button {
  color: #FFFFFF !important;
  background: #9354FF !important;
}

/* Button hover states */
.stButton > button:hover,
button.st-emotion-cache-ag3azy.eacrzsi2:hover,
.st-emotion-cache-ktz07o:hover {
  color: #9354FF !important;
  background: #FFFFFF !important;
}

/* Fix black text in drag & drop areas */
.stFileUploader {
  color: #333 !important;
}

/* Fix for any inverted text elements */
.st-bd, .st-be, .st-bn {
  color: #333 !important;
}

/* Fix specifically for the Browse files button */
.stFileUploader button {
  color: #FFFFFF !important;
  background-color: #9354FF !important;
  border: none !important;
}

/* Fix for Export Format dropdown and other dark selectors */
.css-1qg05tj, 
[data-testid="stSelectbox"] > div > div,
select,
.st-emotion-cache-y4bq5x,
.st-emotion-cache-1qg05tj,
.st-emotion-cache-6qob1r {
  background-color: #FFFFFF !important;
  color: #333 !important;
  border: 1px solid #E2E2E2 !important;
}

/* Fix for any text that might be invisible due to white-on-white */
.st-emotion-cache-vewp9z, 
.st-emotion-cache-vewp9z h1,
.st-emotion-cache-vewp9z h2,
.st-emotion-cache-vewp9z h3,
.st-emotion-cache-vewp9z h4,
.st-emotion-cache-vewp9z h5,
.st-emotion-cache-vewp9z h6,
.st-emotion-cache-vewp9z p,
.st-emotion-cache-vewp9z ol li,
.st-emotion-cache-vewp9z ul li {
  color: #333 !important;
}

/* Ensure form fields are visible with proper contrast */
.st-dv input, 
.st-dv textarea, 
.st-dv select,
.stSelectbox > div > div {
  background-color: #F7F7F7 !important;
  color: #333 !important;
  border: 1px solid #E2E2E2 !important;
}

/* Specific fix for browse button text */
.stFileUploader button,
.stFileUploader [data-testid="stFileUploadDropzone"] button,
.css-1cpxqw2 {
  color: #FFFFFF !important;
  background-color: #9354FF !important;
}

/* Fix for the dark export format dropdown */
[data-testid="stSelectbox"],
div[role="listbox"] {
  background-color: #FFFFFF !important;
  color: #333 !important;
}

/* Fix for checkboxes and their labels */
input[type="checkbox"],
input[type="radio"] {
  border: 1px solid #111 !important;
}

/* Fix for dropdown menus */
.st-ar button {
  color: #111 !important;
  background-color: #f1f1f1 !important;
}

/* Fix for alerts and notification boxes */
.stAlert .stAlertContainer {
  background-color: #FFF !important;
  color: #333 !important;
  border: 1px solid #E2E2E2 !important;
}

/* Fix for any black overlays */
.section-card,
.sidebar-content,
.st-emotion-cache-x2by6s .st-emotion-cache-13o7eu2.e1lln2w84[data-testid="stVerticalBlockBorderWrapper"] .stVerticalBlock {
  background-color: #FFFFFF !important;
  color: #333 !important;
}

/* Ensure any placeholder text is visible */
::placeholder {
  color: #999 !important;
  opacity: 1 !important;
}
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state variables
    # Initialize session state variables
    if 'config' not in st.session_state:
        st.session_state.config = load_config()

    # Ensure scoring_system exists in config after loading
    if 'scoring_system' not in st.session_state.config:
        st.session_state.config['scoring_system'] = {
            "weighting": {
                "requirement_match": 0.4,
                "compliance": 0.25,
                "quality": 0.2,
                "alignment": 0.15,
                "risk": 0.1
            },
            "grading_scale": {
                "excellent": [90, 100],
                "good": [70, 89],
                "fair": [50, 69],
                "poor": [0, 49]
            }
        }
        print("Added default scoring_system to config in session state.")


    if 'knowledge_base' not in st.session_state:
        try:
            kb_dir = st.session_state.config["knowledge_base"]["directory"]
            embedding_model_name = st.session_state.config["knowledge_base"]["embedding_model"]
            st.session_state.knowledge_base = ProposalKnowledgeBase(kb_dir, embedding_model_name)
        except Exception as e:
            st.error(f"Failed to initialize knowledge base: {str(e)}")
            st.session_state.knowledge_base = None

    if 'generator' not in st.session_state:
        openai_key = st.session_state.config["api_keys"]["openai_key"]
        if not openai_key:
            openai_key = os.environ.get("OPENAI_API_KEY", "")

        if openai_key and st.session_state.knowledge_base: # Also check if KB initialized successfully
            st.session_state.generator = EnhancedProposalGenerator(st.session_state.knowledge_base, openai_key)
        elif not openai_key:
            st.error("OpenAI API key is not configured. Please add it to config.json or set the OPENAI_API_KEY environment variable.")
            st.session_state.generator = None
        else: # KB failed to initialize
            st.error("Proposal Generator could not be initialized due to Knowledge Base error.")
            st.session_state.generator = None


    if 'rfp_text' not in st.session_state:
        st.session_state.rfp_text = ""
    if 'rfp_analysis' not in st.session_state:
        st.session_state.rfp_analysis = None
    if 'proposal_data' not in st.session_state:
        st.session_state.proposal_data = {
            "sections": {},
            "required_sections": [],
            "client_background": None,
            "differentiators": None,
            "client_name": "Client Organization"
        }
    if 'client_background' not in st.session_state:
        st.session_state.client_background = None
    if 'differentiators' not in st.session_state:
        st.session_state.differentiators = None
    if 'advanced_analysis' not in st.session_state:
        st.session_state.advanced_analysis = {
            "compliance_matrix": None,
            "risk_assessment": None,
            "alignment_assessment": None,
            "compliance_assessment": None
        }
    if 'template_created' not in st.session_state:
        st.session_state.template_created = False
    if 'template_sections' not in st.session_state:
        st.session_state.template_sections = []
    if 'rfp_response_analysis' not in st.session_state:
        st.session_state.rfp_response_analysis = None
    if 'vendor_analysis' not in st.session_state:
        st.session_state.vendor_analysis = None
    if 'vendor_score_results' not in st.session_state:
        st.session_state.vendor_score_results = None
    if 'vendor_gaps_risks' not in st.session_state:
        st.session_state.vendor_gaps_risks = None
    if 'vendor_proposals' not in st.session_state:
        st.session_state.vendor_proposals = []
    if 'rfp_templates' not in st.session_state:
        st.session_state.rfp_templates = []
    if 'rfp_template_content' not in st.session_state:
        st.session_state.rfp_template_content = None

    if 'dynamic_weights' not in st.session_state or not st.session_state.dynamic_weights:
        st.session_state.dynamic_weights = st.session_state.config.get('scoring_system', {}).get('weighting', {}).copy()
        if not st.session_state.dynamic_weights:
            st.session_state.dynamic_weights = {
                "requirement_match": 0.4, "compliance": 0.25, "quality": 0.2,
                "alignment": 0.15, "risk": 0.1
            }
            st.warning("Scoring system weights not found in config. Using default weights.")


    # --- MODIFIED HEADER SECTION ---
    with st.container():
        col_title_1, col_title_2 = st.columns([1, 6]) # Adjust ratio as needed e.g. [1,5] or [1,7]
        
        logo_path_from_config = st.session_state.config.get("company_info", {}).get("logo_path", "")

        with col_title_1:
            if logo_path_from_config and os.path.exists(logo_path_from_config):
                try:
                    st.image(logo_path_from_config, width=400)  # Adjust width as desired
                except Exception as e:
                    # Optionally show a placeholder or a small error message if logo fails to load
                    # st.caption("Logo error")
                    pass # Fail silently if logo can't be displayed
            else:
                st.empty() # Keep the column for alignment even if no logo

        with col_title_2:
            st.title("Imdad RFP Analyzer & Proposal Generator")
        
        if logo_path_from_config and not os.path.exists(logo_path_from_config):
             st.caption(f"Note: Logo path specified in config ('{logo_path_from_config}') but file not found.")
    # --- END MODIFIED HEADER SECTION ---


    # Main workflow tabs
    tabs = st.tabs(["📋 RFP Assessment", "📝 Proposal Template Creation", "📊 Generate Proposal", 
                "📤 Export", "🔍 Advanced Analysis", "🔍 Vendor Proposal Evaluation", 
                "📋 RFP Template Creator", "📋 SOW Analysis"])
                   
                   
    # Tab 1: Upload RFP (Modified Section)
    with tabs[0]:
        st.header("RFP Assessment")

        col1_tab, col2_tab = st.columns([3, 2])

        with col1_tab:
            uploaded_file = st.file_uploader("Upload RFP Document", type=["docx", "pdf", "txt", "md"])

            if uploaded_file is not None:
                temp_file_path = ""
                try:
                    file_extension = os.path.splitext(uploaded_file.name)[1]
                    if not file_extension:
                        file_extension = ".tmp"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file_obj:
                        temp_file_obj.write(uploaded_file.getvalue())
                        temp_file_path = temp_file_obj.name
                    
                    rfp_text = process_rfp(temp_file_path)
                    st.session_state.rfp_text = rfp_text
                    st.success(f"Successfully processed {uploaded_file.name}")

                    with st.expander("Preview RFP Content", expanded=False):
                        st.text_area("RFP Text", rfp_text, height=300, key="rfp_preview")

                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                finally:
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

        with col2_tab:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Instructions")
            st.markdown("""
            1. Upload your RFP document (PDF, Word, or text)
            2. We'll extract and analyze the key requirements
            3. Click 'Analyze RFP' to get insights
            4. Proceed to the next tab to create your template
            """)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.rfp_text:
                if st.button("Analyze RFP", type="primary", key="analyze_rfp_btn_tab1"):
                    if not st.session_state.generator:
                        st.error("Generator not initialized. Please check API key and Knowledge Base.")
                    else:
                        with st.spinner("Analyzing RFP..."):
                            rfp_analysis_result = st.session_state.generator.analyze_rfp(st.session_state.rfp_text)
                            st.session_state.rfp_analysis = rfp_analysis_result

                            # Extract insights but NOT required sections (that will be done in Tab 2)
                            st.session_state.mandatory_criteria = st.session_state.generator.extract_mandatory_criteria(rfp_analysis_result)
                            st.session_state.deadlines = st.session_state.generator.extract_deadlines(rfp_analysis_result)
                            st.session_state.deliverables = st.session_state.generator.extract_deliverables(rfp_analysis_result)
                            
                            internal_capabilities = st.session_state.config.get("internal_capabilities", {})
                            st.session_state.compliance_assessment = st.session_state.generator.assess_compliance(rfp_analysis_result, internal_capabilities)

                            st.success("RFP Analysis Complete")
                            st.markdown("### Key Insights")
                            
                            st.markdown("#### Mandatory Criteria")
                            if st.session_state.mandatory_criteria:
                                st.markdown("\n".join([f"- {item}" for item in st.session_state.mandatory_criteria]))
                            else:
                                st.markdown("No mandatory criteria found.")

                            st.markdown("#### Deadlines")
                            if st.session_state.deadlines:
                                st.markdown("\n".join([f"- {item}" for item in st.session_state.deadlines]))
                            else:
                                st.markdown("No deadlines found.")

                            st.markdown("#### Deliverables")
                            if st.session_state.deliverables:
                                st.markdown("\n".join([f"- {item}" for item in st.session_state.deliverables]))
                            else:
                                st.markdown("No deliverables found.")

                            st.markdown("#### Compliance Assessment")
                            st.markdown(st.session_state.compliance_assessment)

                            st.markdown("#### Full RFP Analysis")
                            st.write(rfp_analysis_result)
                            
                            st.info("💡 **Next Step:** Go to the 'Proposal Template Creation' tab to upload your RFP and extract sections for your proposal template.")


   # Tab 2: Proposal Template Creation (Fixed Version)
    with tabs[1]:
        st.header("Create Proposal Template")
        
        # Initialize session state for tab2 if not exists
        if 'tab2_rfp_analyzed' not in st.session_state:
            st.session_state.tab2_rfp_analyzed = False
        if 'tab2_required_sections' not in st.session_state:
            st.session_state.tab2_required_sections = []
        if 'tab2_rfp_analysis' not in st.session_state:
            st.session_state.tab2_rfp_analysis = None
        if 'tab2_current_file' not in st.session_state:
            st.session_state.tab2_current_file = None
        if 'tab2_rfp_text' not in st.session_state:
            st.session_state.tab2_rfp_text = None
        
        # Add upload functionality specific to this tab
        uploaded_file_tab2 = st.file_uploader("Upload RFP Document", type=["docx", "pdf", "txt", "md"], key="upload_rfp_tab2")
        
        # Check if a new file is uploaded or if the file has changed
        if uploaded_file_tab2 is not None:
            current_file_info = f"{uploaded_file_tab2.name}_{uploaded_file_tab2.size}"
            
            # Only process if it's a new file or file has changed
            if st.session_state.tab2_current_file != current_file_info:
                temp_file_path = ""
                try:
                    file_extension = os.path.splitext(uploaded_file_tab2.name)[1]
                    if not file_extension:
                        file_extension = ".tmp"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file_obj:
                        temp_file_obj.write(uploaded_file_tab2.getvalue())
                        temp_file_path = temp_file_obj.name
                    
                    # Process the RFP
                    rfp_text = process_rfp(temp_file_path)
                    st.session_state.tab2_rfp_text = rfp_text  # Store specifically for tab2
                    st.session_state.rfp_text = rfp_text  # Store in main session state as well
                    st.success(f"Successfully processed {uploaded_file_tab2.name}")
                    
                    # Reset analysis state for new file
                    st.session_state.tab2_rfp_analyzed = False
                    st.session_state.tab2_required_sections = []
                    st.session_state.tab2_rfp_analysis = None
                    st.session_state.tab2_current_file = current_file_info
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                finally:
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
        
        # Reset states if no file is uploaded
        elif uploaded_file_tab2 is None:
            st.session_state.tab2_rfp_analyzed = False
            st.session_state.tab2_required_sections = []
            st.session_state.tab2_rfp_analysis = None
            st.session_state.tab2_current_file = None
            st.session_state.tab2_rfp_text = None

        # Show file preview and analysis section
        if st.session_state.tab2_rfp_text:
            # Show preview
            with st.expander("Preview RFP Content", expanded=False):
                st.text_area("RFP Text", st.session_state.tab2_rfp_text, height=300, key="rfp_preview_tab2")
            
            # Show analysis button or analysis results
            if not st.session_state.tab2_rfp_analyzed:
                st.markdown("### Step 1: Analyze RFP for Sections")
                if st.button("Analyze RFP for Sections", type="primary", key="analyze_rfp_tab2"):
                    if not st.session_state.generator:
                        st.error("Generator not initialized. Please check API key and Knowledge Base.")
                    else:
                        with st.spinner("Analyzing RFP to extract required sections..."):
                            try:
                                # Analyze RFP
                                rfp_analysis_result = st.session_state.generator.analyze_rfp(st.session_state.tab2_rfp_text)
                                st.session_state.tab2_rfp_analysis = rfp_analysis_result
                                st.session_state.rfp_analysis = rfp_analysis_result  # Store in main session state as well
                                
                                # Extract required sections
                                required_sections = st.session_state.generator.extract_required_sections(rfp_analysis_result)
                                st.session_state.tab2_required_sections = required_sections
                                st.session_state.required_sections = required_sections  # Store in main session state as well
                                
                                # Mark as analyzed
                                st.session_state.tab2_rfp_analyzed = True
                                
                                st.success("RFP Analysis Complete! Sections extracted successfully.")
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error analyzing RFP: {str(e)}")
            else:
                st.success("✅ RFP Analysis Complete!")
                
            # Show section selection interface after analysis
            if st.session_state.tab2_rfp_analyzed:
                st.markdown("---")
                st.markdown("### Step 2: Select and Customize Sections")
                
                col1_tab2, col2_tab2 = st.columns([2, 1])

                with col1_tab2:
                    if st.session_state.tab2_required_sections:
                        st.markdown("#### Sections Extracted from RFP Analysis")
                        st.info(f"Found {len(st.session_state.tab2_required_sections)} sections in the RFP")
                        
                        # Create a 2-column layout for checkboxes
                        checkbox_cols = st.columns(2)
                        
                        for i, section in enumerate(st.session_state.tab2_required_sections):
                            col_idx = i % 2
                            with checkbox_cols[col_idx]:
                                already_added = section in st.session_state.template_sections
                                is_selected = st.checkbox(section, value=already_added, key=f"tab2_section_select_{section}")
                                if is_selected and section not in st.session_state.template_sections:
                                    st.session_state.template_sections.append(section)
                                elif not is_selected and section in st.session_state.template_sections:
                                    st.session_state.template_sections.remove(section)
                    else:
                        st.warning("No specific sections were extracted from the RFP analysis.")

                    st.markdown("---")
                    st.markdown("#### Add Custom Section")
                    new_section_name_input = st.text_input("Enter custom section name:", key="new_section_name_tab2")
                    
                    if st.button("Add Custom Section", type="secondary", key="add_custom_section_tab2"):
                        if new_section_name_input:
                            cleaned_new_section = remove_problematic_chars(new_section_name_input.strip().title())
                            if cleaned_new_section and cleaned_new_section not in st.session_state.template_sections:
                                st.session_state.template_sections.append(cleaned_new_section)
                                st.success(f"Section '{cleaned_new_section}' added to template.")
                                st.rerun()
                            elif cleaned_new_section in st.session_state.template_sections:
                                st.warning(f"Section '{cleaned_new_section}' already exists in template.")
                            else:
                                st.warning("Please provide a valid section name (after cleaning).")
                        else:
                            st.warning("Please provide a section name.")
                    
                    st.markdown("---")
                    st.markdown("#### Current Proposal Template Sections")
                    current_sections_copy = st.session_state.template_sections[:]
                    
                    if not current_sections_copy:
                        st.info("No sections selected for the template yet.")
                    else:
                        for i, section_item in enumerate(current_sections_copy):
                            sec_col1, sec_col2 = st.columns([4, 1])
                            with sec_col1:
                                st.write(f"{i+1}. {section_item}")
                            with sec_col2:
                                if st.button("Remove", key=f"remove_section_tab2_{i}_{section_item}"):
                                    if i < len(st.session_state.template_sections):
                                        st.session_state.template_sections.pop(i)
                                        st.rerun()

                    st.markdown("---")
                    st.markdown("### Step 3: Confirm Template")
                    if st.session_state.template_sections:
                        st.success(f"Template ready with {len(st.session_state.template_sections)} sections")
                        if st.button("Confirm Sections & Proceed to Generate", type="primary", key="confirm_template_tab2"):
                            st.session_state.template_created = True
                            st.success("✅ Template sections confirmed! Proceed to the 'Generate Proposal' tab.")
                    else:
                        st.button("Confirm Sections & Proceed to Generate", type="primary", key="confirm_template_disabled_tab2", disabled=True)
                        st.info("Select at least one section to continue")

                with col2_tab2:
                    st.markdown('<div class="info-box sidebar-content">', unsafe_allow_html=True)
                    st.markdown("### 📝 Template Instructions")
                    if not st.session_state.tab2_rfp_analyzed:
                        st.markdown("""
                        **Step 1: Analyze Document**
                        - Upload an RFP document above
                        - Click 'Analyze RFP for Sections' to extract sections
                        """)
                    else:
                        st.markdown("""
                        **Step 2: Build Template**
                        - ✅ RFP analyzed successfully
                        - Select from extracted sections
                        - Add custom sections if needed
                        - Remove unwanted sections
                        
                        **Step 3: Confirm**
                        - Review your template sections
                        - Click 'Confirm Sections & Proceed'
                        """)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # No file uploaded yet
            st.info("👆 Please upload an RFP document above to get started.")
            st.markdown("""
            ### How it works:
            1. **Upload** your RFP document (PDF, Word, or text file)
            2. **Analyze** the document to extract required sections
            3. **Select** sections you want in your proposal template
            4. **Customize** by adding or removing sections
            5. **Confirm** your template and proceed to generate proposals
            """)

    # Tab 3: Generate Proposal
    with tabs[2]:
        st.header("Generate Proposal")

        if not st.session_state.template_created:
            st.warning("Please create a template first (Tab 2).")
        elif not st.session_state.generator:
            st.warning("OpenAI API key is not configured or Generator not initialized. Please check settings.")
        else:
            col1_tab3, col2_tab3 = st.columns([1, 1])

            with col1_tab3:
                st.markdown("### Proposal Configuration")
                # client_name_input_gen will be cleaned by remove_problematic_chars
                client_name_input_gen = st.text_input("Client Name", st.session_state.proposal_data.get('client_name', "Client Organization"), key="client_name_input_gen")
                
                # differentiators_input will be cleaned by remove_problematic_chars
                differentiators_input = st.text_area("Company Differentiators",
                                                st.session_state.proposal_data.get('differentiators', "Enter key differentiators"),
                                                key="differentiators_input_gen")

                if st.button("Generate Proposal", type="primary", key="generate_proposal_btn"):
                    with st.spinner("Generating proposal..."):
                        try:
                            cleaned_client_name = remove_problematic_chars(client_name_input_gen)
                            cleaned_differentiators = remove_problematic_chars(differentiators_input)
                            
                            company_info_payload = {
                                "name": st.session_state.config["company_info"]["name"], # Assumed safe
                                "differentiators": cleaned_differentiators
                            }
                            # generate_full_proposal expects cleaned inputs or cleans them internally
                            # st.session_state.rfp_text is already cleaned
                            # st.session_state.template_sections contains cleaned section names
                            proposal_data_result = st.session_state.generator.generate_full_proposal(
                                st.session_state.rfp_text,
                                cleaned_client_name,
                                company_info_payload,
                                st.session_state.template_sections
                            )
                            st.session_state.proposal_data = proposal_data_result # Result is cleaned by generate_full_proposal
                            st.session_state.proposal_data['client_name'] = cleaned_client_name # ensure client name is updated
                            st.session_state.proposal_data['differentiators'] = cleaned_differentiators # ensure differentiators updated

                            st.success("Proposal generated successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error generating proposal: {str(e)}")
                            # Consider logging the full traceback for debugging
                            import traceback
                            print(traceback.format_exc())


            with col2_tab3:
                st.markdown("### Generation Controls")
                st.markdown("""
                The proposal generation process:
                1. Uses the RFP analysis and your defined template sections.
                2. Retrieves relevant content from the knowledge base.
                3. Generates sections tailored to the RFP and your inputs.
                """)

            if st.session_state.proposal_data and st.session_state.proposal_data["sections"]:
                st.markdown("---")
                st.header("Proposal Preview")
                # Section names and content in proposal_data are already cleaned
                section_names_preview = list(st.session_state.proposal_data["sections"].keys())
                section_tabs_preview = st.tabs(section_names_preview)

                for i, section_name_item in enumerate(section_names_preview):
                    content_item = st.session_state.proposal_data["sections"][section_name_item]
                    with section_tabs_preview[i]:
                        st.markdown(content_item) # Display already cleaned content
                        st.markdown("---")
                        feedback_col1, feedback_col2 = st.columns([3, 1])
                        with feedback_col1:
                            # feedback_text will be cleaned before use
                            feedback_text = st.text_area(
                                "Provide feedback to improve this section:",
                                key=f"feedback_{section_name_item}"
                            )
                        with feedback_col2:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("Update Section", key=f"update_{section_name_item}"):
                                if feedback_text:
                                    try:
                                        with st.spinner(f"Updating '{section_name_item}'..."):
                                            if not st.session_state.generator:
                                                raise Exception("Generator not initialized.")
                                            # refine_section expects cleaned inputs or cleans them internally
                                            # section_name_item and content_item are from proposal_data (cleaned)
                                            # st.session_state.proposal_data.get('client_name') is cleaned
                                            refined_content_result = st.session_state.generator.refine_section(
                                                section_name_item,
                                                content_item,
                                                feedback_text, # Will be cleaned by refine_section
                                                st.session_state.proposal_data.get('client_name', 'Client')
                                            )
                                            # Result from refine_section is cleaned
                                            st.session_state.proposal_data["sections"][section_name_item] = refined_content_result
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating section: {str(e)}")
                                else:
                                    st.warning("Please provide feedback to update the section.")
            elif st.session_state.template_created : # only show if template was created but no sections yet
                 st.info("Click 'Generate Proposal' to create the content for your selected sections.")


    # Tab 4: Export
    with tabs[3]:
        st.header("Export Your Proposal")

        if not st.session_state.proposal_data or not st.session_state.proposal_data["sections"]:
            st.warning("Please generate your proposal first (Tab 3).")
        elif not st.session_state.generator: # Added this check based on pattern in other tabs
            st.warning("OpenAI API key is not configured or Generator not initialized.")
        else:
            col1_tab4, col2_tab4 = st.columns([2, 1])

            with col1_tab4:
                st.markdown("### Export Settings")
                # company_name_export is from config, assumed safe
                company_name_export = st.session_state.config["company_info"]["name"]
                # client_name_for_export is from proposal_data, already cleaned
                client_name_for_export = st.session_state.proposal_data.get("client_name", "Client")

                uploaded_logo_export = st.file_uploader("Upload Company Logo for Export (optional)", type=["png", "jpg", "jpeg"], key="logo_uploader_export")
                logo_path_export = None
                if uploaded_logo_export:
                    try:
                        # Save to a temporary file with correct extension for fpdf/docx
                        logo_ext = os.path.splitext(uploaded_logo_export.name)[1]
                        if not logo_ext: logo_ext = ".png" # default if no ext
                        with tempfile.NamedTemporaryFile(delete=False, suffix=logo_ext) as temp_logo_file:
                            temp_logo_file.write(uploaded_logo_export.getvalue())
                            logo_path_export = temp_logo_file.name
                    except Exception as e:
                        st.error(f"Error processing logo for export: {e}")
                        logo_path_export = None


                export_format_selection = st.selectbox(
                    "Export Format",
                    ["Word Document (.docx)", "PDF Document (.pdf)", "Markdown (.md)"],
                    key="export_format_select"
                )

                if st.button("Export", type="primary", key="export_button_final"):
                    with st.spinner(f"Exporting proposal as {export_format_selection}..."):
                        try:
                            output_dir_export = "exported_proposals"
                            if not os.path.exists(output_dir_export):
                                os.makedirs(output_dir_export)
                            
                            # Prepare a safe filename base from the cleaned client name
                            safe_client_name_part = client_name_for_export.replace(' ', '_').replace('/', '_') # basic sanitize
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

                            if export_format_selection == "Word Document (.docx)":
                                output_filename_export = f"Proposal_for_{safe_client_name_part}_{timestamp}.docx"
                                output_path_export = os.path.join(output_dir_export, output_filename_export)
                                # export_to_word expects cleaned data or cleans it internally
                                # st.session_state.proposal_data contains cleaned sections/client_name
                                final_path_result = export_to_word(
                                    st.session_state.proposal_data,
                                    company_name_export,
                                    client_name_for_export,
                                    output_path_export,
                                    logo_path_export # Can be None
                                )
                                if final_path_result and os.path.exists(final_path_result):
                                    with open(final_path_result, "rb") as file_docx:
                                        st.download_button(
                                            label="Download Word Document", data=file_docx,
                                            file_name=output_filename_export,
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                        )
                                else: st.error("Failed to create Word document.")

                            elif export_format_selection == "PDF Document (.pdf)":
                                output_filename_export = f"Proposal_for_{safe_client_name_part}_{timestamp}.pdf"
                                output_path_export = os.path.join(output_dir_export, output_filename_export)
                                # export_to_pdf expects cleaned data or cleans it internally
                                final_path_result = export_to_pdf(
                                    st.session_state.proposal_data,
                                    company_name_export,
                                    client_name_for_export, # Already cleaned
                                    output_path_export,
                                    logo_path_export # Can be None
                                )
                                if final_path_result and os.path.exists(final_path_result):
                                    with open(final_path_result, "rb") as file_pdf:
                                        st.download_button(
                                            label="Download PDF", data=file_pdf,
                                            file_name=output_filename_export, mime="application/pdf"
                                        )
                                else: st.error("Failed to create PDF document. Ensure 'fpdf' is installed if using PDF export.")
                            
                            else: # Markdown
                                output_filename_export = f"Proposal_for_{safe_client_name_part}_{timestamp}.md"
                                # All content for md is from proposal_data, which is cleaned
                                md_content_export = f"# Proposal for {client_name_for_export}\n\n"
                                for sec_name, sec_content in st.session_state.proposal_data["sections"].items():
                                    md_content_export += f"## {sec_name}\n\n{sec_content}\n\n"
                                st.download_button(
                                    label="Download Markdown File", data=md_content_export,
                                    file_name=output_filename_export, mime="text/markdown"
                                )
                            st.success("Export process initiated.")
                        except Exception as e:
                            st.error(f"An unexpected error occurred during export: {str(e)}")
                            import traceback
                            print(traceback.format_exc()) # For server-side debugging
                        finally:
                            if logo_path_export and os.path.exists(logo_path_export):
                                try:
                                    os.remove(logo_path_export) # Clean up temp logo
                                except Exception as e_rm:
                                    print(f"Error removing temp logo: {e_rm}")


            with col2_tab4:
                st.markdown("### Export Options")
                st.markdown("""
                You can export your proposal in multiple formats:
                1. **Word Document**: Professional document with formatting.
                2. **PDF Document**: Fixed-format document for printing or sharing.
                3. **Markdown**: Text-based format for easy editing.
                """)


    # Tab 5: Advanced Analysis
    with tabs[4]:
        st.header("Advanced Proposal Analysis")

        if not st.session_state.proposal_data or not st.session_state.proposal_data["sections"]:
            st.warning("Please generate your proposal first (Tab 3).")
        elif not st.session_state.generator:
            st.warning("OpenAI API key is not configured or Generator not initialized.")
        else:
            if st.button("Generate Advanced Analysis", type="primary", key="advanced_analysis_button"):
                with st.spinner("Generating advanced analysis..."):
                    try:
                        internal_capabilities_adv = st.session_state.config.get("internal_capabilities", {})
                        # generate_advanced_analysis expects cleaned data or cleans internally
                        # proposal_data, rfp_analysis, client_name are already cleaned in session_state
                        advanced_analysis_result = st.session_state.generator.generate_advanced_analysis(
                            st.session_state.proposal_data,
                            st.session_state.rfp_analysis,
                            internal_capabilities_adv, # Will be cleaned by generate_advanced_analysis
                            st.session_state.proposal_data.get('client_name', 'Client')
                        )
                        st.session_state.advanced_analysis = advanced_analysis_result # Results are cleaned
                        st.success("Advanced Analysis Complete")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating advanced analysis: {str(e)}")

            if st.session_state.advanced_analysis and any(st.session_state.advanced_analysis.values()):
                st.markdown("### Advanced Analysis Results")
                # All results from advanced_analysis are already cleaned
                if st.session_state.advanced_analysis.get("compliance_matrix"):
                    st.markdown("#### Compliance Matrix")
                    st.markdown(st.session_state.advanced_analysis["compliance_matrix"])
                if st.session_state.advanced_analysis.get("risk_assessment"):
                    st.markdown("#### Risk Assessment")
                    st.markdown(st.session_state.advanced_analysis["risk_assessment"])
                if st.session_state.advanced_analysis.get("alignment_assessment"):
                    st.markdown("#### Alignment Assessment")
                    st.markdown(st.session_state.advanced_analysis["alignment_assessment"])
                if st.session_state.advanced_analysis.get("compliance_assessment"):
                    st.markdown("#### Compliance Assessment (Internal)")
                    st.markdown(st.session_state.advanced_analysis["compliance_assessment"])
                # Note: 'quality_assurance' was in your original code but not added to advanced_analysis dict. Add if needed.
            elif st.session_state.get("advanced_analysis_button_clicked_flag", False): # You'd need to set this flag
                 st.info("Click 'Generate Advanced Analysis' to see results.")


    # Tab 6: Vendor Proposal Evaluation
    with tabs[5]:
        st.header("Vendor Proposal Evaluation")

        if not st.session_state.rfp_analysis:
            st.warning("Please upload and analyze an RFP first (Tab 1).")
        elif not st.session_state.generator:
            st.warning("OpenAI API key is not configured or Generator not initialized.")
        else:
            st.markdown("---")
            st.subheader("⚙️ Configure Scoring Weightage")
            
            num_metrics_eval = len(st.session_state.dynamic_weights)
            num_cols_for_weights_eval = min(num_metrics_eval, 4) # Max 4 columns for weights
            cols_weights_eval = st.columns(num_cols_for_weights_eval if num_cols_for_weights_eval > 0 else 1)

            st.markdown("Enter weights (e.g., decimals summing to 1.0, or percentages summing to 100):")
            total_weight_sum_eval = 0.0
            metrics_list_eval = list(st.session_state.dynamic_weights.keys())

            for i, metric_key in enumerate(metrics_list_eval):
                col_idx_eval = i % num_cols_for_weights_eval if num_cols_for_weights_eval > 0 else 0
                with cols_weights_eval[col_idx_eval]:
                    current_weight_val = st.session_state.dynamic_weights.get(metric_key, 0.0)
                    new_weight = st.number_input(
                        f"{metric_key.replace('_', ' ').title()}", min_value=0.0,
                        value=current_weight_val, step=0.01, format="%.2f",
                        key=f"weight_input_eval_{metric_key}"
                    )
                    if new_weight != current_weight_val: # Update only if changed to avoid excessive reruns
                        st.session_state.dynamic_weights[metric_key] = new_weight
                        # st.rerun() # Rerun to update total_weight_sum_eval display
                    total_weight_sum_eval += new_weight # Summing up current values for display

            st.info(f"Current total weight sum: {total_weight_sum_eval:.2f}")
            if abs(total_weight_sum_eval - 1.0) > 0.01 and abs(total_weight_sum_eval - 100.0) > 1.0:
                st.warning("Weights typically sum to 1.0 (for decimals) or 100.0 (for percentages). The score will be Σ(metric_score * weight).")

            st.markdown("---")
            uploaded_vendor_proposal_file = st.file_uploader("Upload Vendor Proposal", type=["docx", "pdf", "txt", "md"], key="vendor_proposal_upload")

            if uploaded_vendor_proposal_file:
                # Process vendor proposal file (ensure it's only processed once or if file changes)
                if (st.session_state.get('processed_vendor_file_name') != uploaded_vendor_proposal_file.name or
                    st.session_state.get('processed_vendor_file_size') != uploaded_vendor_proposal_file.size):
                    temp_vendor_file_path = ""
                    try:
                        vendor_file_ext = os.path.splitext(uploaded_vendor_proposal_file.name)[1] or ".tmp"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=vendor_file_ext) as temp_vp_file:
                            temp_vp_file.write(uploaded_vendor_proposal_file.getvalue())
                            temp_vendor_file_path = temp_vp_file.name
                        
                        vendor_proposal_text_content = process_rfp(temp_vendor_file_path) # Reuses your RFP processing
                        st.session_state.vendor_proposal_text = vendor_proposal_text_content # Already cleaned
                        st.session_state.processed_vendor_file_name = uploaded_vendor_proposal_file.name
                        st.session_state.processed_vendor_file_size = uploaded_vendor_proposal_file.size
                        st.session_state.vendor_analysis = None # Reset previous analysis
                        st.session_state.vendor_score_results = None
                        st.session_state.vendor_gaps_risks = None
                        st.success(f"Processed vendor proposal: {uploaded_vendor_proposal_file.name}")
                    except Exception as e_vp:
                        st.error(f"Error processing vendor proposal: {e_vp}")
                    finally:
                        if temp_vendor_file_path and os.path.exists(temp_vendor_file_path):
                            os.unlink(temp_vendor_file_path)
                
                if st.session_state.get('vendor_proposal_text'):
                    with st.expander("Preview Vendor Proposal Content", expanded=False):
                        st.text_area("Vendor Proposal Text", st.session_state.vendor_proposal_text, height=300, key="vendor_proposal_preview_text")
                    
                    # client_name_for_eval will be cleaned
                    client_name_for_eval = st.text_input("Client Name (for analysis context)",
                                                         st.session_state.proposal_data.get('client_name', "Client Organization"),
                                                         key="client_name_eval_input")

                    if st.button("Analyze Vendor Proposal", type="primary", key="analyze_vendor_button"):
                        with st.spinner("Analyzing vendor proposal... This may take a moment."):
                            try:
                                cleaned_client_name_eval = remove_problematic_chars(client_name_for_eval)
                                current_scoring_config_eval = {
                                    "weighting": st.session_state.dynamic_weights,
                                    "grading_scale": st.session_state.config.get('scoring_system', {}).get('grading_scale', {})
                                }
                                # vendor_proposal_text and rfp_analysis are already cleaned in session_state
                                analysis_text_result = st.session_state.generator.analyze_vendor_proposal(
                                    st.session_state.vendor_proposal_text,
                                    st.session_state.rfp_analysis,
                                    cleaned_client_name_eval,
                                    current_scoring_config_eval
                                )
                                st.session_state.vendor_analysis = analysis_text_result # Result is cleaned

                                weighted_score_res, ind_scores_res, grade_res = st.session_state.generator.calculate_weighted_score(
                                    analysis_text_result, current_scoring_config_eval
                                )
                                st.session_state.vendor_score_results = {
                                    "weighted_score": weighted_score_res,
                                    "individual_scores": ind_scores_res,
                                    "grade": grade_res # Already cleaned by calculate_weighted_score
                                }
                                
                                # rfp_analysis is used as requirements context, already cleaned
                                gaps_res, risks_res = st.session_state.generator.identify_gaps_and_risks(
                                    st.session_state.vendor_proposal_text,
                                    st.session_state.rfp_analysis
                                )
                                st.session_state.vendor_gaps_risks = {"gaps": gaps_res, "risks": risks_res} # Results are cleaned

                                st.success("Vendor Analysis and Scoring Complete!")
                                st.rerun()
                            except Exception as e_analyze_vp:
                                st.error(f"Error analyzing vendor proposal: {str(e_analyze_vp)}")
                                st.session_state.vendor_analysis = remove_problematic_chars(f"Analysis Error: {str(e_analyze_vp)}")
                                st.session_state.vendor_score_results = None
                                st.session_state.vendor_gaps_risks = None


            if st.session_state.get('vendor_analysis'):
                st.markdown("---")
                st.header("Vendor Analysis Results")
                if st.session_state.get('vendor_score_results'):
                    score_res_display = st.session_state.vendor_score_results
                    st.subheader("📊 Scoring Summary")
                    if score_res_display['weighted_score'] is not None:
                        st.metric(label="Overall Weighted Score (Normalized)", value=f"{score_res_display['weighted_score']:.2f}")
                        st.metric(label="Grade", value=score_res_display['grade'] or "N/A") # grade is cleaned
                        
                        st.markdown("##### Individual Metric Scores (AI Assessed: 0-100):")
                        if score_res_display.get('individual_scores'):
                            metrics_disp = sorted(score_res_display['individual_scores'].keys())
                            cols_ind_scores = st.columns(min(len(metrics_disp), 5))
                            for i, metric_item_key in enumerate(metrics_disp):
                                score_val = score_res_display['individual_scores'].get(metric_item_key)
                                with cols_ind_scores[i % len(cols_ind_scores)]:
                                    # Metric name and score are cleaned
                                    st.metric(label=remove_problematic_chars(metric_item_key.replace('_', ' ').title()),
                                              value=str(score_val) if score_val is not None else "N/A")
                            st.caption("Overall Score uses configured weights. Individual scores are AI's raw assessment per metric.")
                        else: st.info("No individual metric scores extracted.")
                    else: 
                        st.warning("Could not calculate weighted score. Check AI analysis output or weights.")
                        st.write("Individual Scores Found (Raw AI):", score_res_display.get('individual_scores', "N/A"))

                if st.session_state.get('vendor_gaps_risks'):
                    gaps_risks_disp = st.session_state.vendor_gaps_risks
                    if gaps_risks_disp.get('gaps') or gaps_risks_disp.get('risks'):
                        st.subheader("⚠️ Identified Gaps & Risks (Beta)")
                        if gaps_risks_disp.get('gaps'):
                            st.markdown("##### Gaps:")
                            if gaps_risks_disp['gaps']:
                                for gap_item in gaps_risks_disp['gaps']: st.markdown(f"- {gap_item}") # Already cleaned
                            else: st.info("No significant gaps automatically identified.")
                        if gaps_risks_disp.get('risks'):
                            st.markdown("##### Risks:")
                            if gaps_risks_disp['risks']:
                                for risk_item in gaps_risks_disp['risks']: st.markdown(f"- {risk_item}") # Already cleaned
                            else: st.info("No significant risks automatically identified.")
                    elif gaps_risks_disp.get('gaps') is not None and gaps_risks_disp.get('risks') is not None:
                         st.info("No significant gaps or risks automatically identified based on current analysis.")
                
                st.subheader("🤖 Full AI Analysis Text")
                st.markdown(st.session_state.vendor_analysis) # Already cleaned

    # Tab 7: RFP Template Creator
    with tabs[6]:
        st.header("RFP Template Creator")
        col1_tab7, col2_tab7 = st.columns([2, 1])

        with col1_tab7:
            st.markdown("### Create RFP Template from Scratch")
            # company_objectives_input will be cleaned before use
            company_objectives_input = st.text_area("Company Objectives for this RFP", height=200, key="objectives_input_tab7")
            # template_type_selection will be cleaned before use
            template_type_selection = st.selectbox("Select Standard Template Type", 
                                                   st.session_state.config.get("proposal_settings", {}).get("templates", ["Standard RFP", "Technical RFP", "Commercial RFP"]) + ["Custom"], 
                                                   key="template_type_select_tab7")
            custom_template_name_input = ""
            if template_type_selection == "Custom":
                # custom_template_name_input will be cleaned before use
                custom_template_name_input = st.text_input("Custom Template Name", key="custom_template_name_tab7")

            if st.button("Generate RFP Template", type="primary", key="generate_rfp_template_button"):
                openai_key_check = st.session_state.config["api_keys"]["openai_key"] or os.environ.get("OPENAI_API_KEY")
                if not openai_key_check:
                    st.error("OpenAI API key is not configured for template generation.")
                else:
                    with st.spinner("Generating RFP template..."):
                        try:
                            # Inputs are cleaned before passing to drafter
                            cleaned_objectives = remove_problematic_chars(company_objectives_input)
                            final_template_type = remove_problematic_chars(custom_template_name_input if template_type_selection == "Custom" and custom_template_name_input else template_type_selection)
                            
                            drafter_instance = SpecialistRAGDrafter(openai_key_check)
                            template_content_result = drafter_instance.generate_rfp_template(cleaned_objectives, final_template_type)
                            st.session_state.rfp_template_content = template_content_result # Result is cleaned
                            st.success("RFP Template generated successfully!")
                            st.rerun()
                        except Exception as e_gen_rfp_temp:
                            st.error(f"Error generating RFP template: {str(e_gen_rfp_temp)}")
        
        with col2_tab7:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("### 📝 Template Creator Instructions")
            st.markdown("""
            1. Describe your company's objectives for issuing this RFP.
            2. Select a standard template type or choose 'Custom' and provide a name.
            3. Click "Generate RFP Template".
            4. Review and download the generated template below.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.rfp_template_content:
            st.markdown("---")
            st.header("Generated RFP Template Preview")
            st.markdown(st.session_state.rfp_template_content) # Already cleaned

            st.markdown("---")
            st.header("Download RFP Template")
            # Filename base uses cleaned inputs
            template_filename_base_dl = custom_template_name_input.replace(' ', '_') if template_type_selection == 'Custom' and custom_template_name_input else template_type_selection.replace(' ', '_')
            safe_template_filename_base = remove_problematic_chars(template_filename_base_dl)
            template_filename_dl = f"RFP_Template_{safe_template_filename_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
            
            st.download_button(
                label="Download RFP Template as Markdown",
                data=st.session_state.rfp_template_content, # Already cleaned
                file_name=template_filename_dl,
                mime="text/markdown",
                key="download_rfp_template_button"
            )
            
    # Tab 8: Independent SOW Analysis
    with tabs[7]:  # This is the 8th tab (0-indexed)
        st.header("Comprehensive SOW Analysis")
        
        # Initialize session state for SOW analysis
        if 'sow_analysis_results' not in st.session_state:
            st.session_state.sow_analysis_results = None
        if 'sow_client_goals' not in st.session_state:
            st.session_state.sow_client_goals = ""
        if 'sow_rfp_text' not in st.session_state:
            st.session_state.sow_rfp_text = None
        if 'sow_rfp_processed' not in st.session_state:
            st.session_state.sow_rfp_processed = False
        if 'sow_current_file' not in st.session_state:
            st.session_state.sow_current_file = None
        if 'sow_analysis_complete' not in st.session_state:
            st.session_state.sow_analysis_complete = False
        
        # Step 1: Document Upload Section
        st.markdown("### Step 1: Upload RFP Document")
        uploaded_rfp_sow = st.file_uploader(
            "Upload RFP Document for SOW Analysis", 
            type=["docx", "pdf", "txt", "md"], 
            key="upload_rfp_sow_analysis",
            help="Upload the RFP document that you want to analyze and create a comprehensive SOW for."
        )
        
        # Process uploaded document
        if uploaded_rfp_sow is not None:
            current_file_info = f"{uploaded_rfp_sow.name}_{uploaded_rfp_sow.size}"
            
            # Only process if it's a new file or file has changed
            if st.session_state.sow_current_file != current_file_info:
                temp_file_path = ""
                try:
                    file_extension = os.path.splitext(uploaded_rfp_sow.name)[1]
                    if not file_extension:
                        file_extension = ".tmp"
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file_obj:
                        temp_file_obj.write(uploaded_rfp_sow.getvalue())
                        temp_file_path = temp_file_obj.name
                    
                    # Process the RFP
                    rfp_text = process_rfp(temp_file_path)
                    st.session_state.sow_rfp_text = rfp_text
                    st.session_state.sow_current_file = current_file_info
                    st.session_state.sow_rfp_processed = True
                    st.session_state.sow_analysis_complete = False  # Reset analysis state
                    st.session_state.sow_analysis_results = None   # Clear previous results
                    
                    st.success(f"✅ Successfully processed {uploaded_rfp_sow.name}")
                    
                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    st.session_state.sow_rfp_processed = False
                finally:
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
        
        # Reset states if no file is uploaded
        elif uploaded_rfp_sow is None:
            st.session_state.sow_rfp_text = None
            st.session_state.sow_rfp_processed = False
            st.session_state.sow_current_file = None
            st.session_state.sow_analysis_complete = False
            st.session_state.sow_analysis_results = None

        # Show document preview and next steps
        if st.session_state.sow_rfp_processed and st.session_state.sow_rfp_text:
            # Document preview
            with st.expander("📄 Preview RFP Document Content", expanded=False):
                st.text_area("RFP Content", st.session_state.sow_rfp_text, height=300, key="sow_rfp_preview")
            
            st.markdown("---")
            
            # Step 2: Strategic Goals Input (Optional)
            st.markdown("### Step 2: Client Strategic Context (Optional)")
            st.markdown("*Provide additional context about the client's strategic objectives to enhance SOW alignment*")
            
            col1_goals, col2_goals = st.columns([3, 1])
            
            with col1_goals:
                sow_client_goals = st.text_area(
                    "Client Strategic Goals & Business Priorities:",
                    value=st.session_state.sow_client_goals,
                    height=120,
                    placeholder="e.g., Digital transformation to improve operational efficiency by 30%, enhance customer satisfaction, achieve regulatory compliance, reduce costs by 20%, etc.",
                    key="sow_client_goals_input_independent"
                )
                
                if sow_client_goals != st.session_state.sow_client_goals:
                    st.session_state.sow_client_goals = sow_client_goals
            
            with col2_goals:
                st.info("""
                **💡 What to include:**
                - Business transformation goals
                - Operational objectives  
                - Strategic priorities
                - Performance targets
                - Industry challenges
                - Regulatory requirements
                """)
            
            st.markdown("---")
            
            # Step 3: Generate SOW Analysis
            st.markdown("### Step 3: Generate Comprehensive SOW Analysis")
            
            col1_generate, col2_info = st.columns([2, 1])
            
            with col1_generate:
                if not st.session_state.generator:
                    st.error("⚠️ OpenAI API key is not configured or Generator not initialized.")
                    st.info("Please check your API configuration in the settings.")
                else:
                    # Show analysis button
                    if not st.session_state.sow_analysis_complete:
                        if st.button("🚀 Generate Comprehensive SOW Analysis", type="primary", key="generate_sow_analysis_independent"):
                            with st.spinner("🔄 Generating comprehensive SOW analysis... This may take 3-5 minutes."):
                                try:
                                    # Check if the method exists in the generator
                                    if not hasattr(st.session_state.generator, 'generate_comprehensive_sow_analysis'):
                                        st.error("❌ SOW analysis method not found. Please update your generation_engine.py with the SOW integration code.")
                                        st.info("Add the generate_comprehensive_sow_analysis method to the EnhancedProposalGenerator class.")
                                    else:
                                        # Generate comprehensive SOW analysis
                                        progress_bar = st.progress(0)
                                        status_text = st.empty()
                                        
                                        status_text.text("🔍 Extracting requirements...")
                                        progress_bar.progress(20)
                                        
                                        sow_results = st.session_state.generator.generate_comprehensive_sow_analysis(
                                            st.session_state.sow_rfp_text,
                                            st.session_state.sow_client_goals if st.session_state.sow_client_goals else None
                                        )
                                        
                                        progress_bar.progress(100)
                                        status_text.text("✅ Analysis complete!")
                                        
                                        st.session_state.sow_analysis_results = sow_results
                                        st.session_state.sow_analysis_complete = True
                                        
                                        # Clear progress indicators
                                        progress_bar.empty()
                                        status_text.empty()
                                        
                                        st.success("🎉 Comprehensive SOW Analysis Complete!")
                                        st.balloons()
                                        st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Error generating SOW analysis: {str(e)}")
                                    import traceback
                                    with st.expander("🐛 Debug Information", expanded=False):
                                        st.code(traceback.format_exc())
                    else:
                        st.success("✅ SOW Analysis Complete!")
                        if st.button("🔄 Regenerate Analysis", type="secondary", key="regenerate_sow_analysis"):
                            st.session_state.sow_analysis_complete = False
                            st.session_state.sow_analysis_results = None
                            st.rerun()
            
            with col2_info:
                st.markdown("**📋 Analysis Includes:**")
                st.markdown("""
                🔍 **Requirements Extraction**
                - Functional & Technical
                - Operational & Business
                - Compliance & Regulatory
                
                📊 **Structured SOW**
                - Hierarchical breakdown
                - Tasks & Sub-tasks
                - Clear deliverables
                
                📈 **Bill of Quantities** 
                - Resource estimation
                - Timeline planning
                - Effort calculations
                
                🎯 **Strategic Summary**
                - Executive overview
                - Value alignment
                - Implementation roadmap
                """)
        
        else:
            # No document uploaded yet
            st.info("👆 Please upload an RFP document above to begin the SOW analysis process.")
            
            # Show overview of the process
            st.markdown("### 📋 How SOW Analysis Works:")
            
            process_cols = st.columns(4)
            
            with process_cols[0]:
                st.markdown("""
                **🔄 Step 1: Upload**
                - Upload RFP document
                - Automatic text extraction
                - Document validation
                """)
            
            with process_cols[1]:
                st.markdown("""
                **🎯 Step 2: Context**
                - Add strategic goals
                - Business priorities
                - Optional but recommended
                """)
            
            with process_cols[2]:
                st.markdown("""
                **🚀 Step 3: Generate**
                - AI-powered analysis
                - Comprehensive extraction
                - Structured output
                """)
            
            with process_cols[3]:
                st.markdown("""
                **📊 Step 4: Review**
                - Multiple components
                - Download options
                - Export capabilities
                """)

        # Display SOW Analysis Results
        if st.session_state.sow_analysis_complete and st.session_state.sow_analysis_results:
            st.markdown("---")
            st.markdown("## 📊 SOW Analysis Results")
            
            # Summary metrics
            col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
            
            with col_metric1:
                st.metric("📋 Components", "5", help="Number of analysis components generated")
            
            with col_metric2:
                requirements_count = len(st.session_state.sow_analysis_results.get('comprehensive_requirements', '').split('###'))
                st.metric("🔍 Requirement Categories", f"{requirements_count}", help="Number of requirement categories identified")
            
            with col_metric3:
                # Estimate phases from SOW structure
                sow_content = st.session_state.sow_analysis_results.get('structured_sow', '')
                phases_count = sow_content.count('### PHASE') if sow_content else 0
                st.metric("📊 Project Phases", f"{phases_count}", help="Number of project phases structured")
            
            with col_metric4:
                st.metric("📄 Document Processed", "✅", help="RFP document successfully analyzed")
            
            st.markdown("---")
            
            # Create tabs for different SOW components
            sow_tabs = st.tabs([
                "📋 Executive Summary", 
                "🔍 Requirements Analysis", 
                "📊 Structured SOW", 
                "📈 Bill of Quantities",
                "🔬 RFP Analysis"
            ])
            
            # Executive Summary Tab
            with sow_tabs[0]:
                st.markdown("### 🎯 Strategic Executive Summary")
                if st.session_state.sow_analysis_results.get('strategic_executive_summary'):
                    st.markdown(st.session_state.sow_analysis_results['strategic_executive_summary'])
                    
                    # Download option
                    summary_content = st.session_state.sow_analysis_results['strategic_executive_summary']
                    st.download_button(
                        label="📥 Download Executive Summary",
                        data=summary_content,
                        file_name=f"Executive_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_exec_summary_independent"
                    )
                else:
                    st.warning("⚠️ Executive summary not available")
            
            # Requirements Analysis Tab
            with sow_tabs[1]:
                st.markdown("### 🔍 Comprehensive Requirements Analysis")
                if st.session_state.sow_analysis_results.get('comprehensive_requirements'):
                    st.markdown(st.session_state.sow_analysis_results['comprehensive_requirements'])
                    
                    # Download option
                    req_content = st.session_state.sow_analysis_results['comprehensive_requirements']
                    st.download_button(
                        label="📥 Download Requirements Analysis",
                        data=req_content,
                        file_name=f"Requirements_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_requirements_independent"
                    )
                else:
                    st.warning("⚠️ Requirements analysis not available")
            
            # Structured SOW Tab
            with sow_tabs[2]:
                st.markdown("### 📊 Structured Scope of Work")
                if st.session_state.sow_analysis_results.get('structured_sow'):
                    st.markdown(st.session_state.sow_analysis_results['structured_sow'])
                    
                    # Download option
                    sow_content = st.session_state.sow_analysis_results['structured_sow']
                    st.download_button(
                        label="📥 Download Structured SOW",
                        data=sow_content,
                        file_name=f"Structured_SOW_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_sow_independent"
                    )
                else:
                    st.warning("⚠️ Structured SOW not available")
            
            # Bill of Quantities Tab
            with sow_tabs[3]:
                st.markdown("### 📈 Bill of Quantities")
                if st.session_state.sow_analysis_results.get('bill_of_quantities'):
                    st.markdown(st.session_state.sow_analysis_results['bill_of_quantities'])
                    
                    # Download option
                    boq_content = st.session_state.sow_analysis_results['bill_of_quantities']
                    st.download_button(
                        label="📥 Download Bill of Quantities",
                        data=boq_content,
                        file_name=f"Bill_of_Quantities_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_boq_independent"
                    )
                else:
                    st.warning("⚠️ Bill of quantities not available")
            
            # RFP Analysis Tab
            with sow_tabs[4]:
                st.markdown("### 🔬 Detailed RFP Analysis")
                if st.session_state.sow_analysis_results.get('rfp_analysis'):
                    st.markdown(st.session_state.sow_analysis_results['rfp_analysis'])
                    
                    # Download option
                    analysis_content = st.session_state.sow_analysis_results['rfp_analysis']
                    st.download_button(
                        label="📥 Download RFP Analysis",
                        data=analysis_content,
                        file_name=f"RFP_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_rfp_analysis_independent"
                    )
                else:
                    st.warning("⚠️ RFP analysis not available")
            
            # Export all SOW components
            st.markdown("---")
            st.markdown("### 📦 Export Complete SOW Package")
            
            col_export1, col_export2, col_export3 = st.columns(3)
            
            with col_export1:
                if st.button("📄 Export as Word Document", type="secondary", key="export_sow_word_independent"):
                    try:
                        # Create combined document content
                        combined_content = {
                            "Executive Summary": st.session_state.sow_analysis_results.get('strategic_executive_summary', ''),
                            "Requirements Analysis": st.session_state.sow_analysis_results.get('comprehensive_requirements', ''),
                            "Structured SOW": st.session_state.sow_analysis_results.get('structured_sow', ''),
                            "Bill of Quantities": st.session_state.sow_analysis_results.get('bill_of_quantities', ''),
                            "RFP Analysis": st.session_state.sow_analysis_results.get('rfp_analysis', '')
                        }
                        
                        # Use existing export function
                        output_dir = "exported_proposals"
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"Complete_SOW_Analysis_{timestamp}.docx"
                        output_path = os.path.join(output_dir, filename)
                        
                        # Create proposal data structure for export
                        sow_proposal_data = {
                            "sections": combined_content,
                            "client_name": "Client Organization"  # Default since this is independent
                        }
                        
                        export_path = export_to_word(
                            sow_proposal_data,
                            st.session_state.config["company_info"]["name"],
                            sow_proposal_data["client_name"],
                            output_path
                        )
                        
                        if export_path and os.path.exists(export_path):
                            with open(export_path, "rb") as file:
                                st.download_button(
                                    label="📥 Download Word Document",
                                    data=file,
                                    file_name=filename,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key="download_complete_sow_word_independent"
                                )
                        
                    except Exception as e:
                        st.error(f"❌ Error exporting SOW: {str(e)}")
            
            with col_export2:
                # Export as combined markdown
                if st.button("📝 Export as Markdown", type="secondary", key="export_sow_markdown_independent"):
                    combined_markdown = f"""# Comprehensive SOW Analysis
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
{st.session_state.sow_analysis_results.get('strategic_executive_summary', 'Not available')}

## Requirements Analysis
{st.session_state.sow_analysis_results.get('comprehensive_requirements', 'Not available')}

## Structured Scope of Work
{st.session_state.sow_analysis_results.get('structured_sow', 'Not available')}

## Bill of Quantities
{st.session_state.sow_analysis_results.get('bill_of_quantities', 'Not available')}

## RFP Analysis
{st.session_state.sow_analysis_results.get('rfp_analysis', 'Not available')}
"""
                    
                    st.download_button(
                        label="📥 Download Combined Markdown",
                        data=combined_markdown,
                        file_name=f"Complete_SOW_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key="download_combined_markdown_independent"
                    )
            
            with col_export3:
                # Export as PDF option (if available)
                if st.button("📑 Export as PDF", type="secondary", key="export_sow_pdf_independent"):
                    try:
                        # Create combined document content for PDF
                        combined_content = {
                            "Executive Summary": st.session_state.sow_analysis_results.get('strategic_executive_summary', ''),
                            "Requirements Analysis": st.session_state.sow_analysis_results.get('comprehensive_requirements', ''),
                            "Structured SOW": st.session_state.sow_analysis_results.get('structured_sow', ''),
                            "Bill of Quantities": st.session_state.sow_analysis_results.get('bill_of_quantities', ''),
                            "RFP Analysis": st.session_state.sow_analysis_results.get('rfp_analysis', '')
                        }
                        
                        # Use existing export function
                        output_dir = "exported_proposals"
                        if not os.path.exists(output_dir):
                            os.makedirs(output_dir)
                        
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"Complete_SOW_Analysis_{timestamp}.pdf"
                        output_path = os.path.join(output_dir, filename)
                        
                        # Create proposal data structure for export
                        sow_proposal_data = {
                            "sections": combined_content,
                            "client_name": "Client Organization"
                        }
                        
                        export_path = export_to_pdf(
                            sow_proposal_data,
                            st.session_state.config["company_info"]["name"],
                            sow_proposal_data["client_name"],
                            output_path
                        )
                        
                        if export_path and os.path.exists(export_path):
                            with open(export_path, "rb") as file:
                                st.download_button(
                                    label="📥 Download PDF Document",
                                    data=file,
                                    file_name=filename,
                                    mime="application/pdf",
                                    key="download_complete_sow_pdf_independent"
                                )
                        
                    except Exception as e:
                        st.error(f"❌ Error exporting PDF: {str(e)}")
                        st.info("PDF export requires the 'fpdf' library. Install with: pip install fpdf")
                        
if __name__ == "__main__":
    main()