
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
  ```

### 2️⃣ Steps to Run the Bot
1. Clone this repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Create a `database.json` file to store sales, inventory, and expenses:
   ```json
   {
       "savdolar": [],
       "ombor": {},
       "xarajatlar": []
   }
   ```

3. Update the **bot token** in the code:
   ```python
   app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
   ```

4. Run the bot locally:
   ```bash
   python bot.py
   ```

5. Access the bot via Telegram and start using commands.

---

## 🖼 Visual Styling and Stickers

To make the bot interactive and fun:
- **Emoji Integration**: Commands and responses include emojis to improve readability.
- **Stickers**: Use Telegram stickers to acknowledge user actions or errors (e.g., 👍, ❌, 🎉). You can include stickers using Telegram’s `send_sticker` method in responses.

Example:
```python
await update.message.reply_sticker(sticker="CAACAgIAAxkBAAEB1Jlk9Xo7K0X5...")
```

---

## 🔒 Security

- Admin password is required for system access.
- Replace the default password (`ADMIN_PASSWORD`) in the code with a secure password:
   ```python
   ADMIN_PASSWORD = "YourSecurePassword"
   ```

---

## 📁 File Structure

| File/Directory       | Description                                      |
|-----------------------|--------------------------------------------------|
| `bot.py`             | Main script containing the bot's logic.          |
| `database.json`      | Persistent storage for sales, inventory, expenses. |
| `oylik_hisobot.pdf`  | Monthly sales and expense report in PDF format.  |

---

## 🌟 Future Improvements
- Add **multi-language support** for commands and responses.
- Integrate **AI-powered analytics** for sales trends.
- Expand report generation with graphs and charts.

---

## 📄 License
This project is open-source and available under the **MIT License**.

---

Start managing your inventory with ease! 🛍️📊
