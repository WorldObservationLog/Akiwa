# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in pyproject.toml
RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --only main

# Option: added font Noto Sans SC
# you can remove this if you don't need it
# but don't forget to added other font
RUN apt update && apt install -y \
  fontconfig \
  wget && \
  mkdir -p /usr/share/fonts/opentype/noto && \
  wget -O font.ttf "https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf" && \
  mv font.ttf /usr/share/fonts/opentype/noto/ && \
  fc-cache -fv && \
  apt remove -y wget && \
  apt autoremove -y && \
  rm -rf /var/lib/apt/lists/* && \
  rm -rf /tmp/*

# Make port 80 and 12345 available to the world outside this container
EXPOSE 12345

# Run main.py when the container launches
CMD ["python", "main.py"]