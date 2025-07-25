# sunsets
Predicting beautiful sunsets

## Streamlit App

This repository includes a Streamlit app in `streamlit_app.py` which displays the
sunset score for a chosen location. Popular cities (including Tel Aviv) are
available in a dropdown and coordinates can be selected on an interactive map.

### Local Development

Install the dependencies and run the app:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Free Hosting

You can deploy the app for free on [Streamlit Community Cloud](https://streamlit.io/cloud).
Create a new app pointing to this repository and select `streamlit_app.py` as the
entry point.
