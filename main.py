from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger

from urllib3.connectionpool import log as urllibLogger
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep
from random import randint, choice
import sqlite3, logging, schedule


USERNAME = "dalleuniverse"
PASSWORD = "G91687278@"
INSTA_LOGIN_PAGE = "https://www.instagram.com/accounts/login/"
INSTA_TAG_PAGE = 'https://www.instagram.com/explore/tags/'


comment_list = [
    'Nice!', 'This is amazing', 'Very cool!', 'This looks so cool', 'Love it', 'Awesome!', 'WHOA', 'Fantastic!', 'Cool', 'Lovelyyy',
    '🔥', '👏👏👏👏', '❤️🧡💛💚💙💜', '🙌🙌', '🏆', '😍', '❤️🙌🔥👏', '😮', '🎨❤️', '🙌👽',
    'Surreal!!!', 'Omg yes', 'It was very good.', 'Deep 🙌', 'Beautiful', 'Nailed it.', 'Very nice, keep posting!', 'WOW!', 'UNREAL!', ':0',
    "That's insane!", 'Fireeeee', 'Good job', 'Interesting!', 'Accurate!', 'Really cool pic!', 'Need', 'OMG 😳', 'That details', 'Hard',
    'Yup', 'Soooo good!!!!!', 'Just wooow', 'Constantly amazed <3', 'Is crazy', 'So great!!', 'MADNESS', 'This is mind-blowing!', "Yep that's it!", 'Magical',
    'Holy…', 'Haha cool one', 'Perfect!', 'increíble', 'Genius!! 😍', 'Bruh', 'Daaaaaaaaaaaaaaaaamn', 'Well done.', 'Letsgo!!', "Best photo I've seen today!",
]

tag_list = [
    'dalle', 'dalle', 'dalle2', 'ai', 'openai', 'art', 'digitalart', 'alart', 'generativeart', 
    'artificialintelligence', 'aiartcommunity', 'abstractart', 'aiartists', 'neuralart', 
    'contemporaryart', 'deepdream', 'artist', 'artoftheday', 'newmediaart', 'nightcafestudio', 'aiartist', 
    'modernart', 'neuralnetworks', 'neuralnetworkart', 'abstract', 'styletransfer', 'digitalartist', 'artificial',
]


def insert_post(post):
    """
    Function to insert a post into the database
    """

    conn = sqlite3.connect('insta.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts(post TEXT)')
    c.execute("INSERT INTO posts VALUES (?)", (post,))
    conn.commit()
    conn.close()


def check_post(post):
    """
    Function to check if a post is already in the database
    """

    conn = sqlite3.connect('insta.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS posts(post TEXT)')
    c.execute('SELECT * FROM posts')
    for row in c.fetchall():
        if post in row:
            return True
    conn.close()
    return False


def job():
    """
    Function to run the Instagram bot.
    """

    firefox_options = Options()
    firefox_options.add_argument('--disable-logging')
    firefox_options.add_argument("--log-level=OFF")
    firefox_options.add_argument("--headless")
    firefox_options.headless = True

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
    driver.get(INSTA_LOGIN_PAGE)
    wait = WebDriverWait(driver, 20)
    sleep(randint(2, 5))
    wait.until(EC.element_to_be_clickable((By.NAME, 'username'))).send_keys(USERNAME)
    wait.until(EC.element_to_be_clickable(( By.NAME, "password"))).send_keys(PASSWORD)
    sleep(randint(2, 5))
    wait.until(EC.element_to_be_clickable(( By.NAME, "password"))).send_keys(Keys.RETURN)
    sleep(5)

    def validate_login():
        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "eiCW-"))).text
            print('\nError: Login failed\n\n'+'-='*20+'\n\n')
            return False
        except:
            print(f'\n{USERNAME} logged in\n\n'+'-='*20+'\n\n')
            return True

    if validate_login() == True:
        tag_link = INSTA_TAG_PAGE+choice(tag_list)
        driver.get(tag_link)
        wait = WebDriverWait(driver, 20)
        sleep(10)

        links = []
        number_of_posts = randint(40, 120)
        limit = 0

        while limit < 30:
            hrefElements = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//a[@href]")))
            elements_link = [x.get_attribute("href") for x in hrefElements]
            for link in elements_link:
                if '/p/' in link:
                    if not check_post(link):
                        if link not in links:
                            links.append(link)

            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            driver.implicitly_wait(5)
            if len(links) >= number_of_posts:
                break

            links = links[:number_of_posts]
            limit = limit + 1
        
        print(f'Posts found: {len(links)}\n')
        for link in links:
            try:
                driver.get(link)
                wait = WebDriverWait(driver, 20)
                sleep(randint(10, 40))
                like_button = None

                try:
                    like_button = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@class="_aamw"]/button')))
                    like_button.click()

                except:
                    driver.execute_script('arguments[0].click();', like_button)  

                print("Liked: " + link)
                insert_post(link)

                if randint(1, 25) == 1:
                    commentSection = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
                    commentSection.click()
                    commentSection = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")))
                    commentSection.send_keys(choice(comment_list))
                    commentSection.send_keys(Keys.ENTER)
                    print("Commented: " + link)

                sleep(randint(4, 8))

            except Exception as e:
                print('Error: ' + str(e))

    driver.close()
    print('\nJob done!\n')


schedule.every().day.at("20:34:42").do(job)
schedule.every().day.at("23:31:31").do(job)
schedule.every().day.at("02:35:45").do(job)
schedule.every().day.at("05:28:15").do(job)
schedule.every().day.at("08:44:22").do(job)
schedule.every().day.at("11:34:01").do(job)
schedule.every().day.at("14:23:55").do(job)
schedule.every().day.at("17:42:52").do(job)


if __name__ == "__main__":
    print('Program started!\n')
    seleniumLogger.setLevel(logging.WARNING)
    urllibLogger.setLevel(logging.WARNING)
    
    while True:
        try:
            schedule.run_pending()
            sleep(60)

        except KeyboardInterrupt:
            print('\nExiting...\n')
            break

        except Exception as e:
            print('Error: ' + str(e))
            sleep(60)
            continue

