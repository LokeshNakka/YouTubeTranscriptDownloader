import json
import re
import time
import pandas
import requests

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


def Download(vid, tlang=None):
    url = f'https://www.youtube.com/watch?v={vid}'
    opt = Options()
    opt.add_argument("--headless")
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    driver = Chrome(
        service=Service(driver_path),
        desired_capabilities=capabilities,
        options=opt
    )
    driver.get(url)
    try:
        cc_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="ytp-subtitles-button ytp-button"]')))
        cc_element.click()
    except:
        raise CCNotAvailable('CC Not Available For This Video')

    s = ''
    for i in driver.get_log('performance'):
        s += f'\n{str(i)}'
    links = re.findall(r'https://www.youtube.com/api/timedtext[^"]+', s)
    if len(links) > 0:
        while True:
            try:
                url = links[-1]
                response = requests.get(url if tlang is None else f'{url}&tlang={tlang}')
                events = response.json()['events']
                with open('sub.json', 'w')as jfile:
                    json.dump(response.json(), jfile)
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
                            tEndMs = events[index + 1].get('tStartMs', None) if index + 1 < len(events) else entry.get(
                                'dDurationMs', 0) + tStartMs
                            s_entry = f'{sub_index}\n{sub_TimeStamp(tStartMs)} --> {sub_TimeStamp(tEndMs)}\n{dialogue}\n'
                            subtitles_entries.append(s_entry)
                            sub_index += 1
                with open('sub.srt', 'w', encoding='utf-8') as f:
                    f.write('\n'.join(subtitles_entries))

                break
            except:
                time.sleep(.5)
    else:
        raise CCNotAvailable('CC Not Found In Network.Request')


if __name__ == '__main__':
    Download('EDul4jJQA2I', tlang=None)
