import requests
import json
import os
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class APIExamScraper:
    def __init__(self):
        """
        Initialize the API-based exam scraper
        """
        self.session = requests.Session()
        self.base_url = "https://www.trueplookpanya.com"
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with appropriate headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'th-TH,th;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def discover_api_endpoints(self, exam_id):
        """
        Try to discover API endpoints by analyzing the page
        
        Args:
            exam_id (int): Exam ID to analyze
            
        Returns:
            list: List of potential API endpoints
        """
        url = f"{self.base_url}/examination2/examPreview?id={exam_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for JavaScript files that might contain API calls
            script_tags = soup.find_all('script', src=True)
            api_endpoints = []
            
            for script in script_tags:
                script_url = urljoin(self.base_url, script['src'])
                try:
                    script_response = self.session.get(script_url)
                    script_content = script_response.text
                    
                    # Look for API patterns in JavaScript
                    api_patterns = [
                        r'["\'](/api/[^"\']+)["\']',
                        r'["\'](/examination[^"\']+)["\']',
                        r'ajax\s*\(\s*["\']([^"\']+)["\']',
                        r'fetch\s*\(\s*["\']([^"\']+)["\']',
                        r'\.get\s*\(\s*["\']([^"\']+)["\']',
                        r'\.post\s*\(\s*["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in api_patterns:
                        matches = re.findall(pattern, script_content)
                        for match in matches:
                            if 'exam' in match.lower() or 'question' in match.lower():
                                full_url = urljoin(self.base_url, match)
                                if full_url not in api_endpoints:
                                    api_endpoints.append(full_url)
                
                except Exception as e:
                    continue
            
            # Also look for inline JavaScript
            inline_scripts = soup.find_all('script', src=False)
            for script in inline_scripts:
                if script.string:
                    for pattern in api_patterns:
                        matches = re.findall(pattern, script.string)
                        for match in matches:
                            if 'exam' in match.lower() or 'question' in match.lower():
                                full_url = urljoin(self.base_url, match)
                                if full_url not in api_endpoints:
                                    api_endpoints.append(full_url)
            
            return api_endpoints
            
        except Exception as e:
            print(f"Error discovering API endpoints: {e}")
            return []
    
    def try_api_endpoints(self, exam_id, endpoints):
        """
        Try different API endpoints to get exam data
        
        Args:
            exam_id (int): Exam ID
            endpoints (list): List of API endpoints to try
            
        Returns:
            dict: Exam data if successful, None otherwise
        """
        for endpoint in endpoints:
            try:
                # Try different parameter formats
                param_variations = [
                    {'id': exam_id},
                    {'examId': exam_id},
                    {'exam_id': exam_id},
                    {'examID': exam_id}
                ]
                
                for params in param_variations:
                    response = self.session.get(endpoint, params=params)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if data and ('questions' in data or 'exam' in data or 'data' in data):
                                print(f"Found API endpoint: {endpoint}")
                                return self.process_api_data(data, exam_id)
                        except json.JSONDecodeError:
                            # Try to parse as HTML if not JSON
                            soup = BeautifulSoup(response.content, 'html.parser')
                            if soup.find_all(['div', 'span', 'p']):
                                return self.extract_from_html(soup, exam_id)
                
            except Exception as e:
                continue
        
        return None
    
    def process_api_data(self, data, exam_id):
        """
        Process API response data into standardized format
        
        Args:
            data (dict): Raw API response data
            exam_id (int): Exam ID
            
        Returns:
            dict: Processed exam data
        """
        exam_data = {
            "exam_id": exam_id,
            "metadata": {},
            "questions": [],
            "source": "api"
        }
        
        # Try to extract metadata
        if 'title' in data:
            exam_data['metadata']['title'] = data['title']
        if 'subject' in data:
            exam_data['metadata']['subject'] = data['subject']
        if 'description' in data:
            exam_data['metadata']['description'] = data['description']
        
        # Try to extract questions
        questions_key = None
        for key in ['questions', 'items', 'data', 'exam_questions']:
            if key in data and isinstance(data[key], list):
                questions_key = key
                break
        
        if questions_key:
            for idx, question in enumerate(data[questions_key], 1):
                question_data = {
                    "question_number": idx,
                    "question_text": "",
                    "choices": [],
                    "question_type": "multiple_choice"
                }
                
                # Extract question text
                for text_key in ['question', 'text', 'question_text', 'title']:
                    if text_key in question:
                        question_data['question_text'] = question[text_key]
                        break
                
                # Extract choices
                for choice_key in ['choices', 'options', 'answers', 'alternatives']:
                    if choice_key in question and isinstance(question[choice_key], list):
                        question_data['choices'] = question[choice_key]
                        break
                
                if question_data['question_text']:
                    exam_data['questions'].append(question_data)
        
        return exam_data
    
    def extract_from_html(self, soup, exam_id):
        """
        Extract exam data from HTML when API is not available
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            exam_id (int): Exam ID
            
        Returns:
            dict: Extracted exam data
        """
        exam_data = {
            "exam_id": exam_id,
            "metadata": {
                "title": soup.title.text if soup.title else "",
                "source": "html_extraction"
            },
            "questions": [],
            "source": "html"
        }
        
        # Try to find questions in HTML
        # This would need to be customized based on the actual HTML structure
        question_patterns = [
            soup.find_all('div', class_=lambda x: x and 'question' in x.lower()),
            soup.find_all('div', class_=lambda x: x and 'item' in x.lower()),
            soup.find_all('li'),
            soup.find_all('p')
        ]
        
        for pattern in question_patterns:
            if pattern and len(pattern) > 1:  # Found potential questions
                for idx, element in enumerate(pattern, 1):
                    text = element.get_text().strip()
                    if len(text) > 20 and any(char in text for char in ['?', '？', 'ข้อใด', 'คือ']):
                        question_data = {
                            "question_number": idx,
                            "question_text": text,
                            "choices": [],
                            "question_type": "multiple_choice"
                        }
                        exam_data['questions'].append(question_data)
                
                if exam_data['questions']:
                    break
        
        return exam_data
    
    def scrape_exam(self, exam_id):
        """
        Main method to scrape exam data
        
        Args:
            exam_id (int): Exam ID to scrape
            
        Returns:
            dict: Exam data or None if failed
        """
        print(f"กำลังวิเคราะห์ข้อสอบ ID: {exam_id}")
        
        # First, try to discover API endpoints
        endpoints = self.discover_api_endpoints(exam_id)
        
        if endpoints:
            print(f"พบ API endpoints: {len(endpoints)} รายการ")
            exam_data = self.try_api_endpoints(exam_id, endpoints)
            if exam_data:
                return exam_data
        
        # Fallback: try direct page scraping
        print("กำลังลองดึงข้อมูลจากหน้าเว็บโดยตรง...")
        url = f"{self.base_url}/examination2/examPreview?id={exam_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self.extract_from_html(soup, exam_id)
            
        except Exception as e:
            print(f"Error scraping exam {exam_id}: {e}")
            return None
    
    def scrape_exam_range(self, start_id, end_id=None, output_dir="exam_data_api"):
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
                
                if exam_data and exam_data.get('questions'):
                    # Save to JSON file
                    filename = f"exam_{exam_id}.json"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(exam_data, f, ensure_ascii=False, indent=2)
                    
                    print(f"บันทึกไฟล์: {filepath} ({len(exam_data['questions'])} ข้อ)")
                    successful_scrapes += 1
                else:
                    print(f"ไม่พบข้อมูลข้อสอบ ID: {exam_id}")
                    failed_scrapes += 1
                
                # Add delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing exam {exam_id}: {e}")
                failed_scrapes += 1
                continue
        
        print(f"\nสรุปผลการดึงข้อมูล:")
        print(f"สำเร็จ: {successful_scrapes} ไฟล์")
        print(f"ล้มเหลว: {failed_scrapes} ไฟล์")

def main():
    """Main function to run the API scraper"""
    # Configuration
    START_ID = 13500
    END_ID = 13500  # Change this to scrape multiple exams
    
    scraper = APIExamScraper()
    
    try:
        # Scrape single exam or range
        scraper.scrape_exam_range(START_ID, END_ID)
        
    except KeyboardInterrupt:
        print("\nการดึงข้อมูลถูกยกเลิกโดยผู้ใช้")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main() 