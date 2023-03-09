import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Ma'lumotlar bazasini yaratish
conn = sqlite3.connect('books.db')
cursor = conn.cursor()

# "books" jadvalini yaratish
cursor.execute('''
    CREATE TABLE IF NOT EXISTS books
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     name TEXT,
     genre TEXT,
     author TEXT,
     price INTEGER)
''')

# Bazaga ma'lumot qo'shish
data = [
    {"name": "Robinzon Kruzo", "genre": "Tragedia", "author": "Daniel Defo", "price": 45}
]

for item in data:
    cursor.execute('''
        INSERT INTO books (name, genre, author, price)
        VALUES (?, ?, ?, ?)
    ''', (item['name'], item['genre'], item['author'], item['price']))

conn.commit()

class Books(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/books':
            cursor.execute('SELECT * FROM books')
            books = cursor.fetchall()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(books).encode())
        elif self.path.startswith('/books/'):
            # Biron bir kitobni olish
            book_id = int(self.path.split('/')[-1])
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = cursor.fetchone()
            if book:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(book).encode())
            else:
                self.send_error(404)
        else:
            self.send_error(404)
            
    def do_POST(self):
        if self.path == '/books':
            # Bazaga yangi kitob qo'shish
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_item = json.loads(post_data.decode())
            cursor.execute('''
                INSERT INTO books (name, genre, author, price)
                VALUES (?, ?, ?, ?)
            ''', (new_item['name'], new_item['genre'], new_item['author'], new_item['price']))
            conn.commit()
            new_item['id'] = cursor.lastrowid
            self.send_response(201)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Location', '/books/{}'.format(new_item['id']))
            self.end_headers()
            self.wfile.write(json.dumps(new_item).encode())
        else:
            self.send_error(404)        

    def do_PUT(self):
        if self.path.startswith('/books/'):
            book_id = int(self.path.split('/')[-1])
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = cursor.fetchone()
            if not book:
                self.send_error(404, 'Kitob topilmadi')
                return
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            new_item = json.loads(put_data.decode())
            cursor.execute('''
                UPDATE books SET name = ?, genre = ?, author = ?, price = ? WHERE id = ?
            ''', (new_item['name'], new_item['genre'], new_item['author'], new_item['price'], book_id))
            conn.commit()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            new_item['id'] = book_id
            self.wfile.write(json.dumps(new_item).encode())
        else:
            self.send_error(404)
            
    def do_DELETE(self):
        if self.path.startswith('/books/'):
            book_id = int(self.path.split('/')[-1])
            cursor.execute('SELECT * FROM books WHERE id = ?', (book_id,))
            book = cursor.fetchone()
            if not book:
                self.send_error(404, 'Kitob topilmadi')
                return
            cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            conn.commit()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(book).encode())
        else:
            self.send_error(404, 'Noto\'g\'ri so\'rov')


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, Books)
    print("Server Ishladi")
    httpd.serve_forever()