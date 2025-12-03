import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\Dashboard.tsx"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reduce padding
content = content.replace('p-6', 'p-4')

# 2. Wrap bottom sections in grid
block_target = """            {/* Market Intelligence - Full Width */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-emerald-500" />
                    Market Intelligence
                </h2>
                <Leaderboard />
            </div>

            {/* Advanced Data Tools - Full Width */}
            <div className="mt-8">
                <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                    <Database className="w-5 h-5 text-amber-500" />
                    Advanced Data Tools
                </h2>
                <LogUploader
                    onProcessingComplete={(records) => {
                        console.log("Processed RAW logs:", records);
                    }}
                />
            </div>"""

block_replacement = """            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-8">
                {/* Market Intelligence */}
                <div>
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-emerald-500" />
                        Market Intelligence
                    </h2>
                    <Leaderboard />
                </div>

                {/* Advanced Data Tools */}
                <div>
                    <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Database className="w-5 h-5 text-amber-500" />
                        Advanced Data Tools
                    </h2>
                    <LogUploader
                        onProcessingComplete={(records) => {
                            console.log("Processed RAW logs:", records);
                        }}
                    />
                </div>
            </div>"""

# Normalize line endings
content = content.replace('\r\n', '\n')
block_target = block_target.replace('\r\n', '\n')
block_replacement = block_replacement.replace('\r\n', '\n')

if block_target in content:
    content = content.replace(block_target, block_replacement)
    print("Dashboard blocks updated.")
else:
    print("Dashboard blocks NOT found.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
