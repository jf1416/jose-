import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import session, User, Comment, init_db

# Initialize database and seed with initial data if empty
init_db()

if not session.query(User).first():
    user1 = User(
        id="USR001",
        name="John Doe",
        email="john.doe@email.com",
        phone="+1-555-0123",
        status="active",
        created_at=datetime(2024, 1, 15, 9, 30, 0),
        last_activity=datetime(2024, 1, 20, 14, 22, 0)
    )
    user1.comments = [
        Comment(text="Initial contact made", timestamp=datetime(2024, 1, 15, 9, 35, 0), author="Admin"),
        Comment(text="Follow-up scheduled", timestamp=datetime(2024, 1, 18, 11, 0, 0), author="Sales Team")
    ]

    user2 = User(
        id="USR002",
        name="Jane Smith",
        email="jane.smith@email.com",
        phone="+1-555-0124",
        status="pending",
        created_at=datetime(2024, 1, 18, 16, 45, 0),
        last_activity=datetime(2024, 1, 19, 10, 15, 0)
    )
    user2.comments = [
        Comment(text="Awaiting documentation", timestamp=datetime(2024, 1, 18, 16, 50, 0), author="Support")
    ]

    session.add_all([user1, user2])
    session.commit()


def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class CRMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tracking CRM System")
        self.create_widgets()
        self.refresh_stats()
        self.refresh_table()

    def create_widgets(self):
        header = ttk.Frame(self.root)
        header.pack(fill='x')
        title = ttk.Label(header, text="Tracking CRM System", font=("Arial", 16, "bold"))
        title.pack(side='left', padx=10, pady=10)
        self.time_label = ttk.Label(header)
        self.time_label.pack(side='right', padx=10)
        self.update_time()

        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(action_frame, text="New Registration", command=self.open_new_user_window).pack(side='left')
        self.search_var = tk.StringVar()
        ttk.Entry(action_frame, textvariable=self.search_var, width=20).pack(side='left', padx=5)
        ttk.Button(action_frame, text="Query", command=self.search_user).pack(side='left')

        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(fill='x', padx=10, pady=5)
        self.total_label = ttk.Label(stats_frame, text="Total Users: 0")
        self.total_label.pack(side='left', padx=5)
        self.active_label = ttk.Label(stats_frame, text="Active Users: 0")
        self.active_label.pack(side='left', padx=5)
        self.pending_label = ttk.Label(stats_frame, text="Pending Users: 0")
        self.pending_label.pack(side='left', padx=5)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Email", "Status", "Created", "Last"), show='headings')
        for col in ("ID", "Name", "Email", "Status", "Created", "Last"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        self.tree.bind('<Double-1>', self.on_double_click)

    def update_time(self):
        self.time_label.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)

    def refresh_stats(self):
        users = session.query(User).all()
        total = len(users)
        active = len([u for u in users if u.status == 'active'])
        pending = len([u for u in users if u.status == 'pending'])
        self.total_label.config(text=f"Total Users: {total}")
        self.active_label.config(text=f"Active Users: {active}")
        self.pending_label.config(text=f"Pending Users: {pending}")

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for user in session.query(User).all():
            self.tree.insert('', 'end', iid=user.id, values=(
                user.id, user.name, user.email, user.status,
                format_time(user.created_at), format_time(user.last_activity)
            ))

    def open_new_user_window(self):
        win = tk.Toplevel(self.root)
        win.title("Register New User")
        ttk.Label(win, text="Full Name").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        name_var = tk.StringVar()
        ttk.Entry(win, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(win, text="Email").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        email_var = tk.StringVar()
        ttk.Entry(win, textvariable=email_var).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(win, text="Phone").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        phone_var = tk.StringVar()
        ttk.Entry(win, textvariable=phone_var).grid(row=2, column=1, padx=5, pady=5)

        def register():
            name = name_var.get().strip()
            email = email_var.get().strip()
            phone = phone_var.get().strip()
            if not name or not email:
                messagebox.showerror("Error", "Name and Email are required")
                return
            new_id = f"USR{session.query(User).count() + 1:03d}"
            now = datetime.now()
            user = User(
                id=new_id,
                name=name,
                email=email,
                phone=phone,
                status='pending',
                created_at=now,
                last_activity=now
            )
            user.comments = [Comment(text="User registered in system", timestamp=now, author="System")]
            session.add(user)
            session.commit()
            self.refresh_table()
            self.refresh_stats()
            win.destroy()

        ttk.Button(win, text="Register User", command=register).grid(row=3, column=0, columnspan=2, pady=10)

    def search_user(self):
        uid = self.search_var.get().strip()
        user = session.query(User).filter_by(id=uid).first()
        if user:
            self.open_user_details(user)
        else:
            messagebox.showinfo("Not found", "User not found")

    def on_double_click(self, event):
        item = self.tree.selection()
        if item:
            uid = item[0]
            user = session.query(User).get(uid)
            if user:
                self.open_user_details(user)

    def open_user_details(self, user):
        win = tk.Toplevel(self.root)
        win.title(f"User Details - {user.id}")
        info_frame = ttk.Frame(win)
        info_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(info_frame, text=f"Name: {user.name}").grid(row=0, column=0, sticky='w')
        ttk.Label(info_frame, text=f"Email: {user.email}").grid(row=0, column=1, sticky='w', padx=10)
        ttk.Label(info_frame, text=f"Phone: {user.phone}").grid(row=1, column=0, sticky='w')
        ttk.Label(info_frame, text=f"Status: {user.status}").grid(row=1, column=1, sticky='w', padx=10)
        ttk.Label(info_frame, text=f"Created: {format_time(user.created_at)}").grid(row=2, column=0, sticky='w')
        ttk.Label(info_frame, text=f"Last Activity: {format_time(user.last_activity)}").grid(row=2, column=1, sticky='w', padx=10)

        ttk.Label(win, text="Comments & Activity Log").pack(anchor='w', padx=10)
        comments_box = tk.Listbox(win, width=80)
        comments_box.pack(fill='both', expand=True, padx=10, pady=5)
        for c in user.comments:
            comments_box.insert('end', f"[{format_time(c.timestamp)}] {c.author}: {c.text}")

        comment_var = tk.StringVar()
        ttk.Entry(win, textvariable=comment_var, width=60).pack(side='left', padx=10, pady=10)

        def add_comment():
            text = comment_var.get().strip()
            if not text:
                return
            now = datetime.now()
            comment = Comment(user_id=user.id, text=text, timestamp=now, author="Current User")
            user.last_activity = now
            session.add(comment)
            session.commit()
            comments_box.insert('end', f"[{format_time(now)}] Current User: {text}")
            comment_var.set('')
            self.refresh_table()

        ttk.Button(win, text="Add Comment", command=add_comment).pack(side='left', pady=10)


if __name__ == '__main__':
    root = tk.Tk()
    app = CRMApp(root)
    root.mainloop()
