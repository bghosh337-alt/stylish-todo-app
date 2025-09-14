import streamlit as st
from datetime import date
import uuid

st.set_page_config(page_title="To‑Do", page_icon="📝", layout="centered")

# --- CSS: nicer header, task cards, buttons ---
st.markdown(
    """
    <style>
    .app-header{
        background: linear-gradient(90deg,#4b6cb7,#182848);
        padding:16px; border-radius:12px; color: white; margin-bottom:18px;
        box-shadow: 0 6px 18px rgba(24,40,72,0.25);
    }
    .task-card{background:linear-gradient(180deg, rgba(255,255,255,0.98), rgba(250,250,250,0.98));
        padding:12px; border-radius:10px; margin-bottom:10px; border:1px solid #eee;
    }
    .task-title{font-weight:600; font-size:16px}
    .muted{color:#6b7280; font-size:13px}
    .badge{display:inline-block; padding:4px 8px; border-radius:999px; font-size:12px; margin-left:6px}
    .high{background:#fee2e2; color:#991b1b}
    .med{background:#fffbeb; color:#92400e}
    .low{background:#ecfdf5; color:#065f46}
    .done{text-decoration:line-through; color:#9ca3af}
    .controls{display:flex; gap:6px}
    .small-btn{padding:6px 10px; border-radius:8px; border:none; cursor:pointer}
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="app-header">
        <h1 style="margin:0">📝 To‑Do</h1>
        <div style="opacity:0.9">A clean, colorful to‑do list built with Streamlit — local session persistence.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Sidebar controls
with st.sidebar:
    st.header("Add Task")
    new_task = st.text_input("Task title")
    new_desc = st.text_area("Description (optional)")
    priority = st.selectbox("Priority", ["Medium", "High", "Low"], index=0)
    due = st.date_input("Due date", value=date.today())
    add_col1, add_col2 = st.columns([3,1])
    with add_col1:
        add_btn = st.button("Add task")
    with add_col2:
        clear_btn = st.button("Clear")

    st.markdown("---")
    st.subheader("View")
    show_completed = st.checkbox("Show completed", value=True)
    sort_by = st.selectbox("Sort by", ["Added (newest)", "Due date (closest)", "Priority"], index=0)

# Add / clear logic
if add_btn:
    if new_task.strip() == "":
        st.sidebar.warning("Please enter a task title")
    else:
        task = {
            "id": str(uuid.uuid4()),
            "title": new_task.strip(),
            "desc": new_desc.strip(),
            "priority": priority,
            "due": due.isoformat() if isinstance(due, date) else str(due),
            "done": False,
        }
        st.session_state.tasks.insert(0, task)  # newest first
        st.sidebar.success("Task added")

if clear_btn:
    st.session_state.tasks = []
    st.sidebar.info("All tasks cleared")

# Filtering and sorting
tasks = st.session_state.tasks.copy()
if not show_completed:
    tasks = [t for t in tasks if not t["done"]]

if sort_by == "Due date (closest)":
    tasks.sort(key=lambda x: x.get("due", "9999-99-99"))
elif sort_by == "Priority":
    prio_map = {"High": 0, "Medium": 1, "Low": 2}
    tasks.sort(key=lambda x: prio_map.get(x.get("priority","Medium")))
# else keep as added (newest first)

# Main area: summary
col1, col2, col3 = st.columns(3)
col1.metric("Total", len(st.session_state.tasks))
col2.metric("Pending", len([t for t in st.session_state.tasks if not t["done"]]))
col3.metric("Completed", len([t for t in st.session_state.tasks if t["done"]]))

st.markdown("---")

# Function to render a single task card
def render_task(t):
    prio_class = "med"
    if t["priority"] == "High":
        prio_class = "high"
    elif t["priority"] == "Low":
        prio_class = "low"

    done_class = "done" if t["done"] else ""

    st.markdown(f"<div class=\"task-card\">", unsafe_allow_html=True)

    cols = st.columns([5,1,1])
    with cols[0]:
        st.markdown(f"<div class=\"task-title {done_class}\">{t['title']}</div>", unsafe_allow_html=True)
        if t.get("desc"):
            st.markdown(f"<div class=\"muted\">{t['desc']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class=\"muted\">Due: {t.get('due')} <span class=\"badge {prio_class}\">{t.get('priority')}</span></div>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("✔", key=f"done_{t['id']}"):
            # toggle
            for e in st.session_state.tasks:
                if e['id'] == t['id']:
                    e['done'] = not e['done']
                    break
            st.experimental_rerun()
    with cols[2]:
        if st.button("✏️", key=f"edit_{t['id']}"):
            st.session_state.editing = t['id']
            st.experimental_rerun()

    # Edit area
    if st.session_state.get('editing') == t['id']:
        with st.form(key=f"form_{t['id']}"):
            etitle = st.text_input("Title", value=t['title'])
            edesc = st.text_area("Description", value=t.get('desc',''))
            eprio = st.selectbox("Priority", ["High","Medium","Low"], index=["High","Medium","Low"].index(t['priority']))
            edue = st.date_input("Due date", value=date.fromisoformat(t['due']))
            sub1, sub2 = st.columns([1,1])
            with sub1:
                save = st.form_submit_button("Save")
            with sub2:
                delete = st.form_submit_button("Delete")
            if save:
                for e in st.session_state.tasks:
                    if e['id'] == t['id']:
                        e['title'] = etitle.strip()
                        e['desc'] = edesc.strip()
                        e['priority'] = eprio
                        e['due'] = edue.isoformat()
                        break
                st.session_state.pop('editing', None)
                st.experimental_rerun()
            if delete:
                st.session_state.tasks = [e for e in st.session_state.tasks if e['id'] != t['id']]
                st.session_state.pop('editing', None)
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Render all tasks
if len(tasks) == 0:
    st.info("No tasks yet — add one from the sidebar!")
else:
    for t in tasks:
        render_task(t)

# Footer: tips and download
st.markdown("---")
st.markdown("**Tips:** Click ✔ to toggle completion. Use the ✏️ button to edit or delete a task.")

# Download tasks as JSON
import json
if st.button("Export tasks (JSON)"):
    st.download_button(label="Download JSON", data=json.dumps(st.session_state.tasks, indent=2), file_name="tasks.json")

# Small attribution
st.markdown("<div style=\"opacity:0.6; font-size:12px; margin-top:8px\">Made By Bhaskar using Streamlit</div>", unsafe_allow_html=True)
