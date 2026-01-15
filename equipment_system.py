import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime, timedelta, date
import streamlit.components.v1 as components

# --- 1. Page Configuration ---
st.set_page_config(page_title="Equipment Management System", layout="wide", page_icon="📸")

# --- 2. 50 Common Inventory Items (Pre-defined) ---
DEFAULT_ITEMS = [
    # Digital Cameras
    ("Canon EOS 5D Mark IV", "Digital Camera", 2), ("Sony Alpha 7 IV", "Digital Camera", 3),
    ("Fujifilm X-T5", "Digital Camera", 2), ("Nikon Z6 II", "Digital Camera", 2),
    ("Canon EOS R5", "Digital Camera", 1), ("Sony Alpha 7S III", "Digital Camera", 1),
    ("Panasonic Lumix GH6", "Digital Camera", 2), ("Blackmagic Pocket 4K", "Digital Camera", 2),
    ("Fujifilm X100V", "Digital Camera", 1), ("Ricoh GR IIIx", "Digital Camera", 1),
    ("Olympus OM-1", "Digital Camera", 1), ("Canon EOS 90D", "Digital Camera", 3),
    ("Nikon D850", "Digital Camera", 1), ("Hasselblad X2D", "Digital Camera", 1), ("Leica Q2", "Digital Camera", 1),
    # Film Cameras
    ("Canon AE-1 Program", "Film Camera", 4), ("Nikon FM2", "Film Camera", 4),
    ("Pentax K1000", "Film Camera", 3), ("Minolta X-700", "Film Camera", 3),
    ("Leica M6", "Film Camera", 1), ("Olympus OM-1 (Film)", "Film Camera", 2),
    ("Hasselblad 500C/M", "Film Camera", 1), ("Mamiya RZ67", "Film Camera", 1),
    ("Rolleiflex 2.8F", "Film Camera", 1), ("Yashica Mat-124G", "Film Camera", 2),
    ("Canon A-1", "Film Camera", 2), ("Nikon F3", "Film Camera", 2),
    ("Contax T2", "Film Camera", 1), ("Fujifilm GA645", "Film Camera", 1), ("Kodak Retina IIIC", "Film Camera", 1),
    # Tripods & Support
    ("Manfrotto MT055CXPRO4", "Tripod", 5), ("Manfrotto Befree Live", "Tripod", 3),
    ("Gitzo Systematic Series 3", "Tripod", 2), ("Benro Mach3", "Tripod", 4),
    ("Sachtler Ace XL (Fluid Head)", "Tripod", 2), ("DJI RS 3 Pro Gimbal", "Tripod", 2),
    ("Peak Design Travel Tripod", "Tripod", 1), ("Velbon Videomate 638", "Tripod", 3),
    ("Zhiyun Crane 3S", "Tripod", 1), ("iFootage Cobra Monopod", "Tripod", 2),
    # Projectors
    ("Epson EH-TW7000 4K", "Projector", 1), ("BenQ W1130", "Projector", 2),
    ("Sony VPL-VW290ES", "Projector", 1), ("XGIMI Horizon Pro", "Projector", 2),
    ("Panasonic PT-VMZ51 (Laser)", "Projector", 1), ("Optoma UHD35", "Projector", 1),
    ("Epson CO-FH02 Portable", "Projector", 3), ("NEC P525UL", "Projector", 1),
    ("JVC DLA-NP5", "Projector", 1), ("Dangbei Mars Pro", "Projector", 1)
]

# --- 3. Database Initialization (Auto-Import Logic) ---
def init_db():
    conn = sqlite3.connect('equipment.db')
    c = conn.cursor()
    
    # Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  category TEXT,
                  total_qty INTEGER,
                  in_stock_qty INTEGER)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_name TEXT,
                  contact_info TEXT,
                  item_name TEXT,
                  action TEXT,
                  borrow_time TEXT,
                  duration_days INTEGER,
                  expected_return TEXT,
                  status TEXT)''')
    
    # --- AUTO IMPORT CHECK ---
    # Check if the inventory is empty
    c.execute("SELECT count(*) FROM items")
    count = c.fetchone()[0]
    
    if count == 0:
        # If empty, automatically insert the 50 default items
        print("Database empty. Auto-importing default items...")
        for item in DEFAULT_ITEMS:
            c.execute("INSERT INTO items (name, category, total_qty, in_stock_qty) VALUES (?, ?, ?, ?)",
                      (item[0], item[1], item[2], item[2]))
        conn.commit()
    
    conn.commit()
    conn.close()

def run_query(query, params=(), fetch=False):
    conn = sqlite3.connect('equipment.db')
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        data = c.fetchall()
        conn.close()
        return data
    conn.commit()
    conn.close()

# --- 4. Helper: Digital Clock ---
def show_digital_clock():
    clock_html = """
    <div style="font-family: 'Helvetica Neue', sans-serif; font-size: 24px; font-weight: bold; color: #333; background: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #d6d6d6;">
        🕒 <span id="clock"></span>
    </div>
    <script>
    function updateTime() {
        var now = new Date();
        var timeString = now.toLocaleTimeString('en-US', { hour12: false });
        document.getElementById('clock').innerHTML = timeString;
    }
    setInterval(updateTime, 1000);
    updateTime();
    </script>
    """
    components.html(clock_html, height=80)

# Initialize System (This runs on every load)
init_db()

# --- 5. Sidebar Navigation ---
with st.sidebar:
    st.title("🎬 Equipment Center")
    show_digital_clock()
    st.write("---")
    
    menu = ["Borrow Equipment", "Return Equipment", "Inventory Management", "Logs & Notifications"]
    choice = st.radio("Menu", menu)
    
    st.write("---")
    st.info("📅 **Policy:** Maximum loan duration is 7 days.")

# --- Function 1: Borrow Equipment ---
if choice == "Borrow Equipment":
    st.subheader("📝 Borrow Equipment")
    
    with st.container(border=True):
        items = run_query("SELECT name, in_stock_qty FROM items WHERE in_stock_qty > 0", fetch=True)
        item_options = {f"{i[0]} (Available: {i[1]})": i[0] for i in items}
        
        with st.form("borrow_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("Student Name / ID")
                contact_info = st.text_input("Email / Phone Number")
            
            with col2:
                selected_label = st.selectbox("Select Item", list(item_options.keys()) if item_options else ["Out of Stock"])
                
                # Calendar Input
                today = datetime.now().date()
                max_due_date = today + timedelta(days=7)
                
                return_date = st.date_input(
                    "📅 Expected Return Date (Max 7 days)",
                    value=today + timedelta(days=1),
                    min_value=today,
                    max_value=max_due_date,
                    help="Click to select a date."
                )
                
                duration_days = (return_date - today).days
                if duration_days < 1: duration_days = 1
                st.caption(f"📊 Duration: **{duration_days}** days")

            submitted = st.form_submit_button("Confirm Checkout", type="primary")
            
            if submitted and student_name and item_options:
                real_item_name = item_options[selected_label]
                current_time = datetime.now()
                expected_return_dt = datetime.combine(return_date, current_time.time())
                
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                return_str = expected_return_dt.strftime("%Y-%m-%d %H:%M:%S")

                run_query("INSERT INTO logs (student_name, contact_info, item_name, action, borrow_time, duration_days, expected_return, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (student_name, contact_info, real_item_name, "Borrowed", time_str, duration_days, return_str, "active"))
                
                run_query("UPDATE items SET in_stock_qty = in_stock_qty - 1 WHERE name = ?", (real_item_name,))
                
                st.success(f"✅ Success! Please return by {return_date}.")
                time.sleep(1.5)
                st.rerun()

# --- Function 2: Return Equipment ---
elif choice == "Return Equipment":
    st.subheader("↩️ Return Equipment")
    
    with st.container(border=True):
        active_loans = run_query("SELECT id, student_name, item_name, borrow_time FROM logs WHERE status = 'active'", fetch=True)
        
        if not active_loans:
            st.info("✅ All items are accounted for. No pending returns.")
        else:
            loan_dict = {f"{row[1]} - {row[2]} (Borrowed: {row[3]})": row[0] for row in active_loans}
            selected_return = st.selectbox("Select Loan Record", list(loan_dict.keys()))
            
            if st.button("Confirm Return", type="primary"):
                log_id = loan_dict[selected_return]
                record = run_query("SELECT item_name FROM logs WHERE id = ?", (log_id,), fetch=True)[0]
                item_name = record[0]
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                run_query("UPDATE logs SET status = 'returned', action = 'Returned (Date: ' || ? || ')' WHERE id = ?", (current_time, log_id))
                run_query("UPDATE items SET in_stock_qty = in_stock_qty + 1 WHERE name = ?", (item_name,))
                
                st.balloons()
                st.success("✅ Item returned successfully!")
                time.sleep(1.5)
                st.rerun()

# --- Function 3: Inventory Management ---
elif choice == "Inventory Management":
    st.subheader("📦 Inventory Management")
    
    # (Auto-import is now handled in init_db, so we removed the manual button)

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Current Inventory")
            data = run_query("SELECT name, category, in_stock_qty, total_qty FROM items", fetch=True)
            if data:
                df = pd.DataFrame(data, columns=["Item Name", "Category", "In Stock", "Total Qty"])
                st.dataframe(df, use_container_width=True, height=500)
            else:
                st.info("Inventory is empty.")
            
        with col2:
            st.markdown("#### Add New Item")
            with st.form("add_item_form"):
                new_name = st.text_input("Item Name")
                new_category = st.selectbox("Category", ["Digital Camera", "Film Camera", "Lens", "Lighting", "Tripod", "Projector", "Audio", "Others"])
                new_qty = st.number_input("Total Quantity", min_value=1, value=1)
                
                if st.form_submit_button("Add to Inventory"):
                    run_query("INSERT INTO items (name, category, total_qty, in_stock_qty) VALUES (?, ?, ?, ?)",
                              (new_name, new_category, new_qty, new_qty))
                    st.success(f"Added: {new_name}")
                    st.rerun()

# --- Function 4: Logs & Notifications ---
elif choice == "Logs & Notifications":
    st.subheader("📨 Logs & Notifications")
    
    with st.container(border=True):
        st.markdown("#### 🔴 Overdue / Due Soon")
        
        data = run_query("SELECT student_name, contact_info, item_name, expected_return, duration_days FROM logs WHERE status = 'active'", fetch=True)
        
        if data:
            df = pd.DataFrame(data, columns=["Student", "Contact", "Item", "Due Date", "Days"])
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df['Status'] = df['Due Date'].apply(lambda x: "⚠️ OVERDUE" if x < now_str else "Normal")
            
            st.dataframe(df, use_container_width=True)
            
            st.write("---")
            st.markdown("#### 📧 Send Reminder Email")
            
            student_to_notify = st.selectbox("Select Student to Notify", df['Student'] + " (" + df['Contact'] + ")")
            
            if st.button("Generate Email Draft"):
                selected_name = student_to_notify.split(" (")[0]
                selected_row = df[df['Student'] == selected_name].iloc[0]
                
                email = selected_row['Contact']
                item = selected_row['Item']
                due_date = selected_row['Due Date']
                
                subject = f"Equipment Return Reminder: {item}"
                body = f"Hi {selected_name},\n\nThis is a friendly reminder that the equipment you borrowed ({item}) is due for return by {due_date}.\n\nPlease return it to the Equipment Center as soon as possible.\n\nThank you!"
                
                mailto_link = f"mailto:{email}?subject={subject}&body={body}"
                
                st.code(body, language='text')
                st.markdown(f"👉 [Click here to open Email Client]({mailto_link})", unsafe_allow_html=True)
        else:
            st.success("No active loans at the moment.")
            
    with st.expander("View Full History Log"):
        all_logs = run_query("SELECT * FROM logs ORDER BY id DESC", fetch=True)
        st.dataframe(pd.DataFrame(all_logs, columns=["ID", "Student", "Contact", "Item", "Action", "Time", "Duration", "Expected Return", "Status"]))
