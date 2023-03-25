from flask import Flask, render_template, jsonify, request
import pymysql

# 資料庫連線
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Tt-143085',
    database='kkbox',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)

# 取得 cursor 物件，進行 CRUD
cursor = connection.cursor()

# 建立 Flask 物件
app = Flask(__name__)

''' 樣版 '''
# 套用網頁樣版
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

''' Web API '''
# 取得 youtube 所有列表
@app.route('/kkbox', methods=['GET'])
def getKKBOXList():
    # 預設回傳訊息
    dictResponse = {"success": False, "info": "查詢失敗"}
    
    try:
        # 查詢資料  資料會存在cursor本身
        sql = "select charts.id,boards.title, charts.song_name, charts.song_url from `charts` join `boards` on boards.id = charts.board_id"
        cursor.execute(sql)

        # 查詢結果列數大於0 ，代表有資料
        if cursor.rowcount > 0:
            # 將查詢結果轉成 list 型態 (list 裡頭元素都是 dict)
            results = cursor.fetchall()
            
            # 新增屬性 results，將查詢結果送回前端頁面
            dictResponse["success"] = True
            dictResponse["info"] = "查詢成功"
            dictResponse["results"] = results
        else:
            dictResponse["info"] = "查詢結果為空"

        # 提交 SQL 執行結果
        connection.commit()

    except Exception as e:
        # 取消transaction
        connection.rollback()
        dictResponse["info"] = f"SQL 執行失敗: {e}"

    # 回傳結果
    return jsonify(dictResponse)

# 搜尋特定文字
@app.route("/kkbox/title", methods = ["POST"])
def getKKBOXData():
    # 回傳訊息
    dictResponse = {"success": False, "info": "搜尋失敗"}
    
    try:
        # 取得搜尋字串
        title = request.json['title']

        # 處理成 SQL 看得懂的格式
        title = "%" + title.replace(" ", "%") + "%" #空格會變成%

        # 查詢資料
        sql = "SELECT * FROM `charts` WHERE `song_name` LIKE %s"
        cursor.execute(sql, {title})

        # 查詢結果列數大於0 ，代表有資料
        if cursor.rowcount > 0:
            # 將查詢結果轉成 list 型態 (list 裡頭元素都是 dict)
            results = cursor.fetchall()
            
            # 新增屬性 results，將查詢結果送回前端頁面
            dictResponse["success"] = True
            dictResponse["info"] = "搜尋成功"
            dictResponse["results"] = results
        else:
            dictResponse["info"] = "查詢結果為空"

        # 提交 SQL 執行結果
        connection.commit()
    except Exception as e:
        #  取消交易
        connection.rollback()
        dictResponse["info"] = f"SQL 執行失敗: {e}"

    # 回傳結果
    return jsonify(dictResponse)

    

# 刪除或更新指定 kkbox id 的資料
@app.route("/kkbox/<id>", methods=["DELETE", "POST"])
def setKKBOXData(id):
    # 回傳訊息
    dictResponse = {"success": False, "info": "系統異常"}

    try:
        if request.method == 'DELETE':
            # 預設刪除用的回傳訊息
            dictResponse["info"] = "刪除失敗"
            
            # 刪除資料
            sql = "DELETE FROM `charts` WHERE `id` = %s"
            cursor.execute(sql, (id)) # 用()tuple {}set 都可以

            # 刪除結果列數大於0 ，代表有成功刪除資料
            if cursor.rowcount > 0:
                dictResponse["success"] = True
                dictResponse["info"] = "刪除成功"
        
        elif request.method == 'POST':
            # 預設更新用的回傳訊息
            dictResponse["info"] = "更新失敗"

             # 更新資料
            sql = "UPDATE `charts` SET `song_name` = %s WHERE `id` = %s"
            cursor.execute(sql, (request.json['song_name'], id))

            # 更新結果列數大於0 ，代表有更新資料
            if cursor.rowcount > 0:
                dictResponse["success"] = True
                dictResponse["info"] = "更新成功"

        # 提交 SQL 執行結果
        connection.commit()
    except Exception as e:
        # 取消交易
        connection.rollback()
        dictResponse["info"] = f"SQL 執行失敗: {e}"

    # 回傳結果
    return jsonify(dictResponse)


# 主程式區域 0.0.0.0表對外服務
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)