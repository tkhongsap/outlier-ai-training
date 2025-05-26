import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

class ExamScraper:
    def __init__(self, headless=True, wait_time=10):
        """
        Initialize the exam scraper with Selenium WebDriver
        
        Args:
            headless (bool): Run browser in headless mode
            wait_time (int): Maximum wait time for elements to load
        """
        self.wait_time = wait_time
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Add user agent to avoid detection
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.wait_time)
        except Exception as e:
            print(f"Error setting up WebDriver: {e}")
            print("Please make sure ChromeDriver is installed and in PATH")
            raise
    
    def scrape_exam(self, exam_id):
        """
        Scrape exam data for a specific exam ID
        
        Args:
            exam_id (int): The exam ID to scrape
            
        Returns:
            dict: Exam data including metadata and questions
        """
        url = f"https://www.trueplookpanya.com/examination2/examPreview?id={exam_id}"
        
        try:
            print(f"กำลังดึงข้อมูลข้อสอบ ID: {exam_id}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if page loaded successfully
            if "404" in self.driver.title or "Not Found" in self.driver.title:
                print(f"ไม่พบข้อสอบ ID: {exam_id}")
                return None
            
            # Wait for content to load
            try:
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except TimeoutException:
                print(f"Timeout waiting for page to load for exam ID: {exam_id}")
                return None
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract exam metadata
            metadata = self.extract_metadata(soup, exam_id)
            
            # Extract questions
            questions = self.extract_questions(soup)
            
            exam_data = {
                "exam_id": exam_id,
                "url": url,
                "metadata": metadata,
                "questions": questions,
                "total_questions": len(questions)
            }
            
            print(f"ดึงข้อมูลสำเร็จ: {len(questions)} ข้อ")
            return exam_data
            
        except Exception as e:
            print(f"Error scraping exam {exam_id}: {e}")
            return None
    
    def extract_metadata(self, soup, exam_id):
        """Extract exam metadata from the page"""
        metadata = {
            "exam_id": exam_id,
            "title": "",
            "subject": "",
            "grade_level": "",
            "exam_type": "",
            "description": ""
        }
        
        # Try to extract title from various possible locations
        title_selectors = [
            "h1.exam-title",
            "h1",
            ".exam-header h1",
            ".page-title",
            "title"
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                metadata["title"] = title_elem.get_text().strip()
                break
        
        # Try to extract other metadata from tables or divs
        # Look for common patterns in Thai educational websites
        info_elements = soup.find_all(['table', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['info', 'detail', 'meta', 'exam']
        ))
        
        for element in info_elements:
            text = element.get_text()
            if 'วิชา' in text or 'subject' in text.lower():
                # Extract subject information
                pass
            if 'ชั้น' in text or 'grade' in text.lower():
                # Extract grade level
                pass
        
        return metadata
    
    def extract_questions(self, soup):
        """Extract questions and answers from the page"""
        questions = []
        
        # Try multiple selectors for questions
        question_selectors = [
            ".question-item",
            ".question-block",
            ".exam-question",
            "[class*='question']",
            ".item-question"
        ]
        
        question_elements = []
        for selector in question_selectors:
            elements = soup.select(selector)
            if elements:
                question_elements = elements
                break
        
        # If no specific question elements found, try to find patterns
        if not question_elements:
            # Look for numbered patterns (1., 2., etc.)
            all_text = soup.get_text()
            if any(f"{i}." in all_text for i in range(1, 6)):
                # Try to parse questions from text patterns
                question_elements = self.parse_questions_from_text(soup)
        
        for idx, element in enumerate(question_elements, 1):
            question_data = {
                "question_number": idx,
                "question_text": "",
                "choices": [],
                "question_type": "multiple_choice"
            }
            
            # Extract question text
            question_text = element.get_text().strip()
            if question_text:
                question_data["question_text"] = question_text
            
            # Try to extract choices
            choice_selectors = [
                ".choice",
                ".answer-choice",
                ".option",
                "[class*='choice']",
                "li"
            ]
            
            for choice_selector in choice_selectors:
                choices = element.select(choice_selector)
                if choices:
                    question_data["choices"] = [choice.get_text().strip() for choice in choices if choice.get_text().strip()]
                    break
            
            if question_data["question_text"]:
                questions.append(question_data)
        
        return questions
    
    def parse_questions_from_text(self, soup):
        """Parse questions from text patterns when no specific elements are found"""
        # This is a fallback method to extract questions from plain text
        # Implementation would depend on the specific text format
        return []
    
    def scrape_exam_range(self, start_id, end_id=None, output_dir="exam_data"):
        """
        Scrape multiple exams in a range
        
        Args:
            start_id (int): Starting exam ID
            end_id (int): Ending exam ID (if None, scrape only start_id)
            output_dir (str): Directory to save JSON files
        """
        if end_id is None:
            end_id = start_id
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        successful_scrapes = 0
        failed_scrapes = 0
        
        for exam_id in range(start_id, end_id + 1):
            try:
                exam_data = self.scrape_exam(exam_id)
                
                if exam_data:
                    # Save to JSON file
                    filename = f"exam_{exam_id}.json"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(exam_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"บันทึกไฟล์: {filepath}")
                    successful_scrapes += 1
                else:
                    failed_scrapes += 1
                
                # Add delay between requests to be respectful
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing exam {exam_id}: {e}")
                failed_scrapes += 1
                continue
        
        print(f"\nสรุปผลการดึงข้อมูล:")
        print(f"สำเร็จ: {successful_scrapes} ไฟล์")
        print(f"ล้มเหลว: {failed_scrapes} ไฟล์")
    
    def close(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    """Main function to run the scraper"""
    # Configuration
    START_ID = 13500
    END_ID = 13500  # Change this to scrape multiple exams
    
    scraper = ExamScraper(headless=True)
    
    try:
        # Scrape single exam or range
        scraper.scrape_exam_range(START_ID, END_ID)
        
    except KeyboardInterrupt:
        print("\nการดึงข้อมูลถูกยกเลิกโดยผู้ใช้")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 