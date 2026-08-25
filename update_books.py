import os
import json
import hashlib

def generate_book_json():
    base_dir = 'public/books'
    book_tree = {}
    # 支持的所有书籍格式
    book_exts = ('.pdf', '.epub', '.mobi', '.txt', '.md', '.azw3')

    for root, dirs, files in os.walk(base_dir):
        category = os.path.relpath(root, base_dir)
        if category == '.':
            continue

        assets_in_cat = []
        book_files = [f for f in files if f.lower().endswith(book_exts)]

        for b_file in sorted(book_files):
            name_without_ext = os.path.splitext(b_file)[0]
            file_ext = os.path.splitext(b_file)[1].lower().lstrip('.')

            # 尝试读取同名 .txt 文件作为概要
            summary = ""
            s_path = os.path.join(root, name_without_ext + '.txt')
            if os.path.exists(s_path):
                try:
                    with open(s_path, 'r', encoding='utf-8') as f:
                        summary = f.read().strip()
                except Exception:
                    summary = ""

            # 尝试读取同名 .meta.json 文件获取作者/年份等元数据
            author = ""
            year = None
            meta_path = os.path.join(root, name_without_ext + '.meta.json')
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                        author = meta.get('author', '')
                        year = meta.get('year', None)
                except Exception:
                    pass

            # 生成稳定 ID
            id_hash = hashlib.md5(f"{category}/{b_file}".encode()).hexdigest()[:8]
            book_id = f"book-{id_hash}"

            assets_in_cat.append({
                "id": book_id,
                "title": name_without_ext,
                "author": author,
                "year": year,
                "fileName": b_file,
                "summary": summary,
            })

        if assets_in_cat:
            book_tree[category] = assets_in_cat

    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(book_tree, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in book_tree.values())
    print(f"✅ 索引更新成功！共 {len(book_tree)} 个分类，{total} 本书籍。")

if __name__ == "__main__":
    generate_book_json()
