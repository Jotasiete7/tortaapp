import os

path = r"C:\Users\Pichau\.gemini\antigravity\brain\74e19e36-8c67-453a-a689-6e4ab79920f3\Torta app\TortaApp-V2\components\PlayerProfile.tsx"

with open(path, 'rb') as f:
    content = f.read()

# Target: The span that displays the server name directly
# <span className="font-bold ml-1">{stats.fav_server || 'Unknown'}</span>
target = b'<span className="font-bold ml-1">{stats.fav_server || \'Unknown\'}</span>'

# Replacement: The IIFE logic
replacement = b"""<span className="font-bold ml-1">
                                    {(() => {
                                        const s = (stats.fav_server || '').toLowerCase();
                                        if (s.includes('har')) return 'Harmony';
                                        if (s.includes('mel')) return 'Melody';
                                        if (s.includes('cad')) return 'Cadence';
                                        return stats.fav_server || 'Unknown';
                                    })()}
                                </span>"""

if target in content:
    content = content.replace(target, replacement)
    print("PlayerProfile fixed.")
    with open(path, 'wb') as f:
        f.write(content)
else:
    print("Target not found in PlayerProfile.tsx")
    # Debug: maybe it's already fixed?
    if b'return \'Harmony\'' in content:
        print("It seems already fixed.")
    else:
        print("Could not find target or fix.")

