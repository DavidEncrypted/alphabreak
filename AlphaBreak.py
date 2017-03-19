import captcha.captcha as capm
import os, sys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from fann2 import libfann
import random, uuid
cap = capm.Captcha(length=7)
ann = libfann.neural_net()
ann.create_from_file("ann_fin.net")
letters = "abcdefghklmnprstuvwyzABDEFGHIJKLMNRTUXY23456789"

usernameinp = sys.argv[1]
print "Username: " + usernameinp
def toInput(seg):
    input = []
    for x in range(seg.size[0]):
        for y in range(seg.size[1]):
            p = (x, y)
            col = seg.getpixel(p)

            norm = (((col / 255.00) * 2.00) - 1.00) * -1.00
            input.append(norm)
    return input

def use_ann(segs):

    #print len(segs)
    answer = ""
    #print answer
    for seg in segs:
        inputann = toInput(seg)
        outputann = ann.run(inputann)
        max = [-1, 0]
        for x in range(len(outputann)):
            if outputann[x] > max[0]:
                max = [outputann[x],x]
        #print max[0], max[1], letters[max[1]]
        #print letters[max[1]]
        answer += letters[max[1]]
        #print answer
    return answer




# path to the firefox binary inside the Tor package
binary = '/Applications/TorBrowser.app/Contents/MacOS/firefox'
if os.path.exists(binary) is False:
    raise ValueError("The binary path to Tor firefox does not exist.")
firefox_binary = FirefoxBinary(binary)


browser = None
def get_browser(binary=None):
    global browser
    # only one instance of a browser opens, remove global for multiple instances
    if not browser:
        browser = webdriver.Firefox(firefox_binary=binary)
    return browser

def getcap():
    global browser
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #get element captcha
    htmlcap = browser.find_element_by_id('captcha')
    #save screenshot
    browser.save_screenshot('screenshot.png')
    #get location in screenshot
    caploc = (200, 593)  # int(htmlcap.location.get('y')))
    #print caploc
    capsize = (215, 80)
    imcap = Image.open('screenshot.png').convert('L')
    #imcap.show()
    #fullcap = imcap.crop((caploc[0], caploc[1], caploc[0] + capsize[0], caploc[1] + capsize[1]))
    fullcap = imcap.crop((259, 393, 259 + 215, 393 + 80))
    #imcap.crop((200, 200, 400, 400)).show()
    #print fullcap.size
    #fullcap.show()
    return fullcap

def fill_form(answer, curr):
    global browser
    global usernameinp
    username = "{}{}".format(usernameinp, curr)
    password = "VerySecurePass{}".format(curr)
    pin = "{}".format(random.randint(100000,999999))
    browser.find_element_by_name("da_username").clear()
    browser.find_element_by_name("da_username").send_keys(username)
    browser.find_element_by_name("da_passwd").send_keys(password)
    browser.find_element_by_name("da_passcf").send_keys(password)
    browser.find_element_by_name("da_pin").send_keys(pin)
    browser.find_element_by_name("captcha_code").send_keys(answer)

    browser.find_element_by_class_name("bstd").click()

    try:
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.NAME, "mne"))
        )

        print "username: ", username, "password", password
        print "pin: ", pin
        #print "woopwoop"
        return 1
    except:
        #print "Nope"
        return 0



if __name__ == "__main__":
    browser = get_browser(binary=firefox_binary)
    finished = 0
    current = 0
    while finished == 0:

        browser.get('http://pwoah7foa6au2pul.onion/register.php')
        done = 0
        WebDriverWait(browser, 1000).until(
            EC.presence_of_element_located((By.NAME, "da_username"))
        )
        while done == 0:
            failure = 0
            do = 1
            answ = "AAAAAAA"
            while do == 1:
                capim = getcap()
                #capim.show()
                cap.update_cap(capim)
                fail = cap.segment()
                if fail == 1:
                    do = 0
                else:
                    #print "failure"
                    #failure = 1
                    answ = 'aaaaaaa'
                    do = 0
            if failure != 1:
                answ = use_ann(cap.get_segments())
                #print answ
            done = fill_form(answ, current)
            #if done == 0:
            #    browser.refresh()

        mnm = browser.find_element_by_css_selector('p.std:nth-child(3)')
        #print mnm.text
        browser.find_element_by_name('mne').send_keys(mnm.text)
        browser.find_element_by_class_name('bstd').click()
        #print 'waiting'
        WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.std:nth-child(7)"))
        )
        #print 'found'
        pressed = 0
        while pressed == 0:
            try:

                browser.find_element_by_css_selector('a.std:nth-child(7)').click()
                browser.get('http://pwoah7foa6au2pul.onion/register.php')
            except:
                pressed = 1


        current += 1
    #browser.quit()