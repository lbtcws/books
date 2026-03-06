import os
import json

def generate_book_json():
    base_dir = 'books'
    book_tree = {}
    # 支持的正文格式
    book_exts = ('.pdf', '.epub', '.md')

    for root, dirs, files in os.walk(base_dir):
        category = os.path.relpath(root, base_dir)
        if category == '.': continue
        
        assets_in_cat = []
        # 只筛选出属于“书/正文”的文件
        book_files = [f for f in files if f.lower().endswith(book_exts)]
        
        for b_file in book_files:
            name_without_ext = os.path.splitext(b_file)[0]
            
            # 【核心修改】概要管理逻辑：
            # 严格只读取同名的 .txt 文件作为概要
            summary = "（作者很懒，暂无概要记录...）"
            s_path = os.path.join(root, name_without_ext + '.txt')
            
            if os.path.exists(s_path):
                try:
                    with open(s_path, 'r', encoding='utf-8') as f:
                        summary = f.read().strip()
                except Exception as e:
                    summary = f"读取概要出错: {str(e)}"
            
            assets_in_cat.append({
                "title": name_without_ext,
                "fileName": b_file,
                "summary": summary
            })

        if assets_in_cat:
            book_tree[category] = assets_in_cat

    with open('books_data.json', 'w', encoding='utf-8') as f:
        json.dump(book_tree, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 索引更新成功！严格执行 [TXT管理概要] 模式。")

if __name__ == "__main__":
    generate_book_json()