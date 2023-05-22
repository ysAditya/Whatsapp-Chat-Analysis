mkdir -p ~/.streamlit/
echo "[general]" > ~/.streamlit/credentials.toml
echo "email = \"\"" >> ~/.streamlit/credentials.toml
echo "[s3]" >> ~/.streamlit/credentials.toml
echo "region = \"us-west-2\"" >> ~/.streamlit/credentials.toml
echo "[run]" >> ~/.streamlit/credentials.toml
echo "production = true" >> ~/.streamlit/credentials.toml
