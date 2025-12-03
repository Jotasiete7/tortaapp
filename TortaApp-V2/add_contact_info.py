import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\App.tsx"

with open(path, 'rb') as f:
    content = f.read()

# Target: The Portuguese button and its closing tags
# We want to insert AFTER the language switcher block.
# The language switcher block ends with:
#       </button>
#   </div>
# </div>

# Let's find the Portuguese button first
pt_btn_part = b"setLanguage('pt')"

if pt_btn_part in content:
    # Find the position
    idx = content.find(pt_btn_part)
    # Find the next closing div of the grid
    grid_close = content.find(b'</div>', idx)
    # Find the next closing div of the section
    section_close = content.find(b'</div>', grid_close + 6)
    
    # We want to insert before the section_close, or actually append a new section after the language section.
    # The structure is:
    # <div className="space-y-6">
    #    <div className="space-y-2">...language...</div>
    #    <-- INSERT HERE -->
    # </div>
    
    # So we need to find where the language section ends.
    # It seems the language section is the `div className="space-y-2"`
    
    # Let's try to match the exact closing sequence if possible, or just use the fact that we are inside "space-y-6"
    
    # New content to insert
    new_block = b"""
                                  {/* Contact Info */}
                                  <div className="space-y-2 pt-4 border-t border-slate-700/50">
                                      <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                                          <User className="w-4 h-4 text-emerald-500" />
                                          Developer Contact
                                      </label>
                                      <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 space-y-3">
                                          <div className="flex items-center justify-between text-sm">
                                              <span className="text-slate-400">Email:</span>
                                              <span className="text-white font-mono select-all">tortadev@gmail.com</span>
                                          </div>
                                          <div className="flex items-center justify-between text-sm">
                                              <span className="text-slate-400">In-game Nick:</span>
                                              <span className="text-amber-400 font-bold">Jotasiete</span>
                                          </div>
                                          <p className="text-xs text-slate-500 mt-2 italic">
                                              Report bugs or send feedback directly.
                                          </p>
                                      </div>
                                  </div>"""
                                  
    # We will insert it after the language section closing div.
    # The language section starts with <div className="space-y-2">
    # It contains the label and the grid.
    
    # Let's find the end of the language section more reliably.
    # We found `section_close` above. Let's assume that's the one.
    
    # Insert after section_close + 6 (length of </div>)
    insert_pos = section_close + 6
    
    new_content = content[:insert_pos] + new_block + content[insert_pos:]
    
    with open(path, 'wb') as f:
        f.write(new_content)
    print("Contact info added.")

else:
    print("Could not find Portuguese button to locate insertion point.")

