import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\Dashboard.tsx"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Restore padding
content = content.replace('p-4', 'p-6')

# 2. Remove grid wrapper
target_block = """            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-8">
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

replacement_block = """            {/* Market Intelligence - Full Width */}
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

# Normalize line endings
content = content.replace('\r\n', '\n')
target_block = target_block.replace('\r\n', '\n')
replacement_block = replacement_block.replace('\r\n', '\n')

if target_block in content:
    content = content.replace(target_block, replacement_block)
    print("Dashboard layout restored.")
else:
    print("Target block NOT found. Layout might already be restored or different.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
