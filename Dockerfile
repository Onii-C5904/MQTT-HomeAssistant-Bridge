FROM ophub/armbian-trixie:arm64
COPY ./mqtt.py /app/mqtt.py
COPY ./iio.py /app/iio.py
COPY ./helper.py /app/helper.py
WORKDIR /app
CMD python3 mqtt.py