// 設定後端 API 的基礎網址 (因為你剛才改成了 5001)
const API_BASE_URL = 'http://127.0.0.1:5001/api';

// 1. 處理登入功能
async function handleLogin(event) {
    event.preventDefault(); // 防止表單重新整理頁面

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const role = document.querySelector('input[name="role"]:checked').value;

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, role })
        });

        const data = await response.json();

        if (response.ok) {
            alert('✅ ' + data.message);
            // 登入成功後跳轉頁面 (例如首頁)
            window.location.href = 'index.html'; 
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('連線錯誤:', error);
        alert('無法連線到伺服器，請確保後端 app.py 正在執行中。');
    }
}