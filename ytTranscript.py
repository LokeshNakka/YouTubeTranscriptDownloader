import json
import re
import time
import pandas
import requests

from YT_TLangs import *
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class CCNotAvailable(Exception):
    pass


driver_path = ChromeDriverManager().install()


def sub_TimeStamp(tms):
    return f"{pandas.Timestamp(tms, unit='ms').strftime('%H:%M:%S')},{tms % 1000}"


def GetBrowser(isHeadless=True):
    opt = Options()
    if isHeadless:
        opt.add_argument("--headless")
    opt.add_argument("--mute-audio")
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    try:
        return Chrome(service=Service(driver_path), desired_capabilities=capabilities, options=opt)
    except Exception as err:
        print(err)
        return Chrome(driver_path, desired_capabilities=capabilities, options=opt)


def Download(vid, tlang=None):
    url = f'https://www.youtube.com/watch?v={vid}'

    driver = GetBrowser()

    while True:
        try:
            driver.get(url)
            break
        except Exception as err:
            print(err)
            time.sleep(2)

    try:
        cc_element = WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="ytp-subtitles-button ytp-button"]')))
        cc_element.click()
    except Exception as err:
        print(err)
        raise CCNotAvailable('CC Not Available For This Video')

    perf_logs = driver.get_log('performance')[::-1]
    for ind, log in enumerate(perf_logs):
        s = f'\n{str(log)}'
        links = re.findall(r'https://www.youtube.com/api/timedtext[^"]+', s)
        if len(links) > 0:
            while True:
                try:
                    url = links[-1]
                    response = requests.get(url if tlang is None else f'{url}&tlang={tlang}')
                    events = response.json()['events']

                    with open('subtitles.json', 'w') as jFile:
                        json.dump(response.json(), jFile)

                    subtitles_entries = []
                    sub_index = 1

                    for index, entry in enumerate(events):
                        segs = entry.get('segs', None)
                        if segs is not None:
                            dialogue = ''.join([_.get('utf8', '') for _ in segs]).strip('\n')
                            if len(dialogue) == 0:
                                continue
                            else:
                                tStartMs = entry.get('tStartMs', 0)
                                tEndMs = events[index + 1].get('tStartMs', None) if index + 1 < len(
                                    events) else entry.get('dDurationMs', 0) + tStartMs
                                s_entry = f'{sub_index}\n{sub_TimeStamp(tStartMs)} --> {sub_TimeStamp(tEndMs)}\n{dialogue}\n'
                                subtitles_entries.append(s_entry)
                                sub_index += 1

                    with open('subtitles.srt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(subtitles_entries))
                    break
                except Exception as err:
                    print(err)
                    time.sleep(1)
            break
        elif len(perf_logs)-1 == ind:
            raise CCNotAvailable('CC Not Found In Network.Request')


if __name__ == '__main__':
    Download('EDul4jJQA2I', tlang=TLangs.English)
