import time
import subprocess
import os
import pyperclip
import pandas as pd
import numpy as np

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMessageBox,QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.Qt import *

from selenium import webdriver
# import chromedriver_autoinstaller
import chromedriver_autoinstaller


from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager

import threading
import random


