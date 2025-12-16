import streamlit as st

def inject_global_styles():
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        .kiosk-hero {
          padding: 16px;
          border-radius: 14px;
          border: 1px solid rgba(255,255,255,0.08);
          background: rgba(255,255,255,0.02);
          margin-bottom: 16px;
        }
        .kiosk-hero h2 { margin: 0; }

        .kiosk-card {
            padding: 18px 18px 6px 18px;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            background: rgba(255,255,255,0.03);
            margin-bottom: 16px;
        }
        .kiosk-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .ticket {
            border: 1px dashed rgba(255,255,255,0.22);
            border-radius: 14px;
            padding: 16px;
            background: rgba(255,255,255,0.02);
        }
        .small-muted {
            opacity: 0.75;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="kiosk-hero">
          <h2>{title}</h2>
          <div class="small-muted">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
