import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\Sidebar.tsx"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '<span className="font-medium">Admin Panel</span>\n                        </button>'
replacement = """<span className="font-medium">Admin Panel</span>
                        </button>
                        <button
                            onClick={() => onNavigate(ViewState.PRICEMANAGER)}
                            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 group ${currentView === ViewState.PRICEMANAGER
                                ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20 shadow-sm'
                                : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                                }`}
                        >
                            <BadgeDollarSign className={`w-5 h-5 ${currentView === ViewState.PRICEMANAGER ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                            <span className="font-medium">Price Manager</span>
                        </button>"""

# Normalize line endings for matching
content = content.replace('\r\n', '\n')
target = target.replace('\r\n', '\n')
replacement = replacement.replace('\r\n', '\n')

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Sidebar updated successfully.")
else:
    print("Target not found in Sidebar.tsx")
