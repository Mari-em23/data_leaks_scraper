# Run from /Code : python -m Forums.patched.search_and_scrape_from_patched

from datetime import datetime
from playwright.sync_api import sync_playwright
import os
import sys
import json

from sqlite_connection.sqlite_connection import add_forums_leaks


"""
What this script does:
1. Navigates to the search page of the forum.
2. Fills in the search keyword and submits the search form.
3. Waits for the search results to load and extracts relevant information from each result, including
    - Thread title
    - Author
    - Forum name
    - Number of replies
    - Number of views
    - Link to the thread
4. For each thread, it also navigates to the thread page to extract the post date and saves a screenshot of the thread.
5. Saves all extracted information into a JSON file and also creates a Python list representation for easy access in other scripts.
6. Logs the process and handles exceptions gracefully, including saving error screenshots if something goes wrong.

PS : should be logged in to the website before running the script and close all browser tabs before running
"""
def main():
    url_search = "https://patched.to/search.php"
    headless = True # Headless mode refers to running the browser without a visible graphical user interface (GUI)
    keyword = "tunisia"
    opera_exe = r"C:\Users\benta\AppData\Local\Programs\Opera GX\opera.exe"
    opera_profile = r"C:\Users\benta\AppData\Roaming\Opera Software\Opera GX Stable" # Path to Opera GX user profile to stay logged in the website

    with sync_playwright() as p:
        
        context = p.chromium.launch_persistent_context( # Launches a persistent browser context using the specified user data directory and executable path, allowing the browser to maintain state across sessions (e.g., staying logged in)
            user_data_dir=opera_profile, 
            executable_path=opera_exe,
            headless=headless
        )
        page = context.new_page()
        
        try:
            website = "Patched.to"

            # Navigate to search page
            page.goto(url_search, wait_until='domcontentloaded') # Waits until The browser has downloaded and parsed the HTML and built the DOM tree

            # Fill in search form
            page.wait_for_selector('input[name="keywords"]', timeout=5000)
            page.fill('input[name="keywords"]', keyword)
            
            # Submit search
            page.wait_for_selector('input[value="Search"]', timeout=5000).click()
            page.wait_for_load_state('domcontentloaded')

            # Extract all search results from the table
            posts = []
            index = 0
            while True:

                rows = page.query_selector_all('table.tborder tr.inline_row') # Selects all table rows with class "inline_row" within a table with class "tborder", which represent individual search results
                for row in rows:
                    index += 1

                    # Extract thread title
                    title_elem = row.query_selector('a.subject_old, a.subject_new') # Selects the thread title link, which can have class "subject_old" (if read) or "subject_new" (if unread)
                    title = title_elem.text_content() if title_elem else 'N/A'

                    # Extract author
                    author_elem = row.query_selector('div.author a')
                    author = author_elem.text_content() if author_elem else 'N/A'

                    # Extract forum
                    forum_elem = row.query_selector('td a[href*="Forum-"]')
                    forum = forum_elem.text_content() if forum_elem else 'N/A'

                    # Extract replies count
                    replies_cells = row.query_selector_all('td')
                    replies = 'N/A'
                    views = 'N/A'
                    if len(replies_cells) >= 5: 
                        replies_text = replies_cells[4].text_content().strip()
                        replies = replies_text if replies_text else 'N/A'

                    if len(replies_cells) >= 6: 
                        views_text = replies_cells[5].text_content().strip()
                        views = views_text if views_text else 'N/A'

                
                    # Extract thread link
                    link_elem = row.query_selector('a.subject_old, a.subject_new')
                    link = link_elem.get_attribute('href') if link_elem else 'N/A'
                    if link and not link.startswith('http'):
                        link = 'https://patched.to/' + link

                    # Go to thread page
                    thread_page = context.new_page()
                    thread_page.goto(link, wait_until='domcontentloaded') 
                    
                    # Show post if user is banned
                    page_content = thread_page.content()
                    if f'This post is by a banned user ({author})' in page_content:       
                        show_button = thread_page.query_selector('a.unhide-banned-post')
                        if show_button:
                            show_button.click()
                            thread_page.wait_for_load_state('domcontentloaded')

                    # Extract post date 
                    post_date_element = thread_page.query_selector('span.post_date')

                    # Convert to datetime object
                    post_date_text = post_date_element.text_content().strip()
                    date_str = post_date_text.split("(")[0].replace(f"OP\xa0 Posted at ", "").strip()
                
                    # Convert to datetime object
                    post_date = str(datetime.strptime(date_str, "%d-%m-%Y, %I:%M %p"))

                    # Save screenshot of the thread page
                    thread_path = os.path.join("Forums/threads_screenshots", f"thread_number_{index}.png")
                    
                    # Sreenshot only the post element. 
                    captured_el = None
                    
                    captured_el= thread_page.query_selector('#posts_container #posts .post[class*="classic"]')
                    if captured_el:
                        captured_el.screenshot(path=thread_path)
                    
                    # Close the thread page
                    thread_page.close()
                    
                    

                    post_info = {
                        'title': title.strip(),
                        'forums_website': website.strip(),
                        'author': author.strip(),
                        'forum': forum.strip(),
                        'replies': replies.strip(),
                        'views': views.strip(),
                        'link': link,
                        'post_date': post_date,
                        'screenshot': thread_path
                    }
                
                    posts.append(post_info)        

                if page.locator("a.pagination_next").first.is_visible():
                    page.locator("a.pagination_next").first.click()
                    page.wait_for_load_state('domcontentloaded')
                else:
                    break

            # Save to JSON file
            output_file = os.path.join('Forums/darkforums/search_results.json')
            # Load existing data if file exists
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_posts = json.load(f)
                    except json.JSONDecodeError:
                        existing_posts = []
            else:
                existing_posts = []
            # Append new posts
            existing_posts.extend(posts)
            # Write back
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_posts, f, indent=2, ensure_ascii=False)


            # Also save to Python list representation
            list_file = os.path.join('Forums/darkforums/search_results.py')
            if os.path.exists(list_file):
                # Import existing list safely
                import importlib.util
                spec = importlib.util.spec_from_file_location("search_results", list_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                existing_posts = getattr(module, "posts", [])
            else:
                existing_posts = []
            existing_posts.extend(posts)
            with open(list_file, 'w', encoding='utf-8') as f:
                f.write('posts = ')
                f.write(repr(existing_posts))

                # Print summary
                print(f'\n{"="*80}')
                print(f'Search Results for: {keyword}')
                print(f'Total posts found: {len(posts)}')
                print(f'{"="*80}\n')

                for i, post in enumerate(posts, 1):
                    print(f'{i}. {post["title"]}')
                    print(f'   Author: {post["author"]}')
                    print(f'   Forum: {post["forum"]}')
                    print(f'   Replies: {post["replies"]} | Views: {post["views"]}')
                    print(f'   Posted at: {post["post_date"]}')
                    print(f'   Link: {post["link"]}')
                    print(f'   Screenshot: {post["screenshot"]}')
                    print()

                add_forums_leaks(posts)
                return posts

        except Exception as e:
            print("Search and scrape failed:", e)
            try:
                err_path = os.path.join('search_error.png')
                page.screenshot(path=err_path, full_page=True)
            except Exception:
                pass
            raise
        finally:
            try:
                context.close()
            except Exception:
                pass


if __name__ == '__main__':
    main()