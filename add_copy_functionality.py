"""
Patch to add Copy functionality to SuperPy Treeviews
"""
import os

def apply_copy_patch():
    file_path = 'superpy_app.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Add copy_selected_rows and create_tree_context_menu methods
    # We'll add them before the _build_ui method or similar utility methods
    if 'def copy_selected_rows(self' not in content:
        new_methods = """
    def copy_selected_rows(self, tree):
        \"\"\"Copy selected rows to clipboard (tab-separated)\"\"\"
        selection = tree.selection()
        if not selection:
            return
            
        lines = []
        # Get headers
        headers = [tree.heading(c)['text'] for c in tree['columns']]
        lines.append('\\t'.join(headers))
        
        # Get data
        for item in selection:
            values = tree.item(item)['values']
            lines.append('\\t'.join(map(str, values)))
            
        text_to_copy = '\\n'.join(lines)
        self.clipboard_clear()
        self.clipboard_append(text_to_copy)
        self.update() # Required for clipboard to work
        self.log_message(f"Copied {len(selection)} rows to clipboard")

    def create_tree_context_menu(self, tree):
        \"\"\"Create context menu for treeview\"\"\"
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Copiar", command=lambda: self.copy_selected_rows(tree))
        
        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()
        
        tree.bind("<Button-3>", show_menu)
        tree.bind("<Control-c>", lambda e: self.copy_selected_rows(tree))
"""
        # Insert before _build_ui
        content = content.replace(
            '    def _build_ui(self):',
            new_methods + '    def _build_ui(self):'
        )
        print("✓ Added copy methods")

    # 2. Apply to Search Tree
    if 'self.create_tree_context_menu(self.search_tree)' not in content:
        # Find where search tree is packed
        search_pack = "self.search_tree.pack(side='left', fill='both', expand=True)"
        if search_pack in content:
            content = content.replace(
                search_pack,
                search_pack + "\n        self.create_tree_context_menu(self.search_tree)"
            )
            print("✓ Applied to Search Tree")
            
    # 3. Apply to Advanced Search Tree
    if 'self.create_tree_context_menu(self.adv_tree)' not in content:
        adv_pack = "self.adv_tree.pack(side='left', fill='both', expand=True)"
        if adv_pack in content:
            content = content.replace(
                adv_pack,
                adv_pack + "\n        self.create_tree_context_menu(self.adv_tree)"
            )
            print("✓ Applied to Advanced Search Tree")

    # 4. Apply to Price Editor Tree (if exists)
    if 'self.create_tree_context_menu(self.price_tree)' not in content:
        price_pack = "self.price_tree.pack(side='left', fill='both', expand=True)"
        if price_pack in content:
            content = content.replace(
                price_pack,
                price_pack + "\n        self.create_tree_context_menu(self.price_tree)"
            )
            print("✓ Applied to Price Editor Tree")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\n✅ Copy functionality added successfully!")
    print("Restart the app to use Right-Click > Copy or Ctrl+C")

if __name__ == '__main__':
    apply_copy_patch()
