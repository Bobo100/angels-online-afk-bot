# GameProject-Angel(angels-online-afk-bot)

天使之戀 Online 的掛機輔助工具(Python + tkinter 介面)。用 OpenCV / aircv 比對畫面截圖、pyautogui 操作滑鼠鍵盤，另外用一個小的 Keras 模型(`my_model.h5`)辨識畫面上的座標數字。

![image](https://user-images.githubusercontent.com/33471758/215333883-0451bf83-e5da-420b-b396-8e0be1abe048.png)

## 功能

- **自動開遊戲登入**:依帳號群組一次開多個視窗並登入(帳號資料在介面上輸入後存到本機的 `data.json`,已被 gitignore)
- **自動領獎勵**:立即領取，或每 10 分鐘自動領一次
- **自動導航**:讀取目前座標，走到指定的目標座標
- 列出目前開著的天使之戀視窗

## 執行

需要 Windows 與 Python 3.11(TensorFlow 2.13 的支援範圍)。

```bash
pip install -r requirements.txt
python Game.py
```

`start_game.json` 設定遊戲執行檔路徑;`image/` 是比對用的截圖，換解析度或遊戲改版時可能要重新截。

打包成 exe:

```bash
pyinstaller Game.py
```

## 注意

用程式自動操作線上遊戲可能違反遊戲的使用條款。2022 年的舊版歷史另外保存在 private repo `gameproject-angel-legacy`。
