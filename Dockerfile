# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# For Chinese users
#RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
#    pip install poetry && \
#    poetry source add --priority=default mirrors https://pypi.tuna.tsinghua.edu.cn/simple/ && \
#    pip install apt-smart && \
#    apt-smart -a

# Install any needed packages specified in pyproject.toml
RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --only main

# Option: added font Noto Sans SC
# you can remove this if you don't need it
# but don't forget to added other font
# For Chinese users, comment line 27 and uncomment line 28 to use jsDelivr mirror of Noto Sans
RUN apt update && apt install -y wget fontconfig && \
    wget -P /usr/share/fonts/opentype https://github.com/googlefonts/noto-cjk/raw/main/Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf && \
    # wget -P /usr/share/fonts/opentype https://cdn.jsdelivr.net/gh/googlefonts/noto-cjk/Sans/Variable/TTF/Subset/NotoSansSC-VF.ttf && \
    fc-cache -fv

# Make port 80 and 12345 available to the world outside this container
EXPOSE 12345

# Run main.py when the container launches
CMD ["python", "main.py"]