@echo off
call venv\Scripts\activate.bat
echo ==========================================
echo   基于微内核的自演进 RAN 原型
echo   Alpha 1.0
echo ==========================================
echo.
echo 正在启动系统...
echo 请稍候...
echo 如浏览器未自动打开，请手动访问: http://localhost:8501
echo.
echo 按 Ctrl+C 可停止服务
echo.
streamlit run uran/dashboard/research_app.py --server.port 8501
pause