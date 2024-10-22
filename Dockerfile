# ベースイメージ
FROM python:3.10.15

# 作業ディレクトリの設定
WORKDIR /app

RUN apt-get update && apt-get install -y cmake build-essential libboost-dev
RUN pip install --upgrade setuptools wheel
RUN pip install pyarrow --upgrade --prefer-binary
RUN pip install streamlit

# ポートの指定
EXPOSE 8501