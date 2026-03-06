import os
import json

def generate_book_json():
    base_dir = 'books'
    book_tree = {}

    # 扫描 books 文件夹
    for root, dirs, files in os.walk(base_dir):
        # 计算当前是哪一级目录
        category = os.path.relpath(root, base_dir)
        if category == '.':
            continue
        
        # 过滤隐藏文件
        valid_files = [f for f in files if not f.startswith('.')]
        if valid_files:
            book_tree[category] = valid_files

    # 保存为 JSON
    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(book_tree, f, ensure_ascii=False, indent=4)
    
    print("✅ 索引更新成功！books_data.json 已生成。")

if __name__ == "__main__":
    generate_book_json()