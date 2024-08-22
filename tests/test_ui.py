from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import unittest
import os

class PoseDetectionUITests(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        self.driver.get("http://localhost:5500") 
    def test_title(self):
        driver = self.driver
        self.assertEqual(driver.title, "Pose Detection")

    def test_workout_selection(self):
        driver = self.driver
        # Find the workouts dropdown
        select_element = driver.find_element(By.ID, "workoutsSelect")
        select = Select(select_element)

        select.select_by_visible_text('Squats')
        self.assertEqual(select.first_selected_option.text, 'Squats')

        # Select 'Crunches'
        select.select_by_visible_text('Crunches')
        self.assertEqual(select.first_selected_option.text, 'Crunches')

    def test_camera_selection(self):
        driver = self.driver
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "cameraSelect")))

        select_element = driver.find_element(By.ID, "cameraSelect")
        select = Select(select_element)
        select.select_by_index(0)  

    def test_upload_video(self):
        driver = self.driver
        upload_element = driver.find_element(By.ID, "upload")
        video_path = os.path.join(os.getcwd(), "test_data/test_video.mp4")
        upload_element.send_keys(video_path)

    def test_start_camera_button(self):
        driver = self.driver
        start_button = driver.find_element(By.ID, "startCamera")
        start_button.click()


    def tearDown(self):
        # Close the browser window
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
