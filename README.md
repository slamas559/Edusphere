# 📚 PDF Archive & Digital Marketplace

A sleek, modern Django-powered web application that allows users to:

- Upload and explore academic PDF resources
- Search and filter blog posts and products
- Browse a community-driven digital marketplace
- Connect and share educational content

---

## 🚀 Features

### 🧠 Educational Archive
- Upload PDFs with automatic cover thumbnail generation
- Extract PDF metadata: author, page count
- Search PDFs by title or uploader
- View details and download resources

### 🛍️ Marketplace
- List and sell educational materials
- Sort products by category
- Search products by title or description
- Responsive design with image preview

### 📝 Blogging System
- Create and manage blog posts with images
- Like and comment on posts
- Real-time like updates via AJAX
- Search posts by title or content

---

## 🛠️ Tech Stack

- **Backend**: Django, Django ORM, Python
- **Frontend**: Tailwind CSS, HTML, JavaScript
- **Database**: SQLite (can be switched to PostgreSQL)
- **Media Processing**: `PyPDF2`, `pdf2image`, `Pillow`
- **Auth**: Django's built-in User model

---

## 📂 Folder Structure

saas_company/
├── archive/ # PDF archive app
├── market/ # Marketplace app
├── blog/ # Blog system
├── dashboard/ # UI dashboard and layout
├── media/ # Uploaded media files
├── templates/ # Global HTML templates
├── static/ # Static files (CSS, JS)
└── manage.py # Django CLI

---

## 🔍 Search & Filters

- Blog: `?q=term`
- Marketplace: `?q=phone&category=books`
- PDFs: `?q=machine learning`

---

## 🔧 Setup Instructions

1. **Clone this repo**

```bash
git clone https://github.com/slamas559/Edusphere.git
```

### Create virtual envioronment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

---

### Install Dependencies
pip install -r requirements.txt

---

### Run migrations
python manage.py makemigrations
python manage.py migrate

---

### Run the server
python manage.py runserver

---

### ✨ Credits
  Thumbnails: pdf2image, Pillow
  Metadata: PyPDF2
  Icons: Font Awesome
  Styling: TailwindCSS

---

### 📃 License
This project is open-source under the MIT License.

---

### 🤝 Contribute
Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

---

### 🔗 Connect with Me
GitHub: @slamas559
LinkedIn: www.linkedin.com/in/salam-abdulsalam-5a0b08278

