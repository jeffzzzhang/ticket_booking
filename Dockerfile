FROM python:3.9.8
WORKDIR /hotel_promotion
COPY . .
# RUN pip install -r requirements.txt
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
CMD ["python", "app.py"]