import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Set dark theme
plt.rcParams['figure.facecolor'] = '#0f1117'
plt.rcParams['axes.facecolor'] = '#0f1117'

fig, ax = plt.subplots(figsize=(14, 18))
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')

# Title
ax.text(7, 17.5, 'AI Real Estate Transformation Demo — How It Works',
        ha='center', va='top', fontsize=20, fontweight='bold', color='white')

# Colors
box_color = '#181b24'
accent = '#3b82f6'
accent2 = '#10b981'
warning = '#f59e0b'
text_color = 'white'
muted = '#9aa3b2'

# Helper to draw a box
def draw_box(ax, x, y, w, h, title, lines, color=box_color, border=accent, title_size=11, body_size=9.5):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.2",
                         facecolor=color, edgecolor=border, linewidth=2)
    ax.add_patch(box)
    ax.text(x + w/2, y + h - 0.35, title, ha='center', va='top',
            fontsize=title_size, fontweight='bold', color=text_color)
    for i, line in enumerate(lines):
        ax.text(x + 0.2, y + h - 0.8 - i*0.35, line, ha='left', va='top',
                fontsize=body_size, color=muted)

# Helper to draw arrow
def draw_arrow(ax, start, end, color=accent):
    arrow = FancyArrowPatch(start, end, arrowstyle='->', mutation_scale=20,
                            color=color, linewidth=2)
    ax.add_patch(arrow)

# 1. User starts at landing page
draw_box(ax, 4.5, 15.5, 5, 1.3, '1. Landing Page',
         ['User visits http://localhost:8000',
          'Fills out lead form: name, phone, agency, role, challenge'],
         border=accent)

# 2. Submit form
draw_box(ax, 4.5, 13.2, 5, 1.3, '2. Submit Lead',
         ['Browser sends POST /api/leads',
          'FastAPI receives form data'],
         border=accent)

draw_arrow(ax, (7, 15.5), (7, 14.5), accent)

# 3. CRM save
draw_box(ax, 4.5, 10.9, 5, 1.3, '3. SQLite CRM Saves Lead',
         ['database.py writes lead to leads.db',
          'Status = "new", qualified = 0'],
         border=accent2)

draw_arrow(ax, (7, 13.2), (7, 12.2), accent)

# 4. AI call trigger
draw_box(ax, 4.5, 8.6, 5, 1.3, '4. User clicks "Start AI Call"',
         ['Browser opens SSE stream: /api/leads/{id}/call-stream',
          'Or POST /api/leads/{id}/call runs sync call'],
         border=warning)

draw_arrow(ax, (7, 10.9), (7, 9.9), accent)

# 5. AI Voice Engine
draw_box(ax, 4.5, 6.1, 5, 1.5, '5. AI Voice Engine (ai_voice.py)',
         ['Simulated conversation right now',
          'In production: replace with Bland, Retell, Vapi, or Twilio',
          'Asks 4 qualification questions + scores responses'],
         border=accent2)

draw_arrow(ax, (7, 8.6), (7, 7.6), accent)

# 6. Score and update
draw_box(ax, 4.5, 3.6, 5, 1.5, '6. Score & Update CRM',
         ['Positive keywords → qualified = true',
          'Negative keywords → needs_review',
          'CRM updated: status, summary, transcript'],
         border=accent2)

draw_arrow(ax, (7, 6.1), (7, 5.1), accent)

# 7. Dashboard
draw_box(ax, 4.5, 1.1, 5, 1.5, '7. CRM Dashboard',
         ['Visit /dashboard',
          'See stats, lead table, transcripts',
          'Action: view lead detail, rerun call'],
         border=accent)

draw_arrow(ax, (7, 3.6), (7, 2.6), accent)

# Side notes
# Tech stack box
draw_box(ax, 10.5, 10.5, 3.2, 4.0, 'Tech Stack',
         ['FastAPI (backend)',
          'aiosqlite (SQLite)',
          'Jinja2 templates',
          'Vanilla JS/CSS',
          'SSE streaming',
          'Simulated voice engine'],
         border=muted, title_size=10, body_size=9)

# Production swap box
draw_box(ax, 0.3, 10.5, 3.2, 4.0, 'Production Swaps',
         ['Voice: Bland/Retell/Vapi',
          'CRM: GoHighLevel/FBOS',
          'Auth: OAuth/API keys',
          'Hosting: Vercel/Railway',
          'Billing: Stripe',
          'Notifications: Slack/email'],
         border=muted, title_size=10, body_size=9)

# Legend
legend_items = [
    ('Entry Flow', accent),
    ('CRM / Data', accent2),
    ('User Action', warning),
    ('Supporting Info', muted),
]
for i, (label, color) in enumerate(legend_items):
    ax.add_patch(mpatches.Rectangle((0.5 + i*2.5, 0.2), 0.4, 0.25, facecolor=color, edgecolor=color))
    ax.text(1.0 + i*2.5, 0.32, label, ha='left', va='center', fontsize=9, color='white')

plt.tight_layout()
plt.savefig('/Volumes/Agent H n OC/Agent-State-Active/openclaw/workspace-vibeagencyj/ai-real-estate-demo/how-it-works-flowchart.png',
            dpi=150, bbox_inches='tight', facecolor='#0f1117')
print('Saved flowchart: how-it-works-flowchart.png')