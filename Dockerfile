FROM ophub/armbian-trixie:arm64
COPY . /app
WORKDIR /app
CMD python3 mqtt.py
