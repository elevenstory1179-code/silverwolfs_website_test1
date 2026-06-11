import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# 設定圖片上傳路徑
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 模擬資料庫（實際生產環境建議換成 SQLite 或 PostgreSQL）
trouble_tickets = [
    {
        "id": 1,
        "title": "第一層不黏床、翹曲",
        "solution": "將熱床溫度調高 5 度，並使用口紅膠增加附著力。",
        "image": "sample_warping.jpg"
    }
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 路由 1：主頁面 ---
@app.route('/')
def index():
    return render_template('index.html', tickets=trouble_tickets)

# --- 功能 1：上傳問題與圖片 ---
@app.route('/api/upload_issue', methods=['POST'])
def upload_issue():
    title = request.form.get('title')
    solution = request.form.get('solution')
    file = request.files.get('image')
    
    filename = 'default.jpg'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    new_ticket = {
        "id": len(trouble_tickets) + 1,
        "title": title,
        "solution": solution,
        "image": filename
    }
    trouble_tickets.append(new_ticket)
    return redirect(url_for('index'))

# --- 功能 2 & 3：爬取後處理與耗材資訊 ---
@app.route('/api/crawl_data', methods=['GET'])
def crawl_data():
    # 這裡演示爬蟲概念，實際爬取時需替換成目標網站的 URL 與 Selectors
    # 為了防止被目標網站 Banner，通常會加上 Headers
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # 模擬爬取的耗材與後處理數據
    materials = [
        {"name": "PLA", "feature": "好列印、低收縮、不耐熱", "price": "NTD 450 - 800"},
        {"name": "PETG", "feature": "耐候性佳、有韌性、易拉絲", "price": "NTD 600 - 1100"},
        {"name": "ABS", "feature": "高強度、耐熱、收縮率大需封箱", "price": "NTD 550 - 950"}
    ]
    post_process_info = [
        {"title": "PLA 砂紙打磨技巧", "link": "#", "desc": "從 240 目打磨到 1000 目，配合水磨效果更佳。"},
        {"title": "ABS 丙酮燻蒸法", "link": "#", "desc": "利用丙酮蒸氣溶解表面，達到鏡面效果，需注意通風。"}
    ]
    
    return jsonify({
        "materials": materials,
        "post_process": post_process_info
    })

# --- 功能 4：參數計算器 ---
@app.route('/api/calculate_params', methods=['POST'])
def calculate_params():
    data = request.json
    env_temp = float(data.get('env_temp', 25))
    env_humidity = float(data.get('env_humidity', 50))
    material_type = data.get('material_type', 'PLA')
    
    # 基礎參數矩陣
    base_params = {
        'PLA': {'nozzle': 200, 'bed': 60, 'speed': 60},
        'PETG': {'nozzle': 240, 'bed': 80, 'speed': 45},
        'ABS': {'nozzle': 250, 'bed': 100, 'speed': 50}
    }
    
    params = base_params.get(material_type, {'nozzle': 200, 'bed': 60, 'speed': 50}).copy()
    
    # 銀狼特製：環境補償密碼演算法
    # 濕度過高時，稍微拉高噴嘴溫度以利排濕，並降低速度確保層間黏合
    if env_humidity > 65:
        params['nozzle'] += 5
        params['speed'] -= 5
    
    # 環境溫度過低時，稍微提高熱床溫度防止翹曲
    if env_temp < 18:
        params['bed'] += 5
        
    return jsonify(params)

if __name__ == '__main__':
    app.run(debug=True, port=5000)