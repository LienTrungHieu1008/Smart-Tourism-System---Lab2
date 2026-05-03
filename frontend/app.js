const API_BASE_URL = "http://127.0.0.1:8000";

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBfw67yZRd66wa8i4Pf54CfR6cJ25fEKYY",
    authDomain: "smarttourism-api.firebaseapp.com",
    projectId: "smarttourism-api",
    storageBucket: "smarttourism-api.firebasestorage.app",
    messagingSenderId: "181735767446",
    appId: "1:181735767446:web:5c9c6df147e089303531b7",
    measurementId: "G-78BT07SC3B"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const provider = new GoogleAuthProvider();

const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const userInfo = document.getElementById('userInfo');
const userName = document.getElementById('userName');
const userAvatar = document.getElementById('userAvatar');
const searchBtn = document.getElementById('searchBtn');
const searchInput = document.getElementById('searchInput');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const errorDiv = document.getElementById('error');
const historySection = document.getElementById('historySection');
const historyList = document.getElementById('historyList');

let currentIdToken = null;

onAuthStateChanged(auth, async (user) => {
    if (user) {
        loginBtn.classList.add('hidden');
        userInfo.classList.remove('hidden');
        userName.textContent = user.displayName;
        userAvatar.src = user.photoURL;
        currentIdToken = await user.getIdToken();
        fetchHistory(currentIdToken);
    } else {
        loginBtn.classList.remove('hidden');
        userInfo.classList.add('hidden');
        currentIdToken = null;
        historySection.classList.add('hidden');
    }
});

loginBtn.addEventListener('click', () => {
    signInWithPopup(auth, provider).catch(error => {
        showError("Lỗi đăng nhập: " + error.message);
    });
});

logoutBtn.addEventListener('click', () => {
    signOut(auth);
});

searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    loadingDiv.classList.remove('hidden');
    resultsDiv.innerHTML = '';
    errorDiv.classList.add('hidden');

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (currentIdToken) {
            headers['Authorization'] = `Bearer ${currentIdToken}`;
        }

        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ query: query, top_k: 5 })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Lỗi từ máy chủ');
        }

        const data = await response.json();
        renderResults(data);

        if (currentIdToken) {
            setTimeout(() => fetchHistory(currentIdToken), 1500);
        }

    } catch (error) {
        showError(error.message);
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

function renderResults(results) {
    if (results.length === 0) {
        showError("Không tìm thấy địa điểm nào phù hợp.");
        return;
    }

    results.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'result-card';
        div.style.animationDelay = `${index * 0.1}s`;
        div.innerHTML = `
            <div class="card-header">
                <div class="card-title">${item.name}</div>
                <div class="card-score">Độ phù hợp: ${Math.round(item.score * 100)}%</div>
            </div>
            <div class="card-desc">${item.description}</div>
        `;
        resultsDiv.appendChild(div);
    });
}

async function fetchHistory(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/history`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) return;

        const data = await response.json();
        const history = data.history;

        if (history && history.length > 0) {
            historySection.classList.remove('hidden');
            historyList.innerHTML = '';
            history.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.query}`;
                li.addEventListener('click', () => {
                    searchInput.value = item.query;
                    performSearch();
                });
                historyList.appendChild(li);
            });
        }
    } catch (error) {
        console.error("Lỗi lấy lịch sử:", error);
    }
}

function showError(msg) {
    errorDiv.textContent = msg;
    errorDiv.classList.remove('hidden');
}
