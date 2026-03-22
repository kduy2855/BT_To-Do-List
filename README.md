# To-Do API

REST API quản lý công việc với FastAPI, SQLModel, JWT authentication và Alembic migration.

## Tính năng

- Đăng ký, đăng nhập, lấy thông tin người dùng hiện tại
- CRUD todo
- Lọc theo trạng thái hoàn thành
- Tìm kiếm theo từ khóa
- Danh sách việc hôm nay và quá hạn
- Gắn tag và hạn hoàn thành
- Test API bằng `pytest` + `TestClient`

## Công nghệ

- FastAPI
- SQLModel
- Alembic
- SQLite mặc định, hỗ trợ PostgreSQL qua biến môi trường
- Pytest
- Docker / Docker Compose

## Chạy local

### 1. Tạo môi trường ảo

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Cài dependencies

```powershell
pip install -r requirements.txt
```

### 3. Chạy migrate

```powershell
alembic upgrade head
```

### 4. Chạy server

```powershell
uvicorn main:app --reload
```

API mặc định chạy tại `http://127.0.0.1:8000` và tài liệu Swagger ở `http://127.0.0.1:8000/docs`.

## Biến môi trường

Ứng dụng đọc biến môi trường từ file `.env`.

Ví dụ:

```env
APP_NAME=To-Do API
DEBUG=true
VERSION=1.0.0
API_PREFIX=/api/v1
DATABASE_URL=sqlite:///./todo.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Nếu muốn dùng PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/todo_app
```

## Chạy test

```powershell
pytest
```

Các test hiện có:

- Tạo todo thành công
- Validation fail khi dữ liệu không hợp lệ
- Trả về `404` khi không tìm thấy todo
- Trả về `401` khi gọi endpoint cần auth nhưng không có token

## Chạy với Docker

### Chỉ chạy API

```powershell
docker build -t todo-api .
docker run -p 8000:8000 todo-api
```

### Chạy API + PostgreSQL bằng Docker Compose

```powershell
docker compose up --build
```

Compose sẽ:

- chạy PostgreSQL ở cổng `5432`
- chạy migrate bằng `alembic upgrade head`
- khởi động API ở `http://127.0.0.1:8000`

## Cấu trúc test

- `tests/conftest.py`: cấu hình database test và `TestClient`
- `tests/test_todos.py`: các test cho luồng todo
