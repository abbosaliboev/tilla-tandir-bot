# Telegram Inventory Management Bot 📦🤖

**This bot simplifies inventory, sales, and expense management by integrating features like user authentication, PDF reporting, and real-time tracking.** 

---

## ✨ Features
- 🛒 **Inventory Management**:
  - 📥 Add items to inventory.
  - 📤 Remove items from inventory.
  - 🗂 View inventory status.
- 💸 **Sales Management**:
  - Record and track sales.
  - Generate daily and monthly reports.
- 🛠️ **Expense Tracking**:
  - Add expenses with user details.
  - Monitor daily and monthly expenses.
- 🗂️ **PDF Report Generation**:
  - Automatically generate and share **monthly reports** in PDF format. 📝
- 🔒 **Secure Access**:
  - Only authorized users can access bot features through an **admin password**.
- 🤝 **User Management**:
  - View, add, or remove authorized users.
  - Clear the entire user list in one command.

---

## 📚 Bot Commands

### 👤 General Commands
| Command                          | Description                          |
|----------------------------------|--------------------------------------|
| `/start`                         | Start the bot and view commands.     |
| `/yakuniy_savdo [product] [quantity] [price]` | Record a sale.               |
| `/ombor`                         | View all items in the inventory.     |
| `/qabul [product] [quantity]`    | Add products to the inventory.       |
| `/chiqarish [product] [quantity]`| Remove products from the inventory.  |
| `/kunlik_hisobot`                | View daily sales and expense report. |
| `/oylik_hisobot`                 | Generate and share monthly PDF report. |
| `/xarajat [product] [price]`     | Record an expense.                   |

### 🔧 Admin Commands
| Command                          | Description                          |
|----------------------------------|--------------------------------------|
| `/foydalanuvchilar`              | View the list of authorized users.   |
| `/foydalanuvchilarni_tozalash`   | Remove all authorized users.         |
| `/foydalanuvchini_ochirish [user_id]` | Remove a user by ID.           |

---

## 🚀 Deployment Information

This bot was deployed on the **Railway** platform. Railway offers free server hosting for lightweight applications and is ideal for this bot. You can also deploy on similar platforms like **Render** or **Heroku** (free plans available).

### 🔧 Steps to Deploy
1. Sign up for a hosting platform (e.g., Railway or Render).
2. Connect your repository to the platform.
3. Ensure the bot token and database file are properly configured.
4. Deploy and monitor using the hosting platform's dashboard.

---

## 🛠 Setup and Installation

### 1️⃣ Prerequisites
- **Python 3.x** installed.
- Required libraries installed:
  ```bash
  pip install fpdf python-telegram-bot
