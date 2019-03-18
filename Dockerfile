FROM lambci/lambda:build-python3.6
RUN pip install selenium ipython pillow
CMD bash
