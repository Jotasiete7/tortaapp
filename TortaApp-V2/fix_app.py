# -*- coding: utf-8 -*-
import os

app_path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\App.tsx"

try:
    # Read with utf-8, replacing errors to avoid crash
    with open(app_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # We need to find the block. Since bullets might be garbled, let's match by surrounding tags
    # Start: <div className="flex items-center gap-2 mt-1">
    # End: </div> (closing the div)
    
    start_marker = '<div className="flex items-center gap-2 mt-1">'
    
    if start_marker in content:
        start_idx = content.find(start_marker)
        # Find the end of this div. It contains a span and a button.
        # Let's assume the structure is consistent and look for the closing </div> after the button
        # The block ends with </div>.
        # We can try to replace the whole known structure if we can construct it, 
        # but since we don't know how the bullets were read (maybe replacement char), exact match is hard.
        
        # Let's try to construct the target with the replacement char if needed, or just regex replace
        # But regex in python needs import re
        import re
        
        # Regex to match the block
        # <div className="flex items-center gap-2 mt-1"> ... </div>
        # We need to be careful not to match too much.
        
        pattern = r'<div className="flex items-center gap-2 mt-1">\s*<span className="text-xs text-slate-500">\s*\{showEmail \? user\.email : [^}]+\}\s*</span>\s*<button[\s\S]*?</button>\s*</div>'
        
        replacement = """<div className="flex items-center gap-2 mt-1 bg-slate-800/50 px-2 py-1 rounded border border-slate-700/50">
                                        <span className="text-xs text-slate-400 font-mono tracking-wide">
                                            {showEmail ? user.email : '\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022\\u2022'}
                                        </span>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setShowEmail(!showEmail);
                                            }}
                                            className="text-slate-500 hover:text-white transition-colors p-0.5 rounded hover:bg-slate-700"
                                            title={showEmail ? "Hide Email" : "Show Email"}
                                        >
                                            {showEmail ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
                                        </button>
                                    </div>"""
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(app_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("App.tsx fixed with regex.")
        else:
            print("App.tsx regex match failed.")
            # Debug: print what we found around the marker
            print("Context:", content[start_idx:start_idx+200])
            
    else:
        print("App.tsx start marker not found.")

except Exception as e:
    print(f"Error fixing App.tsx: {e}")
