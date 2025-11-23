import os
import random
import shutil
import re
from datetime import datetime

STAGING_DIR = 'staging'
PUBLIC_BLOG_DIR = 'public/blogs'
BLOG_INDEX_FILE = 'public/blogs/main.html'

def get_article_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'<title>(.*?)</title>', content)
    title = title_match.group(1).split(' - ')[0] if title_match else 'Untitled'
    
    desc_match = re.search(r'<meta name="description" content="(.*?)">', content)
    excerpt = desc_match.group(1) if desc_match else ''
    
    # Simple extraction, assuming standard format
    # In a real scenario, might need more robust parsing
    image_match = re.search(r'<img src="(.*?)"', content)
    image = image_match.group(1) if image_match else 'resources/default.jpg'
    
    # Adjust image path if it's relative
    if not image.startswith('http'):
        image = '../' + image
        
    return {
        'title': title,
        'excerpt': excerpt,
        'image': image,
        'date': datetime.now().strftime('%b %d, %Y'),
        'author': 'Tarun Mehra', # Default author
        'readTime': '5 min', # Default read time
        'category': 'Networking' # Default category
    }

def update_blog_index(new_articles):
    with open(BLOG_INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the blogPosts array
    match = re.search(r'const blogPosts = \[\s*([\s\S]*?)\s*\];', content)
    if not match:
        print("Could not find blogPosts array in main.html")
        return

    current_posts_str = match.group(1)
    
    # Generate new post objects
    new_posts_js = []
    start_id = 100 # Start IDs from 100 to avoid collision
    
    for i, article in enumerate(new_articles):
        meta = article['meta']
        filename = article['filename']
        
        post_js = f"""    {{
        id: {start_id + i},
        title: "{meta['title']}",
        excerpt: "{meta['excerpt']}",
        author: "{meta['author']}",
        date: "{meta['date']}",
        readTime: "{meta['readTime']}",
        category: "{meta['category']}",
        image: "{meta['image']}",
        url: "{filename}"
    }}"""
        new_posts_js.append(post_js)
        
    new_posts_str = ",\n".join(new_posts_js)
    
    if current_posts_str.strip():
        updated_posts_str = new_posts_str + ",\n" + current_posts_str
    else:
        updated_posts_str = new_posts_str
        
    new_content = content.replace(match.group(0), f"const blogPosts = [\n{updated_posts_str}\n];")
    
    # Also update the render function to use URL if present
    if 'onclick="openBlog(${post.id})"' in new_content:
        new_content = new_content.replace(
            'onclick="openBlog(${post.id})"', 
            'onclick="if(post.url) window.location.href=post.url; else openBlog(${post.id})"'
        )
        
    with open(BLOG_INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    if not os.path.exists(STAGING_DIR):
        print(f"Staging directory {STAGING_DIR} does not exist.")
        return

    if not os.path.exists(PUBLIC_BLOG_DIR):
        os.makedirs(PUBLIC_BLOG_DIR)

    articles = [f for f in os.listdir(STAGING_DIR) if f.endswith('.html') and f.startswith('article')]
    
    if not articles:
        print("No articles found in staging.")
        return
        
    # Select up to 3 random articles
    selected_articles = random.sample(articles, min(3, len(articles)))
    
    processed_articles = []
    
    for filename in selected_articles:
        src_path = os.path.join(STAGING_DIR, filename)
        dst_path = os.path.join(PUBLIC_BLOG_DIR, filename)
        
        # Get metadata before moving
        meta = get_article_metadata(src_path)
        
        # Move file
        shutil.move(src_path, dst_path)
        print(f"Moved {filename} to {PUBLIC_BLOG_DIR}")
        
        processed_articles.append({
            'filename': filename,
            'meta': meta
        })
        
    update_blog_index(processed_articles)
    print("Updated blog index.")

if __name__ == "__main__":
    main()
