#!/usr/bin/env bash

sudo apt-get update
sudo add-apt-repository ppa:jonathonf/python-3.6
sudo apt-get install python3.6 python3-pip virtualenv node.js npm sqlite3 make unzip wget xvfb
# xvfb to run chrome headless

# install chromedriver
if ! [ -x /usr/local/share/chromedriver ]; then
    wget -N http://chromedriver.storage.googleapis.com/2.26/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    chmod +x chromedriver
    sudo mv -f chromedriver /usr/local/share/chromedriver
    sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver
    sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver
    rm chromedriver_linux64.zip
fi

# install chrome browser
tput setaf 5
echo
echo '  ----> Installing chrome browser, continue? [yN]'
echo
tput sgr0
read choice
case $choice in
    [yY][eE][sS]|[yY])
        sudo apt-get install libxss1 libappindicator1 libindicator7
        wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
        sudo dpkg -i google-chrome*.deb
        sudo apt-get install -f
        rm google-chrome*.deb
        ;;
esac

