import os

# Jamlanmasi kerak bo'lmagan papka va fayllar
EXCLUDE_DIRS = {'.git', '.venv', '__pycache__', '.idea', '.vscode', 'data', 'models'}
EXCLUDE_FILES = {'export_project.py', 'project_summary.md', '.DS_Store', 'poetry.lock'}
# Faqat quyidagi turdagi fayllarni o'qiymiz
INCLUDE_EXTENSIONS = {'.py', '.env.example', '.txt', '.md', '.yaml', '.json'}

def generate_project_summary(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# LOYIHA STRUKTURASI VA KODI\n\n")
        
        # 1. Strukturani yozish
        f.write("## 1. Papka Strukturasi\n```text\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                if file not in EXCLUDE_FILES:
                    f.write(f"{sub_indent}{file}\n")
        f.write("```\n\n")

        # 2. Fayllar mazmunini yozish
        f.write("## 2. Fayllar Mazmuni\n\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                
                ext = os.path.splitext(file)[1]
                if ext in INCLUDE_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, root_dir)
                    
                    f.write(f"### Fayl: `{relative_path}`\n")
                    f.write(f"```{ext.replace('.', '')}\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as code_file:
                            f.write(code_file.read())
                    except Exception as e:
                        f.write(f"Xatolik: Faylni o'qib bo'lmadi ({e})")
                    f.write("\n```\n\n")

    print(f"Tayyor! Loyiha mazmuni '{output_file}' fayliga yozildi.")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    generate_project_summary(current_directory, "project_summary.md")