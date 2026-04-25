body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f7fb;
}

.sidebar {
    width: 250px;
    height: 100vh;
    background: #1e1b4b;
    color: white;
    position: fixed;
    padding: 20px;
    overflow-y: auto;
}

.sidebar h2 {
    margin-bottom: 20px;
}

.menu-title {
    margin-top: 15px;
    margin-bottom: 8px;
    font-size: 14px;
    color: #a5b4fc;
}

.sidebar a {
    display: block;
    color: white;
    text-decoration: none;
    padding: 10px;
    margin-bottom: 5px;
    border-radius: 8px;
}

.sidebar a:hover {
    background: #312e81;
}

.main {
    margin-left: 270px;
    padding: 20px;
}

.cards {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.card {
    flex: 1;
    min-width: 180px;
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    color: white;
    padding: 20px;
    border-radius: 15px;
}
