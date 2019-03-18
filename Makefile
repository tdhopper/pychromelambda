

deploy: bin
	serverless deploy

bin: bin/chromedriver bin/headless-chrome

bin/chromedriver:
	curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
	unzip chromedriver.zip -d bin/
	rm chromedriver.zip

bin/headless-chrome:
	mkdir -p bin/
	curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
	unzip headless-chromium.zip -d bin/
	rm headless-chromium.zip

